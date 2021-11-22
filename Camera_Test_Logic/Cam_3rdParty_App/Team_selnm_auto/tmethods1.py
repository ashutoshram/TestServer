import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pyautogui as chrm
import xp
import exception
import logging


driver = webdriver.Chrome('C://chromedriver_win32//chromedriver.exe')


def login():
    logging.Logger('Execute the Login method')
    driver.get("https://www.microsoft.com/en-in/microsoft-teams/log-in")
    time.sleep(5)
    Signin = driver.find_element_by_xpath(xp.sn).click()
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(5)
    signin1 = driver.find_element_by_xpath(xp.usr3).find_element_by_xpath(xp.box3).find_element_by_xpath(xp.lightbox2)
    time.sleep(5)
    signin1.find_element_by_xpath(xp.sign3).find_element_by_xpath(xp.name3).click()
    time.sleep(5)
    signin1.find_element_by_xpath(xp.sign3).find_element_by_xpath(xp.name3).find_element_by_xpath(xp.name4).send_keys(
        "rahul.p@motivitylabs.com")
    time.sleep(3)
    driver.find_element_by_xpath(xp.passwordbox1).find_element_by_xpath(xp.passbox2).click()
    time.sleep(5)
    driver.find_element_by_xpath(xp.pasbox).find_element_by_xpath(xp.afterpb).click()
    time.sleep(2)
    driver.find_element_by_xpath(xp.pb).send_keys('R@hul@1954')
    driver.find_element_by_xpath(xp.snbtn).click()
    time.sleep(20)
    driver.find_element_by_xpath(xp.xyz2).click()
    driver.maximize_window()
    time.sleep(12)

# Goint to Validate the contact Is present of not .
def contactisa(p_name):
    global tsis
    logging.Logger('Execute the contact method')
    try:
        ts = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_class_name(
            'display-name').text
        print(ts)
        if ts == p_name:
            #logging.Logger('User is Already exist')
            tsis = 'true'
            print(tsis)
    except NoSuchElementException:
        #logging.Logger.log('There is no user with name ')
        tsis = 'false'
        print(tsis)
    return tsis

#Calling the Attendee if he is present in the contacts list or else adding him in the contact lists
def call(j, callt, p_name):
    #logging.Logger('Execute the call method')
    time.sleep(5)
    driver.find_element_by_xpath(xp.calbbtn).click()
    time.sleep(3)
    driver.find_element_by_xpath(xp.callnav).click()
    time.sleep(5)
    """try:
        print('inside existing contact')
        driver.find_element_by_xpath('//button[@title="Add contact"]').click()"""

    """except NoSuchElementException:
        print('inside add contact')
        driver.find_element_by_xpath(xp.adb).click()
        addcontact(p_name)"""
    try:
        driver.find_element_by_xpath(xp.seb).click()
    except NoSuchElementException:
        #driver.find_element_by_xpath('//button[@title="Add contact"]').click()
        #add contact xpath with search 1 tag
        #adc=addcontact(p_name)
        #print('Contact added:-',adc)
        Addcontactatfirst(p_name)
    driver.find_element_by_xpath(xp.seb2).send_keys(p_name)
    driver.find_element_by_xpath(xp.seb2).send_keys(Keys.ENTER)
    time.sleep(5)
    ts = contactisa(p_name)
    if ts == 'true':
        time.sleep(3)
        #ac=driver.find_element_by_class_name("app-icon-fill-hover custom-icon ts-sym ts-svg").find_element_by_name("//title[text()='Call']").click()
        #Ncall = mous.locateCenterOnScreen('Nc.PNG')
        #Vcall = mous.locateCenterOnScreen('Vc.PNG')
        #e = driver.find_element_by_xpath(xp.callb)
        if callt == 'VIDEO':
            #chrm.moveTo(1235, 375)
            vc = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_xpath('//span[@title="Video call"]')
            #time.sleep(2)
            vc.click()
            '''mous.moveTo(1235, 375)
            bc = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_xpath('//span[@title="Video call"]')
            time.sleep(2)
            bc.click()'''
        elif callt == "AUDIO":
            time.sleep(3)
            ac = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_xpath('//button[@title="Call"]')
            time.sleep(2)
            ac.click()
            '''mous.moveTo(1266, 378)
            mous.click()
            time.sleep(3)
            mous.moveTo(Ncall)
            mous.click()'''
        brwsr=chrm.getWindowsWithTitle('Google Chrome')[0].activate()
        time.sleep(3)
        permsn = chrm.locateCenterOnScreen("Cam_Allow1.PNG")
        chrm.moveTo(permsn)
        time.sleep(3)
        p = chrm.locateCenterOnScreen('popup_permission2.PNG')
        logging.Logger('allow is  being found')
        print(permsn)
        print(p)
        if permsn:
            chrm.moveTo(p)
            logging.Logger('Allow is being clicked')
            chrm.click()
        time.sleep(18)
        driver.find_element_by_xpath(xp.cnm)
        time.sleep(2)
        driver.find_element_by_xpath(xp.Controlbar)
        time.sleep(4)
        hp = driver.find_element_by_xpath(xp.grp).find_element_by_class_name("ts-items-group").find_element_by_xpath(
            xp.hangup)
        time.sleep(2)
        chrm.click()
        # mous.click()
        hp.click()
        time.sleep(8)
        return j
    elif ts == 'false':
        driver.find_element_by_xpath(xp.seb).click()
        #click on add contact
        #add contact sendkeys with pname for search tag2
        c_stat = addcontact(p_name)
        time.sleep(5)
        if c_stat == 'done':
            call_c = call_after_add_contact(j, p_name, callt)
            print('no of iteration:-', call_c)
        else:
            print(exception)

#Calling the Attendee after the adding the Contact
def call_after_add_contact(j, p_name, callt):
    driver.find_element_by_xpath(xp.seb).click()
    driver.find_element_by_xpath(xp.seb2).send_keys(p_name)
    driver.find_element_by_xpath(xp.seb2).send_keys(Keys.ENTER)
    time.sleep(3)
    #Ncall = mous.locateCenterOnScreen('Nc.PNG')
    #Vcall = mous.locateCenterOnScreen('Vc.PNG')
    e = driver.find_element_by_xpath(xp.callb)
    if callt == 'VIDEO':
        ac = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_xpath(
            '//button[@title="Call"]')
        ac.click()
        '''mous.moveTo(1235, 375)
        mous.click()
        time.sleep(3)
        mous.moveTo(Vcall)
        mous.click()'''
    elif callt == "AUDIO":
        ac = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_xpath(
            '//button[@title="Call"]')
        time.sleep(2)
        ac.click()
        '''mous.moveTo(1266, 378)
        mous.click()
        time.sleep(3)
        mous.moveTo(Ncall)
        mous.click()'''
    time.sleep(2)
    permsn = chrm.locateOnScreen('Cam_Allow1.PNG')
    chrm.moveTo(permsn)
    p = chrm.locateCenterOnScreen('popup_permission2.PNG')
    if permsn:
        chrm.moveTo(p)
        chrm.click()
    time.sleep(18)
    driver.find_element_by_xpath(xp.cnm)
    time.sleep(2)
    driver.find_element_by_xpath(xp.Controlbar)
    time.sleep(4)
    hp = driver.find_element_by_xpath(xp.grp).find_element_by_class_name("ts-items-group").find_element_by_xpath(
        xp.hangup)
    time.sleep(2)
    chrm.click()
    # mous.click()
    hp.click()
    time.sleep(8)
    return j

#Logging out the Account
def logout():
    driver.find_element_by_xpath(xp.threedots).click()
    time.sleep(2)
    driver.find_element_by_xpath(xp.logout).click()
    #driver.close()

#Adding the Contact in the Contacts Page
def addcontact(p_name):
    driver.find_element_by_xpath('//button[@title="Add contact"]').click()
    time.sleep(3)
    driver.find_element_by_xpath('(//input[@type="search"])[2]').send_keys(p_name)
    time.sleep(3)
    driver.find_element_by_xpath('(//input[@type="search"])[2]').send_keys(Keys.ENTER)
    time.sleep(2)
    driver.find_element_by_xpath('//button[text()="Add"]').click()
    time.sleep(3)
    driver.find_element_by_xpath(xp.seb2).clear()
    return 'done'


#Adding the Contacts Before the Contacts Page
def Addcontactatfirst(p_name):
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
#driver.close()