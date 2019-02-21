from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse

from eos.models import Test
from eos.forms import TestForm 

import importlib



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

            script = form.cleaned_data['script']
            name = form.cleaned_data['name']

            test = form.save(commit=False)
            test.name = name 
            test.script = script 

            test.save()

            #return render(request, 'test_response.html', {'tests': tests})
            return redirect('/eos')

        else:

            print("This Test has already been created, please try a new script.")
            return render(request, 'test_response.html', {'error' : 'Yo! Check your script and try again homie!' })
        
    else:

        form = TestForm()

        print('test_upload: returning form for user completion')
        return render(request, 'test_upload.html', {'form': form})

def upload_success(request):
    return HttpResponse("You successfully uploaded a test!")

def get_arguments(request, test_id):

    #use AccessID to grab correct Test Object
    test_to_run = Test.objects.get(accessID=test_id)

    #prepare script name for module import
    test_module = ((str(test_to_run.script)).strip('.py').replace('/','.'))

    #importing module to current python environment
    d = importlib.import_module(test_module)

    #request the Test Object for argument list to display to user
    arguments = d.Test.get_args()

    #attach arguments as template variables to html page
    return render(request, 'choose_parameters.html', {'arguments': arguments, 'uuid_hidden': test_id})


def edit_test(request, test_id):
    print(request)
    print(test_id)
    return HttpResponse(test_id)


def run_test(request):
    if request == "POST":
        # Run test with parameters
        # UUID and form will be sent here via request
        # Hide UUID --> <-- 


































