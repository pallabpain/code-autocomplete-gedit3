# Code Auto-Complete Plugin for Gedit 3

The Code Auto-Complete Plug-in will allow the user to complete their
code with ease and allow faster development.

Parts of this plugin are based on the work of [Guillaume Chazarain](http://guichaz.free.fr/gedit-completion), [Elias Holzer](http://elias.hiex.at/gedit-plugins/) and a part of is based on the [Pair Character Auto Completion Plug-in] (https://code.google.com/p/gedit-pair-char-autocomplete/)

## Demonstration

![Demo 1](http://share.gifyoutube.com/vOg9jp.gif)

![Demo 2](http://share.gifyoutube.com/vbqwAq.gif)

## Requirements

The plugin requires `exuberant-ctags` to be installed on the system.

To install [Exuberant Ctags](http://ctags.sourceforge.net/) on Ubuntu, use the following command:
	
		sudo apt-get install exuberant-ctags

The plug-in was developed and tested for *Gedit 3.14*

## Installation

- Download the archive on your computer

- Extract the files.

- Open a terminal window and navigate to the extracted folder.

- Type `sh install.sh` and hit <kbd>Enter</kbd> and you're good to go.

## Usage

This plug-in allows you to use auto completion like you're used to it in any unix console. Write the first few characters of a word you've already written in your text and hit <kbd>Tab</kbd>. If there are more possibilities hit <kbd>Tab</kbd> more times to go through the results.
  
If you cycled through a few words, found the one you were looking for and want to write a tabulator, hit a key like <kbd>Shift</kbd> or <kbd>Alt</kbd> and <kbd>Tab</kbd> afterwards.

This plug-in also allows you to insert C and Python snippets in your code. Simply type the keyword e.g. *while* and press <kbd>Ctrl + Space</kbd>

Pair Character completion is also supported (e.g. ( ), { }, [ ], ' ', " ")

- <kbd>Tab</kbd> : Cycle through matches
- <kbd>Ctrl + Space</kbd> (when the cursor is at the end of a keyword) : Insert Snippet


## Languages Supported

This plug-in current supports the following languages:

- C
- Python
- Ruby

Support for more languages will be added soon along with other auto-completion features.

If there are any issues, please let me know.
