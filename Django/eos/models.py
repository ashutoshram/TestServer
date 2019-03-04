from django.db import models
from django.core.files.storage import FileSystemStorage
import uuid

# Create your models here.

fs = FileSystemStorage()

class Test(models.Model):
    
    script = models.FileField(upload_to='eos/scripts/')
    name = models.CharField(max_length=200)

    # Comma separated list of Test Suites that reference this Test. 
    usedByTestSuites = models.CharField(max_length=1000)
    accessID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class TestSuite(models.Model):
    name = CharField(max_length=200)
    tests = ListCharField(
            base_field=CharField(max_length=10)
            size=10
            max_length=(10 * 11)
        )
   

