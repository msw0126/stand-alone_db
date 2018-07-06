from django.db import models

# Create your models here.

class Container(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    container_id = models.CharField(max_length=100)
    table_name = models.CharField(max_length=50)
    key_fields = models.CharField(max_length=200)

    class Meta:
        # managed = True
        db_table = 'container'


class Relation(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    source = models.CharField(max_length=20)
    source_table_name = models.CharField(max_length=50)
    target = models.CharField(max_length=20)
    target_table_name = models.CharField(max_length=50)
    rel_type = models.CharField(max_length=8)
    sc_join = models.CharField(max_length=200)
    tg_join = models.CharField(max_length=200)
    interval = models.CharField(max_length=100, null=True)

    class Meta:
        # managed = True
        db_table = 'relation'