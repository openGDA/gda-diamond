########### ready to test. call with scan number and add qsub opts
import os

def mk_txt_file(fullname, text):
    f = open(fullname, 'w')
    f.write(text)
    f.close()


pycommand='python'
pyfile='two_photon_correlations.py' #with extension
pyargfmt='/dls/i16/data/2014/cm4968-3/ %i %i %i'
qsubopts='-pe smp 12' #for more cores (=more memory)
#qsubopts='-pe smp 12 -l tesla64' #
#path='/dls/i16/data/2014/cm4968-3/processing/'
path='/dls_sw/i16/software/gda/config/pythonscripts/data_analysis/src/'
datadir='/dls/i16/data/2014/cm4968-3/processing/'

#bashname='tmp1.sh'

#for scan in [450745]:
#for scan in range(450745,450755):# pdc etazero+0.056 atten 0

npts=1000
nparts=10
for scan in range(450745,450755):# pdc etazero+0.056 atten 0
    for scanbit in range(nparts):
        pyargs=pyargfmt % (scan, scanbit*npts/nparts+1, (scanbit+1)*npts/nparts)
        bashname='submit_scan_%i_part_%i.sh' % (scan, scanbit)
        mk_txt_file(datadir+bashname, 'module load scisoftpy/ana\ncd '+datadir+'\n'+pycommand+' '+path+pyfile+' '+pyargs)
        #os.system('cd '+datadir+'; qsub '+qsubopts+' '+datadir+bashname)
        os.system('cd '+datadir+'; qsub '+qsubopts+' '+datadir+bashname) 
#module load scisoftpy/ana; qsub /dls_sw/i16/software/gda/config/pythonscripts/data_analysis/src/submit_scan_450745.sh



'''
#   use qdel to delete job
#os.system('pwd')
#os.system('ls')
os.chdir('/dls_sw/i16/software/gda/config/pythonscripts/data_analysis/src')
#os.chdir('/dls/i16/data/2014/cm4968-3/processing')
sys.path.append('/dls_sw/i16/software/gda/config/pythonscripts/data_analysis/src')
sys.path.append('/dls_sw/i16/software/gda/config/pythonscripts/data_analysis/dlstools')

#os.system('chmod +x tmp.py; ./tmp.py 4') #ok

#os.system('./tmp.py 44') #ok
#os.system('qsub -v 55 tmp.py') #didb't work

#os.system('./tmp.py') #ok
#os.system('qsub -V -cwd /dls_sw/i16/software/gda/config/pythonscripts/data_analysis/src/tmp.py') #job submitted but errors
os.system('module load global/cluster; qsub -V -cwd tmp1.sh') #doesn't work
#os.system('module load global/cluster; qsub -V -cwd python tmp1.py') #doesn't work

#####
os.system('qstat')


#os.system('python tmp.py &') #ok
print os.getcwd()
os.system('ls tmp*.py')
#os.system('/dls_sw/i16/software/gda/config/pythonscripts/data_analysis/src/tmp1.py')
'''