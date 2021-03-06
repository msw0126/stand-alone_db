# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-01-22 16:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=10)),
                ('component_id', models.CharField(max_length=100)),
                ('container_id', models.CharField(max_length=100)),
                ('table_name', models.CharField(max_length=50)),
                ('key_fields', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'container',
            },
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=10)),
                ('component_id', models.CharField(max_length=100)),
                ('source', models.CharField(max_length=20)),
                ('source_table_name', models.CharField(max_length=50)),
                ('target', models.CharField(max_length=20)),
                ('target_table_name', models.CharField(max_length=50)),
                ('rel_type', models.CharField(max_length=8)),
                ('sc_join', models.CharField(max_length=200)),
                ('tg_join', models.CharField(max_length=200)),
                ('interval', models.CharField(max_length=100, null=True)),
            ],
            options={
                'db_table': 'relation',
            },
        ),
    ]
