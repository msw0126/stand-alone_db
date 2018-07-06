# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class CsvReaderInfo(models.Model):
    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=50)
    file_name = models.CharField(max_length=100)
    magic_name = models.CharField(max_length=30)

    class Meta:
        # managed = True
        db_table = 'csv_reader_info'


class CsvReaderInfotype(models.Model):
    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=50)
    field = models.CharField(max_length=100)
    field_type = models.CharField(max_length=10)
    date_format = models.CharField(max_length=20, blank=True, null=True)
    sample_data = models.CharField(max_length=1000)
    selected = models.BooleanField(default=True)

    class Meta:
        # managed = True
        db_table = 'csv_reader_infotype'
