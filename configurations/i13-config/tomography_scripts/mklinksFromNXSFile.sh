echo "Hostname: "
echo $HOSTNAME

. /etc/profile.d/modules.sh
cd /dls_sw/i13/software/gda/config/tomography_scripts/
module load numpy
echo "Python interpreter: "
which python
echo "Python command: "
echo python mklinksFromNXSFile.py $@
python mklinksFromNXSFile.py $@
