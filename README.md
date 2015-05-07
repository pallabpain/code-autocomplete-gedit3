# Code Auto-Complete Plugin for Gedit 3

The Code Auto-Complete Plug-in will allow the user to complete their
code with ease and allow faster development.

Parts of this plugin are based on the work of [Guillaume Chazarain](http://guichaz.free.fr/gedit-completion) 
and [Elias Holzer](http://elias.hiex.at/gedit-plugins/)

## Requirements

The plugin requires `exuberant-ctags` to be installed on the system.

To install [Exuberant Ctags](http://ctags.sourceforge.net/) on Ubuntu, use the following command:
	
		sudo apt-get install exuberant-ctags

The plug-in was developed and tested for *Gedit 3.10.4*

## Installation

- Download the files on your computer

- Copy the files `auto-complete.plugin`, `auto-complete.py` and `Keywords.py` in the following folder:

			~/.local/share/gedit/plugins/
			
`~/` denotes your home folder. The `.local` folder is hidden by default. 
You can unhide it by pressing `Ctrl + TAB`. The folder `gedit` may not 
be present by default, so, you may have to create them.

- Enable the plug-in from the gedit menu: *Edit -> Preferences -> Plugins*

## Usage

This plug-in allows you to use auto completion like you're used to it in any
unix console. Write the first few characters of a word you've already
written in your text and hit `TAB`. If there are more possibilities hit
`Tab` more times to go through the results.
 
Press `Ctrl + TAB` to iterate backwards in the case you you've gone too far.
 
If you cycled through a few words, found the one you were looking for and want
to write a tabulator, hit a key like `Shift` or `Alt` and `Tab` afterwards.

## Languages Supported

This plug-in current supports the following languages:

- C
- Python
- Ruby

Support for more languages will be added soon along with other auto-completion features.

If there are any issues, please let me know.
