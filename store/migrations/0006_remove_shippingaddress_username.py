# Generated by Django 3.2.3 on 2021-06-19 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_rename_taxation_id_order_transaction_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingaddress',
            name='username',
        ),
    ]