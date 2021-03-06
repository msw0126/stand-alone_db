# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-01-15 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AtomLearn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=10)),
                ('component_id', models.CharField(max_length=100)),
                ('input_comp_id', models.CharField(max_length=100)),
                ('algorithm', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'atom_learn',
            },
        ),
        migrations.CreateModel(
            name='AtomLearnParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=10)),
                ('component_id', models.CharField(max_length=100)),
                ('param_name', models.CharField(max_length=30)),
                ('param_value', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'atom_learn_param',
            },
        ),
    ]
