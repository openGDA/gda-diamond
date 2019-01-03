# i11 beamline profile

export BEAMLINE=i11

if [ -r "/dls_sw/$BEAMLINE/software/gda/config/bin/gda_environment.sh" ]; then
        . "/dls_sw/$BEAMLINE/software/gda/config/bin/gda_environment.sh"
else

if [ -r "/dls_sw/$BEAMLINE/etc/gda_environment.sh" ]; then
        . "/dls_sw/$BEAMLINE/etc/gda_environment.sh"
fi

fi

if [ -r "/dls_sw/$BEAMLINE/software/gda/config/bin/detector_environment.sh" ]; then
        . "/dls_sw/$BEAMLINE/software/gda/config/bin/detector_environment.sh"
else

if [ -r "/dls_sw/$BEAMLINE/etc/detector_environment.sh" ]; then
        . "/dls_sw/$BEAMLINE/etc/detector_environment.sh"
fi

fi
