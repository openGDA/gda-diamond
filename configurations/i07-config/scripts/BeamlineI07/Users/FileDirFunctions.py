# creates UserSetup.py file in the current user directory
# and makes it editable by members of the experiment's group

from os import system
from datetime import datetime as filedir_datetime
from commands import getoutput

def createUserSetup():
    userdir = "/".join(i07.getDataPath().split("/",6)[0:6])
#    userdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()

    if not path.isdir(userdir):
        print "Error: user directory " + userdir + " does not exist"
    else:
        userfile = userdir + "/UserSetup.py"
        if not path.isfile(userfile):
            print "Creating empty file " + userfile
            system("touch " + userfile)
        else:
            print "File " + userfile + " exists"
        system("setfacl -m g::rwx,u:i07user:rwx,m::rw " + userfile)
        print "Permissions set. Users should now be able to edit this file"


# sets the file path for both Pilatus detectors to the I07 defaults

# gives i07user permission to access data directory

def i07userperm(visit = ''):
    if visit == '':
        visit = getvisit()
    print "Applying permissions to visit " + visit
    year = filedir_datetime.today().year
    d = "/dls/i07/data/" + str(year) + "/" + visit
    if not visit.startswith("cm"):
            print getoutput("setfacl -n -m u:i07user:rx " + d)
            print getoutput("setfacl -n -m u:i07user:rx " + d + "/pilatus?")
            print getoutput("setfacl -n -m u:i07user:rwx " + d + "/processing")
            print getoutput("setfacl -n -m d:u:i07user:rx " + d)
            print getoutput("setfacl -n -m d:u:i07user:rx " + d + "/pilatus?")
            print getoutput("setfacl -n -m d:u:i07user:rwx " + d + "/processing")
    else:
            # remove write permission default for new files to prevent
            # accidental corrupting of data
            print getoutput("setfacl -n -m d:g:i07user:rx " + d)
            print getoutput("setfacl -n -m d:g:i07_staff:rx " + d)

# recursively sets permissions for i07user if you forget to do it at the start

def i07userperm_r(visit = ''):
    if visit == '':
        visit = getvisit()
    i07userperm(visit)
    print "Applying permissions for i07user recursively to visit " + visit
    year = filedir_datetime.today().year
    d = "/dls/i07/data/" + str(year) + "/" + visit

    print getoutput("setfacl -R -n -m u:i07user:rx " + d)
    print getoutput("setfacl -R -n -m u:i07user:rwx " + d + "/processing")

alias("createUserSetup")
alias("i07userperm")
alias("i07userperm_r")
