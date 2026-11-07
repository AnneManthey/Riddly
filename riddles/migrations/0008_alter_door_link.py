from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('riddles', '0007_door_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='door',
            name='link',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
