import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from Camera_Test_Logic.Cam_3rdParty_App.Teams_Meet_Now import xp
import logging
import os

global tsis, cam_sett
u_name = os.environ.get('USERPROFILE')
# Please add your Local Repo project or code sorce path for Replace with similar to "JabraVideoFW\\TestServer"
# intead of \\PycharmProjects\\pythonProject
sel_tm_dir = u_name + '\\PycharmProjects\\pythonProject\\Camera_Test_Logic\\Cam_3rdParty_App\\Teams_Meet_Now'
opt = Options()
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.notifications": 1
})
driver = webdriver.Chrome(chrome_options=opt, executable_path=sel_tm_dir + '\\' + 'chromedriver.exe')


# driver = webdriver.Edge(executable_path ="D://Edge Driver//msedgedriver.exe")
def teams_main(microsoft_mailid, u_password, call_type):
    global cam_sett
    logging.Logger('Execute the Login method')
    driver.get("https://www.microsoft.com//en-in//microsoft-teams//log-in")
    time.sleep(5)
    driver.find_element_by_xpath(xp.sn).click()
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(5)
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, xp.usr3)))
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, xp.box3)))
    signin1 = driver.find_element_by_xpath(xp.usr3).find_element_by_xpath(xp.box3).find_element_by_xpath(xp.lightbox2)
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, xp.sign3)))
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, xp.name3)))
    signin1.find_element_by_xpath(xp.sign3).find_element_by_xpath(xp.name3).click()
    time.sleep(5)
    signin1.find_element_by_xpath(xp.sign3).find_element_by_xpath(xp.name3).find_element_by_xpath(xp.name4).send_keys(
        microsoft_mailid)
    time.sleep(3)
    driver.find_element_by_xpath(xp.passwordbox1).find_element_by_xpath(xp.passbox2).click()
    time.sleep(5)
    driver.find_element_by_xpath(xp.pb).send_keys(u_password)
    time.sleep(4)
    driver.find_element_by_xpath(xp.snbtn).click()
    time.sleep(20)
    driver.find_element_by_xpath(xp.xyz2).click()
    driver.maximize_window()
    time.sleep(12)
    '======================================= conf_methods================================================'

    # Logging out the Account
    def logout():
        time.sleep(5)
        driver.find_element_by_xpath(xp.profile).click()
        time.sleep(2)
        driver.find_element_by_xpath(xp.logout).click()
        time.sleep(5)
        driver.quit()

    def endcall():
        time.sleep(10)
        hp = driver.find_element_by_xpath(xp.grp).find_element_by_class_name("ts-items-group").find_element_by_xpath(
            xp.hangup)
        time.sleep(2)
        # mouse.click()
        hp.click()

    def is_camera():
        time.sleep(2)
        driver.find_element_by_xpath(xp.in_call_device).click()
        time.sleep(1)
        camera = driver.find_element_by_xpath(xp.cam_button).find_element_by_class_name(
            'button-text').text
        return camera

    def is_cam_list():
        # driver.find_element_by_xpath('//*[@id="toast-container"]/div/div/div[2]/div/button[2]').click()
        driver.find_element_by_xpath('//*[@id="device-setting-camera"]/button/div/ng-include').click()
        dropdown = driver.find_element_by_class_name('ts-dropdown-select-options-wrapper').text
        print(dropdown)
        return dropdown

    def sett():
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, xp.video_click)))
        driver.find_element_by_xpath(xp.video_click).click()
        time.sleep(2)
        driver.find_element_by_xpath(xp.video_click).click()
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, xp.settbtn)))
        driver.find_element_by_xpath(xp.settbtn).click()
        cam1 = is_camera()
        if cam1.split(' (')[0] == 'Jabra PanaCast 20' or cam1.split(' (')[0] == 'Jabra PanaCast 50':
            driver.find_element_by_xpath(xp.video_set_close).click()
            return 'true'
        for i in range(len(is_cam_list().split('\n'))):
            if str(is_cam_list().split('\n')[i]).split(' (')[0] == 'Jabra PanaCast 20' or \
                    str(is_cam_list().split('\n')[i]).split(' (')[0] == 'Jabra PanaCast 50':
                driver.find_element_by_xpath(xp.cam_lst_1).click()
                driver.find_element_by_xpath(xp.video_set_close).click()
                print('{}-Selected'.format(is_cam_list().split('\n')[i]).split(' (')[0])
                return 'true'
        else:
            return 'false'

    def startrecording():
        # global update
        driver.find_element_by_xpath(xp.settbtn).click()
        try:
            driver.find_element_by_xpath(xp.rec)
            rec_is = True
        except NoSuchElementException:
            rec_is = False
        if rec_is is True:
            driver.find_element_by_xpath(xp.rec).click()
            time.sleep(20)
            return 'Record Started'
        else:
            endcall()
            print('call ended')
            time.sleep(5)
            try:
                print('inside dismiss ')
                driver.find_element_by_xpath(xp.dismiss).click()
                update = ifnot_record()
            except NoSuchElementException:
                print('inside exception')
                update = ifnot_record()
        if update == 'Record Started':
            return update
        else:
            driver.quit()
            return update

    def ifnot_record():
        meeting_id = driver.find_element_by_xpath(xp.meetbar).find_element_by_class_name('title-text').text
        print(meeting_id)
        time.sleep(7)
        driver.find_element_by_xpath(xp.meetnow_join).click()
        time.sleep(5)
        driver.find_element_by_xpath(xp.joinbarbox).find_element_by_xpath(xp.joinowbar).click()
        time.sleep(5)
        driver.find_element_by_xpath(xp.invite_cls_btn).click()
        rec_stat = startrecording()
        return rec_stat

    def stoprecording():
        driver.find_element_by_xpath(xp.settbtn).click()
        record = driver.find_element_by_xpath(xp.rec)
        if record:
            record.click()
            time.sleep(3)
            driver.find_element_by_xpath(xp.stoprec).click()
        else:
            print('As recording is not available , please run the script again')
        time.sleep(5)

    def namechange():
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, xp.meetname)))
        driver.find_element_by_xpath(xp.meetname).clear()
        driver.find_element_by_xpath(xp.meetname).send_keys('Test Meeting')

    def meetnow():
        WebDriverWait(driver, 40).until(ec.presence_of_element_located((By.XPATH, xp.calender)))
        driver.find_element_by_xpath(xp.row).find_element_by_xpath(xp.calender).click()
        time.sleep(4)
        driver.find_element_by_xpath(xp.meetnow).click()
        time.sleep(5)
        driver.find_element_by_xpath(xp.startmeet).click()
        time.sleep(10)
        namechange()
        time.sleep(2)
        driver.find_element_by_xpath(xp.joinbarbox).find_element_by_xpath(xp.joinowbar).click()
        time.sleep(10)
        # driver.find_element_by_xpath(xp.video_click).click()
        return 'conf started'

    '=======================================main_logics=================================================='

    if call_type.lower() == "conference":
        meet_is = meetnow()
        if meet_is == 'conf started':
            cam_sett = sett()
        else:
            logout()
    if cam_sett == 'true':
        str_stat = startrecording()
        if str_stat == 'Record Started':
            stoprecording()
            endcall()
            time.sleep(10)
            logout()
            return 'Record Done!'

        else:
            os.system("taskkill /f /im chromedriver.exe")
            return "No Record"
    os.system("taskkill /f /im chromedriver.exe")
