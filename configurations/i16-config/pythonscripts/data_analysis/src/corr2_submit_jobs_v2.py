# test to see when jobs go from queue and test to see if .e file is empty
# update dict with completion status: completed; success
# submit all jobs with -h option (change two_photon_... from test mode)

#drmaa - python job management
#qacct -j 3778077 #check job info



import os
from subprocess import Popen, PIPE
import pickle
import time
import pprint

MonitorOnly=True    #Monitor jobs already submitted - no new jobs

def oscall(cmd, test=False):
    print cmd
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    return p.communicate()

def mk_txt_file(fullname, text):
    f = open(fullname, 'w')
    f.write(text)
    f.close()

pycommand='python'
pyfile='two_photon_correlations_v2.py' #with extension
pyargfmt='/dls/i16/data/2014/cm4968-3/ %i'
#qsubopts='-pe smp 12' #for more cores (=more memory)
#qsubopts='-l m_mem_free=20G -q low.q' #run on machine with 20Gb and ensure slow queue (no time limit) 
qsubopts='-h -l m_mem_free=20G -q low.q' # hold till released
success_message='=== Job completed ==='
pickle_file='jobs_aug_14.p' #for jobs dict

bashfmt='submit_scan_%i.sh'

path='/dls_sw/i16/software/gda/config/pythonscripts/data_analysis/src/'
datadir='/dls/i16/data/2014/cm4968-3/processing/'

goodscns=[458468, 458469, 458470, 458471, 458472, 458473, 458474, 458475, 458476, 458477, 458484, 458485, 458486, 458487, 458488, 458489, 458490, 458491, 458492, 458493, 458494, 458495, 458496, 458497, 458498, 458499, 458500, 458501, 458502, 458503, 458504, 458505, 458506, 458507, 458508, 458509, 458510, 458511, 458512, 458513, 458514, 458515, 458516, 458517, 458518, 458519, 458520, 458521, 458522, 458523, 458524, 458525, 458526, 458527, 458528, 458529, 458530, 458531, 458532, 458533, 458534, 458535, 458536, 458537, 458538, 458539, 458540, 458541, 458542, 458543, 458544, 458545, 458546, 458547, 458548, 458549, 458550, 458551, 458552, 458553, 458554, 458555, 458556, 458557, 458558, 458559, 458560, 458561, 458562, 458563, 458564, 458565, 458566, 458567, 458568, 458569, 458570, 458571, 458572, 458573, 458574, 458575, 458576, 458577, 458578, 458579, 458580, 458581, 458582, 458583, 458584, 458585, 458586, 458587, 458588, 458589, 458590, 458591, 458592, 458593, 458594, 458595, 458596, 458597, 458598, 458599, 458600, 458601]

if MonitorOnly==True:
    jobs = pickle.load( open(pickle_file , "rb" ) )
else:
    jobs={}
    #for scan in goodscns[0:1]:
    for scan in goodscns:
        pyargs=pyargfmt % scan
        bashname=bashfmt % scan
        mk_txt_file(datadir+bashname, 'module load scisoftpy/ana\ncd '+datadir+'\n'+pycommand+' '+path+pyfile+' '+pyargs)
        #os.system('cd '+datadir+'; qsub '+qsubopts+' '+datadir+bashname)
        cmd='cd '+datadir+'; qsub '+qsubopts+' '+datadir+bashname
        stdout, stderr = oscall(cmd)
        job_no=int([token for token in stdout.split() if token.isdigit()][0])
        jobs[job_no]= {'scan':scan, 'stdout':stdout, 'stderr':stderr}
    pickle.dump(jobs, open( "jobs_aug_14.p", "wb" ) )


for key in jobs.keys():
    scan = jobs[key]['scan']
    job_out_file = (datadir+bashfmt+'.o%i') % (scan, key)
    print job_out_file
    jobs[key]['success']=None
    try:
        f=open(job_out_file); lines=f.readlines(); f.close;
        for line in lines:
            if success_message in line:
                jobs[key]['success']=True
                pickle.dump(jobs, open( "jobs_aug_14.p", "wb" ) )
    except:
        print '=== Error reading file: '+job_out_file
    
pprint.pprint(jobs)
strlist=oscall('qstat')[0].split('\n')[2:-1]
livejobs=[int(str.split()[0]) for str in strlist]
print '=== Number of live jobs: %i' % len(livejobs)
