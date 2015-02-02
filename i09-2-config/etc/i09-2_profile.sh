# i09-1 beamline profile

export BEAMLINE=i09-2

if [ -r "/dls_sw/$BEAMLINE/software/gda/config/bin/gda_environment.sh" ]; then
        . "/dls_sw/$BEAMLINE/software/gda/config/bin/gda_environment.sh"
else

if [ -r "/dls_sw/$BEAMLINE/etc/gda_environment.sh" ]; then
        . "/dls_sw/$BEAMLINE/etc/gda_environment.sh"
fi

fi

