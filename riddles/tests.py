from datetime import date
import json
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from PIL import Image

from .middleware import REMEMBER_ME_SESSION_AGE
from .models import CalendarSettings, Door, DoorImage, UserDoorProgress


class PwaTests(SimpleTestCase):
    def test_login_page_links_to_manifest(self):
        response = self.client.get(reverse('login'))

        self.assertContains(response, 'rel="manifest" href="/static/manifest.webmanifest"')

    def test_login_page_has_checked_remember_me_option(self):
        response = self.client.get(reverse('login'))

        self.assertContains(
            response,
            '<input type="checkbox" name="remember_me" checked />',
        )

    def test_manifest_and_icons(self):
        manifest_path = finders.find('manifest.webmanifest')
        self.assertIsNotNone(manifest_path)
        manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))

        self.assertEqual(manifest['name'], 'Riddly')
        self.assertEqual(manifest['start_url'], reverse('dashboard'))
        self.assertEqual(manifest['scope'], '/')
        self.assertEqual(manifest['display'], 'standalone')
        self.assertEqual(
            {icon['sizes'] for icon in manifest['icons']},
            {'192x192', '512x512'},
        )
        for icon in manifest['icons']:
            with self.subTest(icon=icon['src']):
                self.assertEqual(icon['type'], 'image/png')
                icon_path = finders.find(icon['src'])
                self.assertIsNotNone(icon_path)
                with Image.open(icon_path) as image:
                    self.assertEqual(image.format, 'PNG')
                    self.assertEqual(
                        image.size,
                        tuple(int(size) for size in icon['sizes'].split('x')),
                    )

    def test_dashboard_redirects_unauthenticated_users_to_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")


class RememberMeLoginTests(TestCase):
    def test_failed_login_preserves_checked_remember_me_option(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'invalid', 'password': 'invalid', 'remember_me': 'on'},
        )

        self.assertContains(
            response,
            '<input type="checkbox" name="remember_me" checked />',
        )

    def test_failed_login_preserves_unchecked_remember_me_option(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'invalid', 'password': 'invalid'},
        )

        self.assertContains(
            response,
            '<input type="checkbox" name="remember_me" />',
        )


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

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.user.username, 'password': 'test-password'},
            follow=True,
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(response.context['user'].is_authenticated)

    def test_authenticated_user_is_redirected_from_login_to_dashboard(self):
        self.client.force_login(self.user)

        for method in ('get', 'post'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(reverse('login'))

                self.assertRedirects(response, reverse('dashboard'))

    def test_login_without_remember_me_uses_browser_session(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.user.username, 'password': 'test-password'},
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_remember_me_uses_30_day_sliding_session(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': self.user.username,
                'password': 'test-password',
                'remember_me': 'on',
            },
        )

        self.assertRedirects(response, reverse('dashboard'))
        session = self.client.session
        self.assertFalse(session.get_expire_at_browser_close())
        self.assertAlmostEqual(
            session.get_expiry_age(),
            REMEMBER_ME_SESSION_AGE,
            delta=2,
        )

        session.set_expiry(REMEMBER_ME_SESSION_AGE - 86400)
        session.save()
        response = self.client.get(reverse('login'))
        self.assertEqual(
            response.cookies['sessionid']['max-age'],
            REMEMBER_ME_SESSION_AGE,
        )

    def test_logout_ends_the_current_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
        )

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

    def test_riddle_page_shows_optional_link(self):
        self.client.force_login(self.user)
        url = 'https://example.com/more'
        self.door.link = url
        self.door.save()

        response = self.client.get(reverse('riddle', kwargs={'slug': self.door.slug}))

        self.assertContains(
            response,
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">Zum Nonogram</a>',
        )

        self.door.link = ''
        self.door.save()
        response = self.client.get(reverse('riddle', kwargs={'slug': self.door.slug}))

        self.assertNotContains(response, url)

    def test_riddle_page_shows_door_images_in_creation_order(self):
        self.client.force_login(self.user)
        DoorImage.objects.create(door=self.door, image='img/first.png')
        DoorImage.objects.create(door=self.door, image='img/second.png')

        response = self.client.get(reverse('riddle', kwargs={'slug': self.door.slug}))
        content = response.content.decode()

        first_image = '/media/img/first.png'
        second_image = '/media/img/second.png'
        self.assertContains(response, first_image)
        self.assertContains(response, second_image)
        self.assertLess(content.index(first_image), content.index(second_image))

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
