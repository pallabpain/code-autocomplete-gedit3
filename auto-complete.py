# Copyright (C) 2015 - Pallab Pain <pallabkumarpain@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Parts of this plugin are based on the work of Guillaume Chazarain
# (http://guichaz.free.fr/gedit-completion) and Elias Holzer
# (http://elias.hiex.at/gedit-plugins/)

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gedit
from gi.repository import GObject

import os
import re
import helper
import subprocess

SEPARATORS = re.escape("&\"'{([-|`)]} .,;:!?/^$\n\r*+#=<>	")

KEY_PAIRS = { 	Gdk.KEY_parenleft :  Gdk.KEY_parenright,
				Gdk.KEY_bracketleft : Gdk.KEY_bracketright,
			 	Gdk.KEY_braceleft : Gdk.KEY_braceright, 
			 	Gdk.KEY_quotedbl : Gdk.KEY_quotedbl,
			 	Gdk.KEY_quoteright : Gdk.KEY_quoteright
			}

KEY_ASCII = { 	Gdk.KEY_parenright : ')',
			  	Gdk.KEY_braceright : '}',
			  	Gdk.KEY_bracketright : ']',
			  	Gdk.KEY_quotedbl : '"',
			  	Gdk.KEY_quoteright : "'"
			}
			
class AutoCompletePlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = "AutoComplete"
	window = GObject.property(type = Gedit.Window)
	
	def __init__(self):
		GObject.Object.__init__(self)
		self.window = None
		self.working_directory = '' # Stores the path of the current working directory
		self.do_reset() # Resets the values related to word completion   
		self.flags = {'python' : False, 'c' : False, 'ruby' : False}   
	
	def do_activate(self):
		handler_ids = []
		for signal in ('tab-added', 'tab-removed'):
			method = getattr(self, 'on_window_' + signal.replace('-', '_'))
			handler_ids.append(self.window.connect(signal, method))
			self.window.AutoCompleteID = handler_ids
			
		for view in self.window.get_views():
			self.connect_view(view)
	
	def do_deactivate(self):
		widgets = [self.window] + self.window.get_views()
		for widget in widgets:
			handler_ids = widget.AutoCompleteID
			if not handler_ids is None:
				 for handler_id in handler_ids:
				 	widget.disconnect(handler_id)
			widget.AutoCompleteID = None
			self.do_remove_tag_file()
			self.window = None
	
	def connect_view(self, view):
		handler_id = view.connect('key-press-event', self.do_complete_word)
		view.AutoCompleteID = [handler_id]
		
	def on_window_tab_added(self, window, tab):
		self.connect_view(tab.get_view())
	
	def on_window_tab_removed(self, window, tab):
		pass
		
	def do_set_flag(self, language):
		for key in self.flags.keys():
			self.flags[key] = False
		self.flags[language] = True
	
	def do_remove_tag_file(self):
		# Removes the intermediate tag file generated by the plugin
		if (self.working_directory != ''):
			os.chdir(self.working_directory)
			if (os.access('.tags', os.F_OK)):
				command = ['rm', '.tags']
				if ((os.getuid() == 0) and (os.environ.has_key('SUDO_USER'))):
					command = ['sudo', '-u', os.environ['SUDO_USER']] + command
				subprocess.Popen(command)
		else: 
			return
			
	def do_get_c_headers(self):
		# Retrieves a list of user-defined headers from a C code
		# e.g. #include "myheader.h" '''
		
		view = self.window.get_active_view()
		buffer = view.get_buffer()
		start = buffer.get_start_iter()
		end = buffer.get_end_iter()
		text = buffer.get_text(start, end, False)
		header_list = re.findall("#include\\s*\"([^\"]+)\"", text)
		return header_list
	
	def do_get_list(self, doc_uri):
		#Generates tag file and returns a list comprising of tags 
		# extracted from the tag file and language specific keywords.

		# Change current working direcotry
		os.chdir(self.working_directory)	
		
		cmd_start = ['ctags', '--fields=k']
		cmd_mid = []
		cmd_end = ['-f', '.tags', doc_uri]
			
		if (self.flags['c']):
			headers = self.do_get_c_headers()
			cmd_mid = ['--c-kinds=+defglnmstuv']
			cmd_end += headers
		elif (self.flags['python']):
			cmd_mid = ['--python-kinds=+cfmvi']
		elif (self.flags['ruby']):
			cmd_mid = ['--ruby-kinds=+cfmF']
		else:
			return []
		
		command = cmd_start + cmd_mid + cmd_end
		final_list = [] # Will store the final formatted tag list
		try:
			subprocess.Popen(command)
			# Create tag file using ctags for the current file
			command = 'grep -v "!" .tags | cut --complement -f 2 | sort | uniq'
			output = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
			tag_list = output.decode()
			tag_list = tag_list.split('\n')
			tag_list.pop()
			tag_list = [tag.split('\t') for tag in tag_list]
			#Generate list in the format [[tag-name, tag-kind, tag-definition]]
			for item in tag_list:
				final_list.append([item[0], item[-1], ''.join(item[1: len(item) - 1])])
			del(tag_list) # Delete the tag_list object
		except Exception as e:
			return []
		# Return the formatted list
		return final_list
			
	def do_reset(self):
		# Resets variables for word completion
		self.loop = False 	# For looping through matches
		self.words = [] 	# Stored list of matches
		self.word_index = 0	# Counter for iterating through matches
		self.snippet_inserted = False # Flag to check if a snippet has been inserted
		self.new_iter = None 
		self.line_changed = None # Tells if the line was changed while inserting a snippet
		
	def do_complete_word(self, view, event):
		# This method is responsible for cycling through the list of
		# completion words when <TAB> is pressed and displaying them
		
		document = self.window.get_active_document() # Get the active document
		if (document.is_untitled()): # If the document is untitled then exit
			return False
		doc_uri = document.get_uri_for_display() # Get the URI of the document
		doc_name = document.get_short_name_for_display() # Get the name of the document e.g. sample.c or sample.py
		self.working_directory = doc_uri.replace(doc_name, '') # Remove name of document from the URI
		
		if doc_name.endswith('.c'):
			self.do_set_flag('c') # Current file is a C file
		elif doc_name.endswith('.py'):
			self.do_set_flag('python') # Current file is a Python file
		elif doc_name.endswith('.rb') or doc_name.endswith('.ruby') :
			self.do_set_flag('ruby') # Current file is a Ruby file
		else:
			return False # Language not supported
		
		if((event.type == Gdk.EventType.KEY_PRESS) and (event.keyval == Gdk.keyval_from_name('Tab'))):
			
			buffer = view.get_buffer() # Get the text buffer for the current view
			
			if (not self.snippet_inserted):
				# Get TextIter at the current cursor location
				# if a snippet wasn't inserted in the previous KEY_PRESS event
				cursor_iter = buffer.get_iter_at_mark(buffer.get_insert())
			else:
				cursor_iter = self.new_iter
			
			line_iter = cursor_iter.copy()
			
			if (self.line_changed != None):
				word_iter = self.line_changed
			else:
				word_iter = cursor_iter.copy()
			
			line_iter.set_line_offset(0)
			line = buffer.get_text(line_iter, cursor_iter, False)
			
			# When the user is pressing TAB for the first time after typing something
			if (not self.loop): 
				# Get the partially typed word before the cursor
				match = re.search("[^%s]+$" % SEPARATORS, line)
				if (not match):
					 return False
				word = match.group()
				if (not word):
					return False
				
				# Get index at the beginning of the selected word
				self.line_index = cursor_iter.get_line_index() - len(word)
				
				# Get keyword list from helper module
				if (self.flags['c']):
					k_list = helper.c_list
				elif (self.flags['python']):
					k_list = helper.python_list
				elif (self.flags['ruby']):
					k_list = helper.ruby_list
				
				tag_list = self.do_get_list(doc_uri)
				keywords = [] 	
				# Convert keyword list into tag list's format
				for keyword in k_list:
					keywords.append([keyword, 'k', ''])
					
				self.words = keywords + tag_list
				# Find suitable matches from the list
				self.words = [w for w in self.words if(w[0].startswith(word) and w != word)]
				self.words.sort()
				# Finally append the partially completed word to the list
				self.words.append([word, 'w', ''])
			
			word_count = len(self.words)
			
			if (word_count > 1):
				if (self.loop):
					if((event.get_state() & Gdk.ModifierType.CONTROL_MASK) == Gdk.ModifierType.CONTROL_MASK):
						# When Ctrl + TAB is pressed
						self.word_index = (self.word_index - 1) % word_count
					else:
						# When TAB is pressed
						self.word_index = (self.word_index + 1) % word_count
				
				word_iter.set_line_index(self.line_index) # Take iter to start of the word in the buffer
				buffer.delete(word_iter, cursor_iter) # Delete that word
				buffer.insert_at_cursor(self.words[self.word_index][0]) # Insert word from list into the buffer
				inserted_word = self.words[self.word_index]
				# Insert snippet (if possible)
				self.snippet_inserted = self.insert_snippet(inserted_word, buffer)
				self.loop = True
				return True
			
			else:
				# If the list has no words in it
				self.do_reset()
				return False
		
		elif (event.type == Gdk.EventType.KEY_PRESS):
			# If a key other than Tab is pressed
			self.do_reset()
			buffer = view.get_buffer()
			
			if (event.keyval in KEY_PAIRS):
				# If [, {, (, " or ' is pressed then
				# complete the pair
				pair_char = KEY_ASCII[KEY_PAIRS[event.keyval]]
				buffer.insert_at_cursor(pair_char)
				cursor_iter = buffer.get_iter_at_mark(buffer.get_insert())
				cursor_iter.backward_chars(1)
				buffer.place_cursor(cursor_iter)
				
			return False

	def insert_snippet(self, word, buffer):
		# Inserts code-snippets
		if (self.flags['c'] and word[0] in helper.C_STYLES.keys()):
			cursor_iter = buffer.get_iter_at_mark(buffer.get_insert())
			line_number = cursor_iter.get_line()
			spaces = self.get_indent(buffer, cursor_iter)
			buffer.insert_at_cursor(helper.C_STYLES[word[0]][0])
			buffer.insert_at_cursor('\n\n' + spaces + helper.C_STYLES[word[0]][1])
			cursor_iter = buffer.get_iter_at_mark(buffer.get_insert())
			iter_copy = cursor_iter.copy()
			cursor_iter.set_line(line_number)
			self.line_changed = cursor_iter
			cursor_iter.forward_to_line_end()
			cursor_iter.backward_chars(len(helper.C_STYLES[word[0]][0]) - 1)
			buffer.place_cursor(cursor_iter)
			self.new_iter = iter_copy
			return True
		
		elif (word[1] == 'f'):
			# If a function is found in the tags
			comma_count = word[2].count(',')
			snippet_text = '('
			for i in range(comma_count):
				snippet_text += ' ,'
			snippet_text += ' )'
			if (comma_count == 0):
				snippet_text = '()'
			
			buffer.insert_at_cursor(snippet_text)
			style_len = len(snippet_text)
			cursor_iter = buffer.get_iter_at_mark(buffer.get_insert())
			iter_copy = cursor_iter.copy()
			cursor_iter.backward_chars(style_len - 1)
			buffer.place_cursor(cursor_iter)
			self.new_iter = iter_copy
			self.line_changed = None
			return True
		
		else:
			self.line_changed = None
			return False
	
	def get_indent(self, buffer, cursor_iter):
		# Computes line indentation
		line_iter = cursor_iter.copy()
		line_iter.set_line_offset(0)
		start = line_iter.copy()
		ch = line_iter.get_char()
		while (ch.isspace()):
			line_iter.forward_char()
			ch = line_iter.get_char()
		s = start.get_slice(line_iter)
		return s
			
				
