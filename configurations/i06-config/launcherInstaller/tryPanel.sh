#!/bin/bash

# You can modify these to suit
panel="top_panel"
position="1"
right_stick="true"
#launcher_path="/usr/share/applications/gnome-terminal.desktop"
launcher_path="/dls_sw/i06-1/software/gda/config/Desktop/grab2log.desktop"
launcher_id="foo_launcher"

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
echo $object_id_list

# Finally, add the applet once everything has been setup
gconftool-2 --set /apps/panel/general/object_id_list --type list --list-type string $object_id_list

