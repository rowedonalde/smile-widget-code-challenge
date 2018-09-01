# Generated by Django 2.0.7 on 2018-09-01 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(help_text='Value in cents')),
                ('date_start', models.DateField()),
                ('date_end', models.DateField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='giftcard',
            name='amount',
            field=models.PositiveIntegerField(help_text='Value in cents'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.PositiveIntegerField(help_text='Price of product in cents if no ProductPrice in date range'),
        ),
        migrations.AddField(
            model_name='productprice',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product'),
        ),
    ]
