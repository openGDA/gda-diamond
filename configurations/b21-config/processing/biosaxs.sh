#! /bin/bash

. /usr/share/Modules/init/bash

module load global/cluster

# those two need to be in sync
DAWN=/dls_sw/apps/DawnDiamond/master/builds-stable/stable-linux64/dawn
MOML=/home/zjt21856/ncd_model.moml

# those would be found in the environment
# beamline staff specified
#PERSISTENCEFILE=/home/zjt21856/persistence_file.nxs
#NCDREDXML=/home/zjt21856/ncd_configuration.xml

# these should be on the command line
#DATAFILE=/home/zjt21856/i22-34820.nxs
#BACKGROUNDFILE=/home/zjt21856/i22-34820.nxs
DATAFILE="$1"
BACKGROUNDFILE="$2"

REDUCTIONOUTPUTFILE=

#is file in visit
read VISIT RESTOFPATH <<<$( echo $DATAFILE | sed 's,\(/dls/.../data/20../[-a-z0-9]*\)/\(.*\),\1 \2,')
echo $RESTOFPATH
if test -d $VISIT ; then
	echo running reduction in visit based directory under $VISIT
	if test -w $VISIT ; then
		REDUCTIONOUTPUTFILE=$(basename ${VISIT}/processed/${RESTOFPATH} nxs).reduced.nxs
		mkdir -p $(dirname $REDUCTIONOUTPUTFILE)
	else 
		REDUCTIONOUTPUTFILE=$(basename ${VISIT}/processing/${RESTOFPATH} nxs).reduced.nxs
		mkdir -p $(dirname $REDUCTIONOUTPUTFILE)
		REDUCTIONOUTPUTFILE=
	fi
	TMPDIR=$(dirname ${VISIT}/tmp/${RESTOFPATH})
	mkdir -p $TMPDIR
	TMPDIR=$(mktemp -d ${TMPDIR}.XXX)
else
	echo running reduction outside of a visit
	TMPDIR=$(mktemp -d ${DATAFILE}.XXX)
fi

cd $TMPDIR
echo now in $TMPDIR

WORKSPACE=$TMPDIR/workspace
mkdir $WORKSPACE
OUTPUTDIR=$TMPDIR/output
mkdir $OUTPUTDIR

sed "s,bgFile>/dls/i22/data/2013/sm8174-1/i22-107002.nxs</bgFile,bgFile>${BACKGROUNDFILE}</bgFile," < $NCDREDXML > ncd_reduction.xml
NCDREDXML=${TMPDIR}/ncd_reduction.xml

mkdir ${WORKSPACE}/reduction/
WORKSPACEMOML=${WORKSPACE}/reduction/reduction.moml
ln -s $MOML $WORKSPACEMOML

# /dls_sw/apps/DawnDiamond/master/builds-stable/stable-linux64/dawn -noSplash -application com.isencia.passerelle.workbench.model.launch -data $WORKSPACE -consolelog -os linux -ws gtk -arch $HOSTTYPE -vmargs -Dorg.dawb.workbench.jmx.headless=true -Dcom.isencia.jmx.service.terminate=false -Dmodel=$MODEL -Dxml.path=/scratch/ws/gda836_git/scisoft-ncd.git/uk.ac.diamond.scisoft.ncd.actors/test/uk/ac/diamond/scisoft/ncd/actors/test/ncd_configuration.xml -Draw.path=/scratch/ws/gda836_git/scisoft-ncd.git/uk.ac.diamond.scisoft.ncd.actors/test/uk/ac/diamond/scisoft/ncd/actors/test/i22-34820.nxs -Dpersistence.path=/scratch/ws/gda836_git/scisoft-ncd.git/uk.ac.diamond.scisoft.ncd.actors/test/uk/ac/diamond/scisoft/ncd/actors/test/persistence_file.nxs -Doutput.path=/scratch/ws/junit-workspace/workflows/output
#-data /tmp/foo \

SCRIPT=$TMPDIR/qsub.script.$$
cat >> qsub.script.$$ <<EOF
$DAWN -noSplash -application com.isencia.passerelle.workbench.model.launch \
-data $WORKSPACE \
-consolelog -os linux -ws gtk -arch $(arch) -vmargs \
-Dorg.dawb.workbench.jmx.headless=true \
-Dcom.isencia.jmx.service.terminate=false \
-Dmodel=$WORKSPACEMOML \
-Dlog.folder=$TMPDIR \
-Dxml.path=$NCDREDXML \
-Draw.path=$DATAFILE \
-Dpersistence.path=$PERSISTENCEFILE \
-Doutput.path=$OUTPUTDIR


if test -n "$REDUCTIONOUTPUTFILE" ; then 
	for i in $OUTPUTDIR/results*.nxs ; do
		mv \$i $REDUCTIONOUTPUTFILE
		break;
	done
fi
EOF

qsub $SCRIPT
