from sun.management import VMManagement;
from java.lang.management import ManagementFactory, RuntimeMXBean;
from java.lang.reflect import Field, Method;

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
    

def findjvmpid():
    runtimeMXBean = ManagementFactory.getRuntimeMXBean();

    jvmField = runtimeMXBean.getClass().getDeclaredField("jvm")

    jvmField.setAccessible(True);
    vmManagement = jvmField.get(runtimeMXBean);

    getProcessIdMethod = vmManagement.getClass().getDeclaredMethod("getProcessId", []);

    getProcessIdMethod.setAccessible(True);
    processId = getProcessIdMethod.invoke(vmManagement, []);
    print("The JVM Process Id: %s" %processId);

    return processId;



def emailto(me='localhost', to="X.Ren@diamond.ac.uk", subject=None):
    # Create a text/plain message
    msg = MIMEText("New GDA dump generated at: %s" %time.strftime("%a, %d %b %Y %H:%M +0000", time.gmtime()) )

    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = to

    # Send the message via our own SMTP server, but don't include the envelope header.
    s=smtplib.SMTP('localhost')
    s.sendmail(me, [to], msg.as_string())
    s.quit();


pids=findpids("gda-i07");
mypid=findmypid("gda-i07");
pid=findjvmpid();

me=findlogin();

if pidowner(pid) != me:
    print("What is this ???");
    exit();
