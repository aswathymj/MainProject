# Generated by Django 5.0.6 on 2024-09-04 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_termsandconditions'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='expected_rate',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
