# Generated by Django 5.0.6 on 2024-08-30 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_servicerequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonesubcategory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='subcategory_images/'),
        ),
    ]
