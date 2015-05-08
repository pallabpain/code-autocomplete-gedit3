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
import subprocess
import Keywords

SEPARATORS = re.escape("&\"'{([-|`)]} .,;:!?/^$\n\r*+#=<>	")

class AutoCompletePlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = "AutoComplete"
	window = GObject.property(type = Gedit.Window)
	
	def __init__(self):
		GObject.Object.__init__(self)
		self.window = None
		self.working_directory = ''
		self.do_reset()
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
		''' Flag to be set for language passed in the argument.
			(For future use)'''
			
		for key in self.flags.keys():
			self.flags[key] = False
		self.flags[language] = True
	
	def do_remove_tag_file(self):
		''' Removes the intermediate tag file generated by the plugin '''
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
		''' Retrieves a list of user-defined headers from a C code
			e.g. #include "myheader.h" '''
		
		view = self.window.get_active_view()
		buffer = view.get_buffer()
		start = buffer.get_start_iter()
		end = buffer.get_end_iter()
		text = buffer.get_text(start, end, False)
		header_list = re.findall("#include\\s*\"([^\"]+)\"", text)
		return header_list
	
	def do_get_list(self):
		''' Generates tag file and returns a list comprising of tags 
			extracted from the tag file and language specific keywords. ''' 
		
		document = self.window.get_active_document()
		if (document.is_untitled()):
			return []
		doc_uri = document.get_uri_for_display()
		doc_name = document.get_short_name_for_display()
		self.working_directory = doc_uri.replace(doc_name, '')
		os.chdir(self.working_directory)
		
		cmd_start = ['ctags', '--format=1']
		cmd_middle = []
		cmd_end = ['-f', '.tags', doc_uri]
		
		if (doc_name.endswith('.c')):
			self.do_set_flag('c')
			headers = self.do_get_c_headers()
			cmd_end += headers
			cmd_middle = ['--c-kinds=+dflmpstuv']
			keyword_list = Keywords.c_list
		
		elif (doc_name.endswith('.py')):
			self.do_set_flag('python')
			cmd_middle = ['--python-kinds=+cfmvi']
			keyword_list = Keywords.python_list
		
		elif (doc_name.endswith('.rb') or doc_name.endswith('.ruby')):
			self.do_set_flag('ruby')
			cmd_middle = ['--ruby-kinds=+cfmF']
			keyword_list = Keywords.ruby_list
		
		else:
			return False
		
		command = cmd_start + cmd_middle + cmd_end
		try:
			subprocess.Popen(command)
			command = 'grep -v "!" .tags | cut -f 1 | sort | uniq'
			output = subprocess.Popen(command, stdout=subprocess.PIPE, 
										shell=True).communicate()[0]
		except Exception as e:
			return keyword_list
			
		tag_list = output.decode()
		tag_list = tag_list.split('\n')
		tag_list.pop()
		keyword_list = keyword_list + tag_list
		return keyword_list
			
	def do_reset(self):
		''' Resets variables for word completion '''
		self.loop = False
		self.words = []
		self.word_index = 0
		self.snippet_inserted = False
		self.new_iter = None
		
	def do_complete_word(self, view, event):
		''' This method is responsible for cycling through the list of
			completion words when <TAB> is pressed and displaying them'''
	
		if((event.type == Gdk.EventType.KEY_PRESS) 
					and (event.keyval == Gdk.keyval_from_name('Tab'))):
			
			buffer = view.get_buffer()
			if (not self.snippet_inserted):
				cursor_iter = buffer.get_iter_at_mark(buffer.get_insert())
			else:
				cursor_iter = self.new_iter
			line_iter = cursor_iter.copy()
			word_iter = cursor_iter.copy()
			line_iter.set_line_offset(0)
			line = buffer.get_text(line_iter, cursor_iter, False)
			
			if (not self.loop):
				match = re.search("[^%s]+$" % SEPARATORS, line)
				if (not match):
					 return False
				word = match.group()
				if (not word):
					return False
				self.line_index = cursor_iter.get_line_index() - len(word)
				word_list = self.do_get_list()
				self.words = [w for w in word_list if(w.startswith(word) 
								and (w != word))]
				self.words.sort()
				self.words.append(word)
			
			word_count = len(self.words)
			if (word_count > 1):
				if (self.loop):
					if((event.get_state() & Gdk.ModifierType.CONTROL_MASK) 
											== Gdk.ModifierType.CONTROL_MASK):
						self.word_index = (self.word_index - 1) % word_count
					else:
						self.word_index = (self.word_index + 1) % word_count
					
				word_iter.set_line_index(self.line_index)
				buffer.delete(word_iter, cursor_iter)
				buffer.insert_at_cursor(self.words[self.word_index])
				inserted_word = self.words[self.word_index]
				self.snippet_inserted = self.insert_snippet(inserted_word, buffer)
				self.loop = True
				return True
			else:
				self.do_reset()
				return False
		else:
			self.do_reset()
			return False

	def insert_snippet(self, word, buffer):
		if (self.flags['c']):
			if (word in Keywords.C_STYLES.keys()):
				buffer.insert_at_cursor(Keywords.C_STYLES[word])
				style_len = len(Keywords.C_STYLES[word])
				cursor_iter = buffer.get_iter_at_mark(buffer.get_insert())
				iter_copy = cursor_iter.copy()
				cursor_iter.backward_chars(style_len - 1)
				buffer.place_cursor(cursor_iter)
				self.new_iter = iter_copy
				return True
			else:
				return False
		elif (self.flags['python']):
			return False				
