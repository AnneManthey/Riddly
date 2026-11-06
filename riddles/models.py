from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.utils.text import slugify



class Door(models.Model):
    """A door with riddle in the advent calendar app."""
    number = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(24)])
    image = models.ImageField(upload_to='img/', blank=True )
    title = models.CharField(max_length=100)
    riddle = models.TextField()
    question = models.CharField(max_length=100, default="Antwort:")
    solution = models.CharField(max_length=100)
    loot = models.CharField(max_length=50)
    css = models.CharField(max_length=50, blank=True)
    js = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)

    class Meta:
        ordering = ['number']
        constraints = [
            models.UniqueConstraint(
                fields=['number'],
                name='unique_shared_door_number'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or f'door-{self.number}'
            slug = base_slug[:100]
            suffix = 2
            while Door.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                suffix_text = f'-{suffix}'
                slug = f'{base_slug[:100 - len(suffix_text)]}{suffix_text}'
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the title and door number."""
        return f"{self.title} (Door number {self.number})"


class UserDoorProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='door_progress',
    )
    door = models.ForeignKey(
        Door,
        on_delete=models.CASCADE,
        related_name='user_progress',
    )
    solved = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    solved_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        ordering = ['door__number']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'door'],
                name='unique_user_door_progress',
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.door}"


class CalendarSettings(models.Model):
    date_restrictions_enabled = models.BooleanField(
        default=False,
        verbose_name='Datumssperre aktivieren',
    )

    class Meta:
        verbose_name = 'Kalendereinstellung'
        verbose_name_plural = 'Kalendereinstellungen'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Kalenderzugang'

    
