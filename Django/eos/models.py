from django.db import models
import uuid

# Create your models here.

class Test(models.Model):
    
    script = models.FileField(upload_to='eos/scripts/')
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200, default="No description.")

    # Comma separated list of Test Suites that reference this Test. 
    usedByTestSuites = models.CharField(max_length=1000)
    accessID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class TestSuite(models.Model):
    name = models.CharField(max_length=200, default="SuiteName")
    accessID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    TestList = models.TextField(null=True)


class Report(models.Model):
    #the report that is saved to this model is a string of a dictionary. 
    #example = " {'YUYV' : 'Success', 'MJPG': 'Fail (20 fps)'} "
    status = models.BooleanField()
    name = models.CharField(max_length=200, default="TestName")
    accessID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report = models.TextField(null=True) 
    isSuiteReport = models.BooleanField(default=False)

