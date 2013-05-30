#! /usr/bin/env python

import os, commands,subprocess, time;
import smtplib #for the actual sending function
from email.mime.text import MIMEText #for email


def findpids(processname):
    pidline=commands.getoutput('/sbin/pidof %s' % processname);
    if pidline is '':
        raise "No process found"
    
    pids=pidline.rsplit();
    return pids

def findmypid(processname):
# ps -u `whoami` -f --cols 6000 | grep -F -e 'gda-i07' | grep -v grep
    hook = subprocess.Popen("ps -u `whoami` | grep -F -e %s" %processname, shell=True, stdout=subprocess.PIPE)
    output = hook.stdout.read().split()
    hook.stdout.close()
    hook.wait()
    pid =output[0];
    print("The GDA client Process Id: %s" %pid);
    return pid;

  
def findlogin():
    return os.getlogin().encode('utf-8');
#    return commands.getoutput("whoami");

def pidowner(pid):
    hook = subprocess.Popen("ps -eo pid,user,group,args,etime,lstart | grep %s | grep -v grep" %pid, shell=True, stdout=subprocess.PIPE)
    output = hook.stdout.read().split()
    hook.stdout.close()
    hook.wait()
    user =output[1];
    print("The GDA client owner: %s" %user);
    return user;
    
def emailto(me='localhost', to="X.Ren@diamond.ac.uk", subject=None):
    # Create a text/plain message
    msg = MIMEText("New GDA dump generated at: %s" %time.strftime("%a, %d %b %Y %H:%M +0000", time.gmtime()) )

    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = to
    msg['Cc'] = 'Paul.Gibbons@diamond.ac.uk'

    # Send the message via our own SMTP server, but don't include the envelope header.
    s=smtplib.SMTP('localhost')
    s.sendmail(me, [to], msg.as_string())
    s.quit();


########################
def determine_gda_config(self):
    self.options.gda_config = os.getenv("GDA_CONFIG")
        
    if not self.options.gda_config and os.getenv("BEAMLINE"):
        path = abspath(self.options.gda_root,"..", os.getenv("BEAMLINE").lower() + "-config")
        if os.path.isdir(path):
            self.options.gda_config = path
        
        if not self.options.gda_config:
            path = abspath(self.options.gda_root, "..", "config")
            if os.path.isdir(path):
                self.options.gda_config = path
        
        if not self.options.gda_config:
            path = abspath(self.options.gda_root, "..", "configurations", "diamond", "base")
            if os.path.isdir(path):
                self.options.gda_config = path

        if not self.options.gda_config:
            path = abspath(self.options.gda_root, "..", "gda-config-base")
            if os.path.isdir(path):
                self.options.gda_config = path

        if not self.options.gda_config:
            path = abspath(self.options.gda_root, "..", "example-config")
            if os.path.isdir(path):
                self.options.gda_config = path

########################

bl=os.getenv("BEAMLINE");
if bl is None:
    print "Beamline not defined"
    exit();


#Method 1: To find all the pids and match with owner
jpids = findpids('gda-%s' %bl);
me=findlogin();
for pid in jpids:
    if pidowner(pid)==me:
        jpid=pid;
        print("The GDA client Process Id: %s" %jpid);
        break;

#Method 2: To find the my pid
#jpid = findmypid('gda-i07');


dumpFileA="/scratch/gda_dump_%s_A.bin" %time.strftime("%Y%m%d_%H:%M:%S", time.gmtime());
dumpCommand="jmap -dump:format=b,file=%s %s" %(dumpFileA, jpid)
os.system(dumpCommand);

raw_input("Please go back to GDA Client, close the 'Area Detector' View, then press Enter to continue ")
dumpFileB="/scratch/gda_dump_%s_B.bin" %time.strftime("%Y%m%d_%H:%M:%S", time.gmtime());
dumpCommand="jmap -dump:format=b,file=%s %s" %(dumpFileB, jpid)
os.system(dumpCommand);

print "Thank you. Two dump file have been generated and an email notification has been sent to your DASC group contact.";
emailto(subject="New GDA dump: %s and %s" %(dumpFileA, dumpFileB));
