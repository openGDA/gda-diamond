#i07 beamline profile

export BEAMLINE=i07

if [ -f "/etc/profile.d/modules.sh" ]; then
    . /etc/profile.d/modules.sh
fi

if [ -r "/dls_sw/$BEAMLINE/etc/gda_environment.sh" ]; then
        . "/dls_sw/$BEAMLINE/etc/gda_environment.sh"
fi

if [ -r "/dls/$BEAMLINE/bin/i07_setup.sh" ]; then
        . "/dls/$BEAMLINE/bin/i07_setup.sh" >& /dev/null
fi
