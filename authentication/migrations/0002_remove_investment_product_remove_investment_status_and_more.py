# Generated by Django 5.0.3 on 2024-03-24 16:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investment',
            name='product',
        ),
        migrations.RemoveField(
            model_name='investment',
            name='status',
        ),
        migrations.AddField(
            model_name='investment',
            name='amount_invested',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='investment',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 24, 16, 47, 42, 182128, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='investment',
            name='product_name',
            field=models.CharField(default=datetime.datetime(2024, 3, 24, 16, 47, 59, 128245, tzinfo=datetime.timezone.utc), max_length=100),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Product',
        ),
    ]
