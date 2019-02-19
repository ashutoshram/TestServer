from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from eos.models import Test
from eos.forms import TestForm 


# Create your views here.


def home(request):
    tests = get_all_tests()
    return render(request, 'home.html', {'tests' : tests})

def get_all_tests():
    tests = Test.objects.all().values()
    return tests


def test_upload(request):

    if request.method == "POST":

        form = TestForm(request.POST, request.FILES)
        if form.is_valid():
            test, created = Test.objects.get_or_create(**form.cleaned_data) 
            if created: 
                test.save()
                name = form.cleaned_data['name']
                script = form.cleaned_data['script']
                parse_and_store(name, script)
                return render(request, 'test_response.html', {'name' : name, 'script' : script, 'error' : 'You success, you!'})
            else: 
                print("This Test has already been created, please try a new script.")
                return render(request, 'test_response.html', {'error' : 'Yo! Check your script and try again homie!' })
        


        return redirect('/eos/success/')

    else:

        form = TestForm()

        print('test_upload: returning form for user completion')
        return render(request, 'test_upload.html', {'form': form})

def upload_success(request):
    return HttpResponse("You successfully uploaded a test!")

def parse_and_store(name, script):
   script_name = settings.MEDIA_ROOT.strip('/') + settings.MEDIA_URL + name + '.py'
   script_out =  open(script_name, "x")   
   script_out.write(script)

   
