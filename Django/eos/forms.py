from django import forms
from eos.models import Test


class TestForm(forms.ModelForm):
    
    class Meta:
        model = Test
        fields = ['name', 'script']
