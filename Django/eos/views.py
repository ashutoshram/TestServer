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
import traceback



# Create your views here.

#BASIC VIEWS

def home(request):
    tests = get_all_Tests()
    #checkIfTestExists(tests)
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
        testIDs = []
        tests = q.getlist('tests')
        print("the tests you chose: %s" % tests)
        for test in tests:
            testID = str(Test.objects.get(name=test).accessID)
            testIDs.append(testID)
        name = q.get('TestSuiteName')
        print("this is the name you chose: %s" % name)

        IDlist = ','.join([ID for ID in testIDs])
        suite = TestSuite()
        suite.TestList = (IDlist)
        suite.name = name
        suite.save()
        return redirect('/eos')




    #FIXME IF TEST IS DELETED REMOVE ENTRY FROM TestList

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
        traceback.print_exc()
        return []


running_tests = {} # a dictionary of tid to test instance
running_suites = {} # a dictionary of tid to suite instance
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
                storage_path = test.get_storage_path()
                # save report to Database and grab from database when needed
                # Report(create with tid)
                status = check_status(report)
                R = Report.objects.create(name=name, report=report, accessID=tid, status=status, storage=storage_path)
                R.save()
                del running_tests[tid]
                break
        for tid in list(running_suites):
            suite = running_suites[tid]
            if suite.is_done():
                del running_suites[tid]
                break
        time.sleep(1)

def check_status(report):
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
        try:
            suite = running_suites[tid]
            percent = suite.get_progress()
            print("progress on suite with tid %s: %d" % (tid, percent))
        except:
            percent = 200
    if percent == 100:
        print("test/suite %s is done" % tid)
    data = {'progress': percent, 'report_id': tid}
    return JsonResponse(data)

    # call progress on the test instance
    # return a JsonResponse

def run_suite(request, suite_id):
    
    if request.method == "POST":
        # after user has selected their parameters
        q = request.POST
        s = Suite(suite_id, q)

        # report each test and gather all reports into one suite report
        # save as suite-report and display on home page --> get_all_suite_reports()
        
        tid = s.get_tid()
        running_suites[tid] = s
        return TemplateResponse(request, 'choose_suite_params.html', {'threadid': tid })
    
    else:
        # show all tests within the Test Suite
        t_params = {}
        names = []
        suite = TestSuite.objects.get(accessID=suite_id)
        t = suite.TestList
        t = t.split(',')
        for testID in t:
            test = load_test(testID)
            for t in test:
                t_arguments = t().get_args()
                t_name = t().get_name()
                t_params[t_name] = t_arguments


        # allow user to choose parameters for each of the tests
        # user will +apply their preferences and then run the suite
        # send back data through request as a POST which will be handled above and run each test
        return render(request, 'choose_suite_params.html', {'args_dict': t_params, 'suite': suite})

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
        tid = uuid.uuid4()
        tid = str(tid)
        name = test.get_name()
        storage_path = name + '_' + str(tid)
        test.set_default_storage_path(storage_path)
        threaded_test(test, args)
        # cache the running instance of the test in the global running_tests dict
        running_tests[tid] = test
        # return the tid as a JsonResponse
        
        if monitoring_thread is None:
            start_monitoring_thread()

        print(tid)


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
    test = Test.objects.get(accessID=test_id)    
    return render(request, 'edit_test.html', {'test': test})


def edit_suite(request, suite_id):
    suite = TestSuite.objects.get(accessID=suite_id)
    return render(request, 'edit_suite.html', {'suite': suite})

def report(request, report_id):
    report = Report.objects.get(accessID=report_id)
    # This is where a report.html will be implemented and show the report in a clean and concise manner. 
    return HttpResponse(report.report)

def delete_test(request, test_id):
    test = Test.objects.get(accessID=test_id)    
    test.delete()
    return redirect('home')

def delete_suite(request, suite_id):
    suite = TestSuite.objects.get(accessID=suite_id)
    suite.delete()
    return redirect('home')

#CLASSES

class Suite():
    def __init__(self, suite_id, q):
        self.suite_id = suite_id
        self.q = q
        self.run()

    def run(self):
        self.tid = uuid.uuid4()
        self.tid = str(self.tid)
        self.current_test = 0
        self.num_tests = 1
        self.done = False
        self.t = threading.Thread(target=self._run, args=(self.tid,))
        self.t.start()
    
    def get_tid(self):
        return self.tid

    def get_progress(self):
        return int(self.current_test * 100/self.num_tests)

    def is_done(self):
        return self.done


    def _run(self, tid):
        try:
            suite = TestSuite.objects.get(accessID=self.suite_id)
            s_name = suite.name
            t = suite.TestList
            t = t.split(',')
            # run each test using the respective list of parameters
            tidlist = []
            self.num_tests = len(t)
            self.current_test = 0
            self.suite_report = []
            for testID in t:
                test = load_test(testID)
                test = test[0]()
                name = test.get_name()
                args = self.q.getlist(name)
                test.run(args)
                report = test.generate_report()
                status = check_status(report)
                self.suite_report.append(report)
                self.current_test += 1
            R = Report.objects.create(name=s_name, report=self.suite_report, accessID=tid, status=status, isSuiteReport=True)
            R.save()
        except:
            print('Suite %s caught exception' % self.suite_id)
            traceback.print_exc()
        self.done = True

