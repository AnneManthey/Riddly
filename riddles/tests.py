from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CalendarSettings, Door, UserDoorProgress


class SharedCalendarTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='first',
            password='test-password',
        )
        self.other_user = user_model.objects.create_user(
            username='second',
            password='test-password',
        )
        self.door = Door.objects.create(
            number=1,
            title='First riddle',
            riddle='What is the answer?',
            question='Answer:',
            solution='yes',
            loot='A prize',
            slug='first-riddle',
        )
        self.calendar_settings, _ = CalendarSettings.objects.get_or_create(
            pk=1,
            defaults={'date_restrictions_enabled': False},
        )

    def test_users_share_door_content_but_not_progress(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('riddle', kwargs={'slug': self.door.slug}),
            {'answer': 'yes'},
        )
        self.assertRedirects(
            response,
            reverse('riddle', kwargs={'slug': self.door.slug}),
        )

        first_progress = UserDoorProgress.objects.get(user=self.user, door=self.door)
        self.assertTrue(first_progress.solved)
        self.assertEqual(first_progress.attempts, 1)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, self.door.loot)
        self.assertNotContains(response, self.door.title)

        self.client.force_login(self.other_user)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, self.door.title)
        self.assertNotContains(response, self.door.loot)
        other_progress = UserDoorProgress.objects.get(
            user=self.other_user,
            door=self.door,
        )
        self.assertFalse(other_progress.solved)
        self.assertEqual(other_progress.attempts, 0)

    def test_wrong_answer_attempt_is_private_to_user(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse('riddle', kwargs={'slug': self.door.slug}),
            {'answer': 'no'},
        )

        self.assertEqual(
            UserDoorProgress.objects.get(user=self.user, door=self.door).attempts,
            1,
        )
        self.assertFalse(
            UserDoorProgress.objects.filter(user=self.other_user, door=self.door).exists()
        )

    def test_new_shared_doors_receive_unique_slugs(self):
        second_door = Door.objects.create(
            number=2,
            title=self.door.title,
            riddle='Another question?',
            question='Answer:',
            solution='yes',
            loot='Another prize',
        )

        self.assertEqual(second_door.slug, 'first-riddle-2')

    def test_date_restrictions_unlock_doors_by_number_and_relock_unsolved_doors(self):
        self.calendar_settings.date_restrictions_enabled = True
        self.calendar_settings.save()
        second_door = Door.objects.create(
            number=2,
            title='Second riddle',
            riddle='Another question?',
            question='Answer:',
            solution='yes',
            loot='Another prize',
            slug='second-riddle',
        )
        self.client.force_login(self.user)

        with patch('riddles.views.timezone.localdate', return_value=date(2025, 12, 1)):
            response = self.client.get(
                reverse('riddle', kwargs={'slug': self.door.slug}),
            )
        self.assertRedirects(response, reverse('dashboard'))

        with patch('riddles.views.timezone.localdate', return_value=date(2026, 11, 30)):
            response = self.client.get(
                reverse('riddle', kwargs={'slug': self.door.slug}),
                follow=True,
            )
        self.assertEqual(response.redirect_chain, [(reverse('dashboard'), 302)])
        self.assertContains(response, 'Diese Tür ist noch gesperrt.')

        with patch('riddles.views.timezone.localdate', return_value=date(2026, 12, 1)):
            response = self.client.get(
                reverse('riddle', kwargs={'slug': self.door.slug}),
            )
        self.assertEqual(response.status_code, 200)

        with patch('riddles.views.timezone.localdate', return_value=date(2026, 12, 1)):
            response = self.client.get(
                reverse('riddle', kwargs={'slug': second_door.slug}),
            )
        self.assertRedirects(response, reverse('dashboard'))

        with patch('riddles.views.timezone.localdate', return_value=date(2027, 1, 1)):
            response = self.client.get(
                reverse('riddle', kwargs={'slug': self.door.slug}),
            )
        self.assertRedirects(response, reverse('dashboard'))

        progress = UserDoorProgress.objects.get(user=self.user, door=second_door)
        progress.solved = True
        progress.save()
        with patch('riddles.views.timezone.localdate', return_value=date(2027, 1, 1)):
            response = self.client.get(
                reverse('riddle', kwargs={'slug': second_door.slug}),
            )
        self.assertEqual(response.status_code, 200)

    def test_locked_doors_remain_visible_but_disabled(self):
        self.calendar_settings.date_restrictions_enabled = True
        self.calendar_settings.save()
        self.client.force_login(self.user)

        with patch('riddles.views.timezone.localdate', return_value=date(2026, 11, 30)):
            response = self.client.get(reverse('dashboard'))

        self.assertContains(response, 'class="single-door door-locked"')
        self.assertContains(response, 'aria-disabled="true"')
        self.assertContains(response, 'Gesperrt')

    def test_disabled_date_restrictions_leave_door_open(self):
        self.calendar_settings.date_restrictions_enabled = False
        self.calendar_settings.save()
        self.client.force_login(self.user)

        with patch('riddles.views.timezone.localdate', return_value=date(2026, 1, 1)):
            response = self.client.get(
                reverse('riddle', kwargs={'slug': self.door.slug}),
            )

        self.assertEqual(response.status_code, 200)
