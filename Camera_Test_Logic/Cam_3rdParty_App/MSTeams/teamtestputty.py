import os
import pyautogui
import time
from time import sleep
import paramiko


# open remote machine connection

#os.startfile("C:/Program Files/PuTTY/putty.exe")
time.sleep(2)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('Testmac',username='Altia Mamba', password="Test123$&")
stdin, stdout, stderr = ssh.exec_command(

'''
cd Desktop/Cam_Test/Camera_Test_Logic/
/Users/mamba/venv/bin/python ./runningfps.py

''')
print (stdout.read())
#stdin, stdout, stderr = ssh.exec_command('cd Downloads')
status =  ssh.get_transport().is_active()
print(status)