#!/bin/sh
# Remove GDA Launchers from user's Desktop on user logout
# to be copied to .logout at user's $HOME on user login 
# to be run on user logout
#
if [ -h "$HOME/Desktop/GDA_Launchers" ]; then
	rm -f $HOME/Desktop/GDA_Launchers
fi

##For the screen grabber to eLog:
panel="top_panel"
position="1"
right_stick="true"
#launcher_path="/usr/share/applications/gnome-terminal.desktop"
launcher_path="/dls_sw/i06-1/software/gda/config/Desktop/grab2log.desktop"
launcher_id="grab2elog_launcher"

# Apply the schemas
for schema in $(gconftool-2 --all-entries /schemas/apps/panel/objects | awk -F '=' '{print $1}'); do
    gconftool-2 --apply-schema /schemas/apps/panel/objects/$schema /apps/panel/objects/$launcher_id/$schema
done

# Tweak things
gconftool-2 --set /apps/panel/objects/$launcher_id/object_type -t string launcher-object
gconftool-2 --set /apps/panel/objects/$launcher_id/launcher_location -t string $launcher_path
gconftool-2 --set /apps/panel/objects/$launcher_id/toplevel_id -t string $panel
gconftool-2 --set /apps/panel/objects/$launcher_id/position -t int $position
gconftool-2 --set /apps/panel/objects/$launcher_id/panel_right_stick -t bool $right_stick 

object_id_list=$(gconftool-2 --get /apps/panel/general/object_id_list | sed -e "s|]|, $launcher_id]|" )


#To remove the screen grabber
object_id_list=$(gconftool-2 --get /apps/panel/general/object_id_list | sed -e 's/\(,grab2elog_launcher\)//g')
gconftool-2 --set /apps/panel/general/object_id_list --type list --list-type string $object_id_list
gconftool-2 --recursive-unset /apps/panel/objects/$launcher_id

