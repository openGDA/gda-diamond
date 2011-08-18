# i18 beamline profile

export BEAMLINE=i18

if [ -r "/dls/i18/etc/gda_environment.sh" ]; then
        . "/dls/i18/etc/gda_environment.sh"
fi

PATH=/dls/i18/software/java/jdk/bin:$PATH
