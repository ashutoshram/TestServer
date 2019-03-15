from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse

import eos.scripts.AbstractTestClass as ATC

from eos.models import Test, TestSuite, Report
from eos.forms import TestForm 

import importlib
import inspect
import json
import threading
import uuid
import time



# Create your views here.

#BASIC VIEWS

def home(request):
    tests = get_all_Tests()
    suites = get_all_TestSuites()
    reports = get_all_Reports()
    return render(request, 'home.html', {'tests' : tests, 'suites': suites, 'reports': reports})

def get_all_Tests():
    tests = Test.objects.all().values()
    return tests

def get_all_TestSuites():
    TestSuites = TestSuite.objects.all().values()
    return TestSuites

def get_all_Reports():
    reports = Report.objects.all().values()
    return reports

def upload_success(request):
    return HttpResponse("You successfully uploaded a test!")

#UPLOAD AND CREATION VIEWS


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

    

# TEST VIEWS

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


running_tests = {} # a dictionary of tid to test instance
monitoring_thread = None

def start_monitoring_thread():
    monitoring_thread = threading.Thread(target=monitor_test, args=())
    monitoring_thread.start()

def threaded_test(test, args):
    t = threading.Thread(target=test.run, args=(args,))
    t.start()


def monitor_test():
    while True:
        # run through all the tests in running_tests 
        for tid in list(running_tests):
            test = running_tests[tid]
            # wait for it to complete and delete the entry once it is done
            if test.is_done():
                # update the report for the test once it is done
                name = test.get_name()
                report = test.generate_report()
                # save report to Database and grab from database when needed
                # Report(create with tid)
                status = check_status(report)
                R = Report.objects.create(name=name, report=report, accessID=tid, status=status)
                R.save()
                del running_tests[tid]
                break
        time.sleep(1)

def check_status(report):
    #rpt = json.loads(report)
    return all(v==0 for v in report.values())
    

def progress(request):
    # lookup test instance from running_tests given tid
    tid = request.META['QUERY_STRING']
    try:
        test = running_tests[tid]
        percent = test.get_progress()
        print("progress on test with tid %s: %d" % (tid, percent))
    except:
        print("no running test with tid %s" % tid)
        percent = 200
    if percent == 100:
        print("test %s is done" % tid)
    data = {'progress': percent, 'report_id': tid}
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

        test = test[0]() # create an instance of the first atc test


        # start a thread running the test
        threaded_test(test, args)
        tid = uuid.uuid4()
        tid = str(tid)
        # cache the running instance of the test in the global running_tests dict
        running_tests[tid] = test
        # return the tid as a JsonResponse
        
        if monitoring_thread is None:
            start_monitoring_thread()

        print(tid)

        name = test.get_name()

        return TemplateResponse(request, 'choose_parameters.html', {'arguments': args,'threadid': tid, 'test_name' : name})

    else:
        test = load_test(test_id)
        if not test:
            return HttpResponse("Invalid script")

        if len(test) > 1:
            return HttpResponse("Too many ATCs in the script")

        test = test[0]() # create an instance of the first atc test

        #request the Test Object for argument list to display to user
        arguments = test.get_args()
        name = test.get_name()

        #attach arguments as template variables to html page
        return render(request, 'choose_parameters.html', {'arguments': arguments, 'uuid_hidden': test_id, 'test_name': name})


def edit_test(request, test_id):
    print(request)
    print(test_id)
    return HttpResponse(test_id)

def report(request, report_id):
    report = Report.objects.get(accessID=report_id)
    # This is where a report.html will be implemented and show the report in a clean and concise manner. 
    return HttpResponse(report.report)



































