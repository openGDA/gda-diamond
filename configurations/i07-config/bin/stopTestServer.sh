#!/bin/sh

FITNESSE_HOME=/usr/local/JavaPackages/fitnesse
TEST_SERVER=diamrl5068.diamond.ac.uk
TEST_PORT=1300


#ShutDown manually over URL by http://hostname:prot?responder=shutdown, or:
java -cp ${FITNESSE_HOME}/fitnesse.jar fitnesse.Shutdown -p ${TEST_PORT}

