#!/bin/bash
#
export BEAMLINE=i06

FITNESSE_HOME=/dls_sw/dasc/testing/fitnesse
TEST_SERVER=i06-control.diamond.ac.uk
TEST_PORT=1200


GDA_ROOT=/dls/$BEAMLINE/software/gda-test
GDA_USERS=/dls/$BEAMLINE
GDA_CONFIG=$GDA_ROOT/config
JAVA_HOME=/dls/$BEAMLINE/software/java/jre
JYTHON_HOME=/dls/$BEAMLINE/software/jython

export GDA_ROOT
export GDA_USERS
export GDA_CONFIG
export JAVA_HOME
export JYTHON_HOME

#export FITNESSE_HOME
#export TEST_SERVER
#export TEST_PORT

PATH=$JAVA_HOME/bin:$GDA_ROOT/bin:$GDA_ROOT/lib:$JYTHON_HOME:/dls/$BEAMLINE/bin:${PATH}
export PATH
