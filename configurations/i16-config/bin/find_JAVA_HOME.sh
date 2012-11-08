TOOLS=/dls_sw/i16/software/tools

ARCH=`uname -i`
if [ "$ARCH" == "i386" ]; then
    export JAVA_HOME=$TOOLS/jdk_i586
else
    export JAVA_HOME=$TOOLS/jdk_x64
fi
export PATH=$JAVA_HOME/bin:$PATH
