# runs the servers locally
source /dls_sw/dasc/tools_versions/set_tools.sh
umask 0002
# --trace could be useful!
/dls_sw/i20-1/software/gda_versions/gda_trunk_8_19/plugins/uk.ac.gda.core/bin/gda --config=/dls_sw/i20-1/software/gda/i20-1-config --mode=live --use-tp --debug -p 8001 --restart servers