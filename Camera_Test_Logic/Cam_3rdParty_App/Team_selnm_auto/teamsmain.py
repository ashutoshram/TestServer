import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import xpaths
import pyautogui as mous
import xp
calt=input("Please enter the call type:")
itr=input("please enter the iteration for Teams call:")
p_name=input("please enter the Participant name:")
global j
import tmethods1

login= tmethods1.login()

for i in range(0,int(itr)):
    j=i+1
    call= tmethods1.call(j, calt.upper(), p_name)
    print(call)
if itr == str(j) :
    print('call complete with '+ itr + ' iteration')
    tmethods1.logout()
else:
    print('iteration fails '+ str(j) + ' times')


