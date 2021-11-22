import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pyautogui as mous
import xp
import exception

driver = webdriver.Chrome('C://chromedriver_win32//chromedriver.exe')


def login():
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


def contactisa(p_name):
    ts = driver.find_element_by_xpath("//*[starts-with(@id,'8:orgid:')]").find_element_by_class_name('display-name').text
    print(ts)
    if ts == p_name:
        tsis = 'true'
        print(tsis)
    else:
        tsis = 'false'
        print(tsis)
    return tsis


def call(j, callt, p_name):
    time.sleep(5)
    driver.find_element_by_xpath(xp.calbbtn).click()
    driver.find_element_by_xpath(xp.callnav).click()
    time.sleep(5)
    driver.find_element_by_xpath(xp.seb).click()
    driver.find_element_by_xpath(xp.seb2).send_keys(p_name)
    driver.find_element_by_xpath(xp.seb2).send_keys(Keys.ENTER)
    time.sleep(5)
    ts = contactisa(p_name)
    if ts == 'true':
        time.sleep(3)
        #ac=driver.find_element_by_class_name("app-icon-fill-hover custom-icon ts-sym ts-svg").find_element_by_name("//title[text()='Call']").click()
        Ncall = mous.locateCenterOnScreen('Nc.PNG')
        Vcall = mous.locateCenterOnScreen('Vc.PNG')
        e = driver.find_element_by_xpath(xp.callb)
        if callt == 'VIDEO':
            mous.moveTo(1235, 375)
            mous.click()
            time.sleep(3)
            mous.moveTo(Vcall)
            mous.click()
        elif callt == "AUDIO":
            time.sleep(3)
            #ac = driver.find_element_by_class_name("exchange-contacts-tab .cell.person")
            mous.moveTo(1266, 378)
            mous.click()
            time.sleep(3)
            mous.moveTo(Ncall)
            mous.click()
        permsn = mous.locateCenterOnScreen("prmrss1.PNG")
        mous.moveTo(permsn)
        p = mous.locateCenterOnScreen('popup_permission2.PNG')
        print(permsn)
        print(p)
        if p:
            mous.moveTo(p)
            mous.click()
        time.sleep(18)
        driver.find_element_by_xpath(xp.cnm)
        time.sleep(2)
        driver.find_element_by_xpath(xp.Controlbar)
        time.sleep(4)
        hp = driver.find_element_by_xpath(xp.grp).find_element_by_class_name("ts-items-group").find_element_by_xpath(
            xp.hangup)
        time.sleep(2)
        mous.click()
        # mous.click()
        hp.click()
        time.sleep(8)
        return j
    elif ts == 'false':
        c_stat = addcontact(p_name)
        if c_stat == 'done':
            call_c = call_after_add_contact(j, p_name, callt)
            print('no of iteration:-', call_c)
        else:
            print(exception)


def call_after_add_contact(j, p_name, callt):
    driver.find_element_by_xpath(xp.seb).click()
    driver.find_element_by_xpath(xp.seb2).send_keys(p_name)
    driver.find_element_by_xpath(xp.seb2).send_keys(Keys.ENTER)
    time.sleep(3)
    Ncall = mous.locateCenterOnScreen('Nc.PNG')
    Vcall = mous.locateCenterOnScreen('Vc.PNG')
    e = driver.find_element_by_xpath(xp.callb)
    if callt == 'VIDEO':
        mous.moveTo(1235, 375)
        mous.click()
        time.sleep(3)
        mous.moveTo(Vcall)
        mous.click()
    elif callt == "AUDIO":
        mous.moveTo(1266, 378)
        mous.click()
        time.sleep(3)
        mous.moveTo(Ncall)
        mous.click()
    time.sleep(2)
    permsn = mous.locateCenterOnScreen('prmrss1.PNG')
    mous.moveTo(permsn)
    p = mous.locateCenterOnScreen('prms.PNG')
    if permsn:
        mous.moveTo(p)
        mous.click()
    time.sleep(18)
    driver.find_element_by_xpath(xp.cnm)
    time.sleep(2)
    driver.find_element_by_xpath(xp.Controlbar)
    time.sleep(4)
    hp = driver.find_element_by_xpath(xp.grp).find_element_by_class_name("ts-items-group").find_element_by_xpath(
        xp.hangup)
    time.sleep(2)
    mous.click()
    # mous.click()
    hp.click()
    time.sleep(8)
    return j


def logout():
    driver.find_element_by_xpath(xp.threedots).click()
    time.sleep(2)
    driver.find_element_by_xpath(xp.logout).click()
    driver.close()


def addcontact(p_name):
    driver.find_element_by_xpath('//button[@title="Add contact"]').click()
    driver.find_element_by_xpath('//*[@id="amsdcController"]').find_element_by_class_name('member-search-box').send_keys(p_name)
    driver.find_element_by_xpath('//*[@id="amsdcController"]').click()
    time.sleep(3)
    #driver.find_element_by_xpath('//button[text()="Add"]').click()
    driver.find_element_by_xpath('//*[@id="add-speed-dial-button"]').click()
    return 'done'
