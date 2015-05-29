#!/bin/sh
#
# Installs the plugin to the users plugin folder

PLUGINS_FOLDER=~/.local/share/gedit/plugins

install_file() {
	echo " - adding $1 to $PLUGINS_FOLDER"
	cp "$1" "$PLUGINS_FOLDER" || exit 1
}

# Install plugin
echo "\nInstalling Code Auto Complete plug-in for Gedit 3"
mkdir -p $PLUGINS_FOLDER
install_file 'auto-complete.plugin'
install_file 'auto-complete.py'
install_file 'helper.py'


echo '\n*** Restart gedit and enable plug-in from Preferences -> Plugins ***\n'

