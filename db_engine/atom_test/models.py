from django.db import models

# Create your models here.
class AtomTest(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    atom_act_id = models.CharField(max_length=100)
    input_comp_id = models.CharField(max_length=100)
    feature_id = models.CharField(max_length=100)
    feature_target = models.CharField(max_length=100)
    # max_value = models.IntegerField()
    class Meta:
    #     # managed = True
        db_table = 'atom_test'