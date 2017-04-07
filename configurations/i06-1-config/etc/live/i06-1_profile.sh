# i06-1 beamline profile

GDA_ROOT_DIR=$(readlink -f /dls_sw/$BEAMLINE/software/gda)
if [[ $GDA_ROOT_DIR == *"8.38"* ]]; then
	. /dls_sw/i06-1/software/gda/workspace_git/gda-mt.git/configurations/i06-config/bin/gda_environment.sh
else
	# Set up path and mode
	export PATH=/dls_sw/prod/etc/Launcher:/dls_sw/$BEAMLINE/software/gda/config/bin:${PATH}
	export GDA_MODE=live

	# Set up command completion for the gda command
	source /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-core.git/core-config/bin/gda_core_completion
fi	