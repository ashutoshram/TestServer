import os


def meet_now(microsoft_mailid, u_password, call_typ):
    from Camera_Test_Logic.Cam_3rdParty_App.Teams_Meet_Now.team_conf import teams_main
    try:
        call_rcd = teams_main(microsoft_mailid, u_password, call_typ)
        return call_rcd
    except ValueError:
        print("Fail to start meet now")
        return 'No Record Done'


def peer_to_peer():
    from Camera_Test_Logic.Cam_3rdParty_App.Teams_Meet_Now.team_conf import teams_main
    call_count = 1
    usr_name = 'Sai Surya Krishna Dixit Dasika'
    call_type = 'Video'
    teams_main(call_count, usr_name, call_type)


def tms_meet_now():
    microsoft_mailid = '<Please provide the Lab username>'  # input("please Enter your Mail ID:")
    u_password = 'Please provide password'  # input("please Enter your password:")
    call_typ = 'Conference'
    call = meet_now(microsoft_mailid, u_password, call_typ)
    print(call)
    os.system("taskkill /f /im chromedriver.exe")
    return call
