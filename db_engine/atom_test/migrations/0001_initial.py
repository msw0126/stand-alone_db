# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-01-15 18:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AtomTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=10)),
                ('component_id', models.CharField(max_length=100)),
                ('atom_act_id', models.CharField(max_length=100)),
                ('input_comp_id', models.CharField(max_length=100)),
                ('feature_id', models.CharField(max_length=100)),
                ('feature_target', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'atom_test',
            },
        ),
    ]