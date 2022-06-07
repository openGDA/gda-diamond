if [[ -n "${DISPLAY:-}" && "${GDA_NO_PROMPT:-}" != true ]]; then
    if [[ "${GDA_MODE}" == "live" ]]; then
        icon_type="warning"
    else
        icon_type="question"
    fi
    RESPONSE=yes
    zenity --width 300 --title "Are you sure?" --question --text "Are you sure you want to ${GDA_OPERATION-restart} the I07 EH2 GDA server in ${GDA_MODE} mode?" --window-icon=${icon_type} || RESPONSE=no
    if [[ $RESPONSE == "no" ]]; then
        exit
    fi
else
    echo "Not restarting GDA server due to no display"
    exit
fi

ssh -x i07user@dc.diamond.ac.uk@i07-ws010 'export GDA_NO_PROMPT='"'1'"'; /dls_sw/i07/software/gda_versions/master_eh2/config/bin/gda servers'
