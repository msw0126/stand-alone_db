from django.db import models

# Create your models here.
class AtomLearn(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    input_comp_id = models.CharField(max_length=100)
    # feature_id = models.CharField(max_length=100)
    # feature_target = models.CharField(max_length=100)
    algorithm = models.CharField(max_length=30)
    # ncores = models.CharField(max_length=10)

    class Meta:
        # managed = True
        db_table = 'atom_learn'

class AtomLearnParam(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    param_name = models.CharField(max_length=30)
    param_value = models.CharField(max_length=1000)

    class Meta:
        # managed = True
        db_table = 'atom_learn_param'