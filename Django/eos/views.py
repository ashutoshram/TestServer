from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse

import eos.scripts.AbstractTestClass as ATC

from eos.models import Test
from eos.models import TestSuite
from eos.forms import TestForm 

import importlib
import inspect
import json
import threading
import uuid



# Create your views here.


def home(request):
    tests = get_all_Tests()
    suites = get_all_TestSuites()
    return render(request, 'home.html', {'tests' : tests, 'suites': suites})

def get_all_Tests():
    tests = Test.objects.all().values()
    return tests

def get_all_TestSuites():
    TestSuites = TestSuite.objects.all().values()
    return TestSuites

def test_upload(request):

    if request.method == "POST":

        form = TestForm(request.POST, request.FILES)

        if form.is_valid(): 

            script = form.cleaned_data['script']
            name = form.cleaned_data['name']

            #FIXME if test has the same name, replace test

            #test, created = Test.objects.get_or_create(name)

            #if not created:
            test = form.save(commit=False)
            test.name = name 
            test.script = script 
            test.status = False


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

def create_suite(request):

    if request.method == "POST":

        # this is after the user has chosen the tests he wants to include in the test suite
        # q = request.POST q = getlist('value')

        q = request.POST
        tests = q.getlist('tests')
        name = q.get('TestSuiteName')
        suite = TestSuite()
        suite.TestList = json.dumps(tests)
        suite.name = name
        suite.save()

        return redirect('/eos')


    else:

        tests = get_all_Tests()

        return render(request, 'suites.html', {'tests': tests}) 

    

def load_test(test_id):
    #use AccessID to grab correct Test Object
    test_to_run = Test.objects.get(accessID=test_id)

    #prepare script name for module import
    test_module = ((str(test_to_run.script)).strip('.py').replace('/','.'))

    # return all ATC classes in the module
    try:
        #importing module to current python environment
        module = importlib.import_module(test_module)
        atc_classes = []
        for member in dir(module):
            handler_class = getattr(module, member)
            if handler_class and inspect.isclass(handler_class):
                if issubclass(handler_class, ATC.AbstractTestClass):
                    atc_classes.append(handler_class)
                    print(atc_classes)
        return atc_classes
    except:
        return []


runningTests = {} # a dictionary of tid to test instance

def threaded_test(test, args):
    t = threading.Thread(target=test.run, args=(test, args))
    t.start()


def progress(request):
    # lookup test instance from runningTests given tid
    tid = request.META['QUERY_STRING']
    try:
        test = runningTests[tid]
        percent = test.progress(test)
        print("progress on test with tid %s: %d" % (tid, percent))
    except:
        print("no running test with tid %s" % tid)
        percent = 0
    if percent == 100:
        print("removing test with tid %s from runningTests" % tid)
        del runningTests[tid]
    data = {'progress': percent}
    return JsonResponse(data)

    # call progress on the test instance
    # return a JsonResponse

def run_test(request, test_id):

    if request.method == "POST":
        q = request.POST

        args = q.getlist('value')
        testID = q.get('uuid')

        test = load_test(test_id)
        if not test:
            return HttpResponse("Invalid script")
        if len(test) > 1:
            return HttpResponse("Too many ATCs in the script")

        test = test[0] # create an instance of the first atc test


        # start a thread running the test
        threaded_test(test, args)
        tid = uuid.uuid4()
        tid = str(tid)
        # cache the running instance of the test in the global runningTests dict
        runningTests[tid] = test
        # return the tid as a JsonResponse

        print(tid)

        return TemplateResponse(request, 'choose_parameters.html', {'arguments': args,'threadid': tid})

        
        """
        print("Running Test Script now")
        return_code = test.run(test,args)

        print(return_code)
        return HttpResponse(json.dumps(return_code))
        """

    else:
        test = load_test(test_id)
        if not test:
            return HttpResponse("Invalid script")

        if len(test) > 1:
            return HttpResponse("Too many ATCs in the script")

        test = test[0] # create an instance of the first atc test

        #request the Test Object for argument list to display to user
        arguments = test.get_args(test)

        #attach arguments as template variables to html page
        return render(request, 'choose_parameters.html', {'arguments': arguments, 'uuid_hidden': test_id})


def edit_test(request, test_id):
    print(request)
    print(test_id)
    return HttpResponse(test_id)



































