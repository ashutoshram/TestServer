import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import xpaths
import pyautogui as mous
import xp

#userpass = input("Enter password:")


driver = webdriver.Chrome(executable_path="D://chrome driver//chromedriver.exe")

ac = ActionChains(driver)

xpathexam= xpaths.oblue1

oblue1 = '/html/body/div/form[1]/div/div/div[2]'

oblue2 = '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div'

oblue3 = '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[1]'

insideblue = '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]'

pass1 = '//*[@id="lightbox"]/div[3]/div/div[2]/div/div[2]'

pass2 = '//*[@id="lightbox"]/div[3]/div/div[2]/div/div[2]/div'

pass3 = '//*[@id="lightbox"]/div[3]/div/div[2]/div/div[2]/div/div[2]'


box4 = '//*[@id="lightbox"]/div[3]/div/div[2]/div'

pass4 = '//*[@id="i0118"]'








sign2 = '//*[@id="lightbox"]/div[3]/div'

sign1 = '//*[@id="lightbox"]/div[3]'

name2 = '//*[@id="lightbox"]/div[3]/div/div/div/div[2]/div[2]'

name1 = '//*[@id="lightbox"]/div[3]/div/div/div/div[2]'





blue = '//*[@id="lightboxTemplateContainer"]/div[2]/div[1]/div'

pbox = '//*[@id="lightboxTemplateContainer"]/div[2]/div[1]/div/div/div/div'

lbox = '//*[@id="lightbox"]/div[1]'

inbox = '//*[@id="lightbox"]/div[3]/div/div[2]/div'











driver.get("https://www.microsoft.com/en-in/microsoft-teams/log-in")
time.sleep(5)
Signin = driver.find_element_by_xpath(xp.sn).click()
driver.switch_to.window(driver.window_handles[1])
time.sleep(3)

signin1 = driver.find_element_by_xpath(xp.usr3).find_element_by_xpath(xp.box3).find_element_by_xpath(xp.lightbox2)

#password = driver.find_element_by_xpath(blue).find_element_by_xpath(pbox).find_element_by_xpath(lbox)

#signin2 = driver.find_element_by_xpath(usr2).find_element_by_xpath(box2).find_element_by_xpath(lightbox2)

#signin3 = driver.find_element_by_xpath(usr3).find_element_by_xpath(box3).find_element_by_xpath(lightbox2)

signin1.find_element_by_xpath(xp.sign3).find_element_by_xpath(xp.name3).click()

signin1.find_element_by_xpath(xp.sign3).find_element_by_xpath(xp.name3).find_element_by_xpath(
    xp.name4).send_keys("parthu.y@motivitylabs.com")

time.sleep(3)

driver.find_element_by_xpath(xp.passwordbox1).find_element_by_xpath(xp.passbox2).click()

time.sleep(5)

#password.find_element_by_xpath(pasbox).clear()

driver.find_element_by_xpath(xp.pasbox).find_element_by_xpath(xp.afterpb).click()

time.sleep(2)

driver.find_element_by_xpath(xp.pb).send_keys('Depari@109')

#driver.find_element_by_xpath(afterpb).send_keys('pariskhit@99')


#signin1.find_element_by_xpath('//*[@id="lightbox"]/div[3]/div/div[2]/div/div[2]/div/div[2]').find_element_by_xpath(pass4).click()

time.sleep(1)

#signin1.find_element_by_xpath('//*[@id="lightbox"]/div[3]/div/div[2]/div/div[2]/div/div[2]').find_element_by_xpath(pass4).send_keys("pariskhit@99")

driver.find_element_by_xpath(xp.snbtn).click()

time.sleep(5)

driver.find_element_by_xpath(xp.xyz1).click()

time.sleep(2)

driver.find_element_by_xpath(xp.xyz2).click()

driver.maximize_window()

driver.find_element_by_xpath('//*[@id="app-bar-20c3440d-c67e-4420-9f80-0e50c39693df"]/ng-include/svg').click()

time.sleep(15)

'''driver.find_element_by_xpath('//*[@id="control-input"]').click()

l = driver.find_element_by_xpath('//*[@id="searchInputField"]')

l.send_keys('Sai Surya')

time.sleep(2)

l.send_keys(Keys.ENTER)

driver.find_element_by_xpath('//*[@id="search-result-tabs"]/li[2]/a').click()

p = driver.find_element_by_id('peopleSearchContent-0').find_element_by_xpath('//*[@id="peopleSearchContent-0"]/div/div[3]').find_element_by_link_text('Associate QA Engineer')

p.click()
'''

f = driver.find_element_by_xpath(xp.xyz3).find_element_by_xpath(xp.xyz4)

f.click()

driver.find_element_by_xpath(xp.callnav).click()

driver.find_element_by_xpath(xp.seb).click()

driver.find_element_by_xpath(xp.seb2).send_keys('Sai Surya')

driver.find_element_by_xpath(xp.seb2).send_keys(Keys.ENTER)

time.sleep(5)

e = driver.find_element_by_xpath(xp.callb)
e.find_element_by_xpath(xp.callc).click()

time.sleep(15)

####### the hangup xpaths#######################
hgpa='//*[@id="hangup-button"]/ng-include/svg'
#//*[@id="hangup-button"]/ng-include/svg

hgpb='//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/calling-unified-bar/section/div/div'

hgpc='//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/calling-unified-bar/section/div/div/div[5]'

hgpd = '//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/calling-unified-bar/section/div/div/div[5]/items-group/div/item-widget/push-button/div'

hgpe = '//*[@id="hangup-button"]'



Containbar='//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/calling-unified-bar/section/div'

Flexcompletebar='//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/calling-unified-bar/section'


AVcontrolcomplete='//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/calling-unified-bar'


callingMainMaster='//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/div[2]/div[3]'

flexmain='//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/div[2]'


###############################end##############
#ac.move_by_offset(910,640).click()
driver.find_element_by_xpath(xp.cnm)
time.sleep(2)
driver.find_element_by_xpath(xp.Controlbar)
time.sleep(4)
hp=driver.find_element_by_xpath(xp.grp).find_element_by_class_name("ts-items-group").find_element_by_xpath(xp.hangup)
time.sleep(2)
mous.moveTo(x=700,y=240)
#mous.click()
hp.click()
time.sleep(8)



driver.find_element_by_xpath(xp.threedots).click()
time.sleep(2)
driver.find_element_by_xpath(xp.logout).click()
driver.close()
#driver.find_element_by_xpath('//*[@id="hangup-button"]').click()

#driver.find_element_by_xpath('//*[@id="hangup-button"]/ng-include/svg').click()













'''username = driver.find_element_by_xpath()
driver.find_element_by_class_name("form-control ltr_override input ext-input text-box ext-text-box")
username.click()
username.send_keys('parthu.y')
driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()
password = driver.find_element_by_xpath(oblue1).find_element_by_xpath(oblue2).find_element_by_xpath(oblue3)
time.sleep(5)
#password.find_element_by_xpath(insideblue).find_element_by_xpath().find_element_by_xpath()
driver.find_element_by_xpath(insideblue).click()
driver.find_element_by_xpath(pass1).send_keys('pariskhit@99')'''

'''password.find_element_by_id("i0118").click()
password.find_element_by_id('i0118').send_keys('pariskhit@99')
signin = driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()'''

