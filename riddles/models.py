from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings



class Door(models.Model):
    """A door with riddle in the advent calendar app."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    number = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(24)])
    image = models.ImageField(upload_to='img/', blank=True )
    title = models.CharField(max_length=100)
    riddle = models.TextField()
    solution = models.CharField(max_length=100)
    loot = models.CharField(max_length=50)
    solved = models.BooleanField(default=False)
    solved_at = models.DateTimeField(null = True, blank=True, default= None )
    css = models.CharField(max_length=50, blank=True)
    js = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True) 

    class Meta:
        ordering = ['number']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'number'],
                name='unique_door_per_user'
            )
        ]
    def __str__(self):
        """Return title, door number and related user."""
        return f"{self.title} (Door number {self.number}, User {self.user})"

    
