from django.db import models

# Create your models here.

class Test(models.Model):
    
    script = models.CharField(max_length=1000)
    name = models.CharField(max_length=200)

    # Comma separated list of Test Suites that reference this Test. 
    usedByTestSuites = models.CharField(max_length=1000)
   

