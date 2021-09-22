import unittest
from HtmlTestRunner import HTMLTestRunner
from test_pyt_src import Test_Pytcam
import os
import pytest

dir = "C:/Users/Rahul/PycharmProjects/pythonProject/reports"
camera_pyt = unittest.TestLoader().loadTestsFromTestCase(Test_Pytcam)
test_suite = unittest.TestSuite([camera_pyt,])
outfile = open(dir + "/PythonTestSummary.html", "w")
runner = HTMLTestRunner(output=dir, stream=outfile, report_title='Test Report', report_name='Acceptance Tests',open_in_browser=True)
runner.run(test_suite)
