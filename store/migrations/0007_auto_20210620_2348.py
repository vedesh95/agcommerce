# Generated by Django 3.2.3 on 2021-06-20 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_remove_shippingaddress_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='desc',
            field=models.TextField(null=True),
        ),
        migrations.DeleteModel(
            name='ShippingAddress',
        ),
    ]