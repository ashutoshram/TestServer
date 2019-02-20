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

            #script = request.FILES['script']
            script = form.cleaned_data['script']
            name = form.cleaned_data['name']

            test = form.save(commit=False)
            test.name = name 
            test.script = script 

            test.save()

            tests = Test.objects.all().values()

            return render(request, 'home.html', {'tests': tests})

        else:

            print("This Test has already been created, please try a new script.")
            return render(request, 'test_response.html', {'error' : 'Yo! Check your script and try again homie!' })
        



    else:

        form = TestForm()

        print('test_upload: returning form for user completion')
        return render(request, 'test_upload.html', {'form': form})

def upload_success(request):
    return HttpResponse("You successfully uploaded a test!")

def run_test(request, test_id):
    print(request)
    print(test_id)

def edit_test(request, test_id):
    print(request)
    print(test_id)
