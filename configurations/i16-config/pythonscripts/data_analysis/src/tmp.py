from subprocess import Popen, PIPE

p = Popen('qsub dummy', stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()