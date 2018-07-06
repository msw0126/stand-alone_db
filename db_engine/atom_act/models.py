from django.db import models

# Create your models here.

class AtomAct(models.Model):
    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    atom_learn_id = models.CharField(max_length=100)
    input_comp_id = models.CharField(max_length=100)
    reason_code_nvars = models.IntegerField()
    ncores = models.IntegerField()
    class Meta:
    #     # managed = True
        db_table = 'atom_act'
