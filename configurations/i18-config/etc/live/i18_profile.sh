# i18 beamline profile

# This file is sourced by i18-config/bin/gda_environment.sh

# For backwards compatibility with older GDA installations, the old profile scripts have been left in place for now.
# The current initialisation order (on beamline workstation machines only) is as follows:
#  - /etc/profile.d/gda_environment.sh is run during login
#  - which sources /dls_sw/i18/etc/i18_profile.sh
#  - which sources /dls_sw/i18/software/gda/config/bin/gda_environment.sh
#  - which sources /dls_sw/i18/software/gda/config/etc/live/i18_profile.sh (this file)

# The /dls_sw/i18/etc/i18_profile.sh file needs to be left as it was so that older GDA installations will continue to
# work. Therefore the i18-config/bin/gda_environment.sh file has to exist, but we simply use it to source this file and
# nothing more.

# A better structure to be used in future is as follows (as used on i15-1):
#  - /etc/profile.d/gda_environment.sh is run during login
#  - which sources /dls_sw/i18/etc/i18_profile.sh
#  - which is actually a symlink to /dls_sw/i18/software/gda/config/etc/live/i18_profile.sh (this file)

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

# Set up path and mode
export PATH=/dls_sw/$BEAMLINE/software/gda/workspace_git/gda-diamond.git/configurations/i18-config/bin:${PATH}
export GDA_MODE=live

# Set up command completion for the gda command
if [[ $(command -v gda >/dev/null) ]]; then
    source <(gda completions bash)
fi
