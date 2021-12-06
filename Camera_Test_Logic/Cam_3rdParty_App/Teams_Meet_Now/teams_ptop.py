import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pyautogui as mouse
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from Camera_Test_Logic.Cam_3rdParty_App.Teams_Meet_Now import xp
import exception
import logging
import os

global tsis
u_name = os.environ.get('USERPROFILE')
sel_tm_dir = u_name + '\\PycharmProjects\\pythonProject\\Camera_Test_Logic\\Cam_3rdParty_App\\Teams_Meet_Now'
opt = Options()
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.notifications": 1
})
driver = webdriver.Chrome(chrome_options=opt, executable_path=sel_tm_dir + '\\' + 'chromedriver.exe')


def contactisa(p_name):
    global tsis
    logging.Logger('Execute the contact method')
    try:
        ts = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_class_name(
            'display-name').text
        print(ts)
        if ts == p_name:
            tsis = 'true'
            print(tsis)
    except NoSuchElementException:
        tsis = 'false'
        print(tsis)
    return tsis


# Calling the Attendee if he is present in the contacts list or else adding him in the contact lists

# Calling the Attendee after the adding the Contact
def call_after_add_contact(j, p_name, callt):
    driver.find_element_by_xpath(xp.seb).click()
    driver.find_element_by_xpath(xp.seb2).send_keys(p_name)
    driver.find_element_by_xpath(xp.seb2).send_keys(Keys.ENTER)
    time.sleep(3)
    driver.find_element_by_xpath(xp.callb)
    if callt == 'VIDEO':
        time.sleep(2)
        # mous.moveTo(1235, 375)
        bc = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_xpath(
            '//span[@title="Video call"]').click()
        # time.sleep(2)
        bc.click()
    elif callt == "AUDIO":
        ac = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_xpath(
            '//button[@title="Call"]')
        time.sleep(2)
        ac.click()
    time.sleep(2)
    permsn = mouse.locateCenterOnScreen(sel_tm_dir + '\\Cam_Allow1.PNG')
    mouse.moveTo(permsn)
    p = mouse.locateCenterOnScreen(sel_tm_dir + '\\popup_permission2.png')
    if permsn:
        # mous.moveTo(301, 152)
        mouse.moveTo(p)
        mouse.click()
    time.sleep(2)
    time.sleep(30)
    driver.find_element_by_xpath(xp.cnm)
    time.sleep(2)
    driver.find_element_by_xpath(xp.Controlbar)
    time.sleep(4)
    hp = driver.find_element_by_xpath(xp.grp).find_element_by_class_name("ts-items-group").find_element_by_xpath(
        xp.hangup)
    time.sleep(2)
    mouse.click()
    # mous.click()
    hp.click()
    time.sleep(8)
    return j


# Adding the Contact in the Contacts Page
def addcontact(p_name):
    driver.find_element_by_xpath('//button[@title="Add contact"]').click()
    time.sleep(3)
    driver.find_element_by_xpath('(//input[@type="search"])[2]').send_keys(p_name)
    time.sleep(3)
    driver.find_element_by_xpath('(//input[@type="search"])[2]').send_keys(Keys.ENTER)
    time.sleep(4)
    try:
        driver.find_element_by_xpath('//button[text()="Add"]').click()
        time.sleep(3)
    except exception:
        print('No user in directory with Name:-', p_name)
        return 'No user in directory with Name:-' + p_name

    driver.find_element_by_xpath(xp.seb2).clear()
    return 'done'


# Adding the Contacts Before the Contacts Page
def adcontactatfirst(p_name):
    driver.find_element_by_xpath('//button[@title="Add contact"]').click()
    time.sleep(3)
    driver.find_element_by_xpath('(//input[@type="search"])').send_keys(p_name)
    time.sleep(3)
    driver.find_element_by_xpath('(//input[@type="search"])').send_keys(Keys.ENTER)
    time.sleep(2)
    driver.find_element_by_xpath('//button[text()="Add"]').click()
    time.sleep(3)
    driver.find_element_by_xpath(xp.seb2).clear()
    return 'done'


def invitesomeone(p_name):
    driver.find_element_by_xpath(xp.invtesmne).click()
    driver.find_element_by_xpath(xp.invtesmne).send_keys(p_name)
    time.sleep(3)
    driver.find_element_by_xpath(xp.invtesmne).send_keys(Keys.ENTER)
    time.sleep(2)


'=======================================ptp_call_methods============================================'


def call(call_count, callt, p_name):
    time.sleep(5)
    driver.find_element_by_xpath(xp.calbbtn).click()
    time.sleep(3)
    driver.find_element_by_xpath(xp.callnav).click()
    time.sleep(5)
    try:
        driver.find_element_by_xpath(xp.seb).click()
    except NoSuchElementException:
        adcontactatfirst(p_name)
    driver.find_element_by_xpath(xp.seb2).send_keys(p_name)
    driver.find_element_by_xpath(xp.seb2).send_keys(Keys.ENTER)
    time.sleep(5)
    ts = contactisa(p_name)
    if ts == 'true':
        time.sleep(3)
        driver.find_element_by_xpath(xp.callb)
        if callt == 'VIDEO':
            time.sleep(2)
            # mous.moveTo(1235, 375)
            bc = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_xpath(
                '//div[@title="Video call"]')
            # time.sleep(2)
            bc.click()
        elif callt == "AUDIO":
            time.sleep(3)
            ac = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_xpath(
                '//button[@title="Call"]')
            time.sleep(2)
            ac.click()
        time.sleep(2)
        permsn = mouse.locateCenterOnScreen(sel_tm_dir + "\\Cam_Allow1.PNG")
        mouse.moveTo(permsn)
        p = mouse.locateCenterOnScreen(sel_tm_dir + '\\popup_permission2.png')
        time.sleep(2)
        if permsn:
            # mous.moveTo(301, 152)
            mouse.moveTo(p)
            mouse.click()
        time.sleep(18)
        driver.find_element_by_xpath(xp.cnm)
        time.sleep(2)
        driver.find_element_by_xpath(xp.Controlbar)
        time.sleep(4)
        hp = driver.find_element_by_xpath(xp.grp).find_element_by_class_name(
            "ts-items-group").find_element_by_xpath(
            xp.hangup)
        time.sleep(2)
        mouse.click()
        # mous.click()
        hp.click()
        time.sleep(8)
        return call_count
    elif ts == 'false':
        driver.find_element_by_xpath(xp.seb).click()
        c_stat = addcontact(p_name)
        time.sleep(5)
        if c_stat == 'done':
            call_c = call_after_add_contact(call_count, p_name, callt)
            print('no of iteration:-', call_c)
        else:
            print(exception)
            return c_stat



