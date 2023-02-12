import requests
session = requests.Session()
Pseudo01 = None
Password01 = None
ADMIN = None
URL = "http://10.10.0.30/"
URL = "http://localhost:3000/"


def login(username=None):
    password = GetPassword(username)
    global Pseudo01  # global variable to be used in the function and outside the function
    global Password01
    global ADMIN
    if Pseudo01 != None and Password01 != None and ADMIN == None:
        ADMIN = "Connected"
        Pseudo01 = None
        Password01 = None
        return session.get(URL+"sign_z01/PHP/sign.php?" + urllib.parse.urlencode({  # login to the website with the credentials in the ZONE01.txt file return is used to check if the login is successful and end the function
            "pseudo": Pseudo01,
            "password": Password01,
            "submit": "Connexion",
        })).status_code == 200, "You are now connected"
    elif username != None and password != None:
        pseudo01 = username
        password01 = password
        ADMIN = None
        return session.get(URL+"sign_z01/PHP/sign.php?" + urllib.parse.urlencode({
            "pseudo": pseudo01,
            "password": password01,
            "submit": "Connexion",
        })).status_code == 200, "You are now connected"
    elif username == None or password == None:
        return "Error", "Please ask an admin to add your credentials in the ZONE01.txt file"


def SwitchDoor(PushTRUEorPullFALSE):  # Enter (alias Push) or Exit (alias Pull)
    # switch PushTRUEorPullFALSE to 1 or 0
    # ping 10.10.0.30 if down return
    ping = os.system("ping -c 1 10.10.0.30")
    if PushTRUEorPullFALSE == "ENTER":
        if ping != 0:
            return "Door is locked"
        else:
            EnterFuck01()
    elif PushTRUEorPullFALSE == "EXIT":
        if ping != 0:
            print()
        else:
            ExitLove01()


def logout():
    session.get(URL+"sign_z01/PHP/deco.php")


def EnterFuck01():
    if not login():
        sys.exit(1)
    print("Enter...")
    session.get(URL+"sign_z01/PHP/enter.php")
    logout()


def ExitLove01():
    if not login():
        return "Error", "Please ask an admin to add your credentials in the ZONE01.txt file"
    print("Exit...")
    session.get(URL+"sign_z01/PHP/exit.php")
    logout()
    return "Success", "You have left the zone"


def ExportedCredentials___():
    if Pseudo01 == None or Password01 == None:
        return False
    else:
        return True
def GetPassword(username):
    # Read the ZONE01.txt file and get the username and password each line like(username password)
    for line in open("ZONE01.txt"):
        Credentials = line.split(" ")
        Username = Credentials[0]
        Password = Credentials[1]
        if Username == username:
            # if username is found return the password
            return Password

