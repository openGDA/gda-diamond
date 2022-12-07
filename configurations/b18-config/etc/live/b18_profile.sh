# b24 beamline profile
#KrisB 17/09/14 - Commenting out $BEAMLINE as always set on beamline workstations via /etc/profile.d/beamline.sh

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

export PATH=/dls_sw/b18/software/gda/workspace_git/gda-dls-beamlines-xas.git/b18/bin:${PATH}
export GDA_MODE=live
