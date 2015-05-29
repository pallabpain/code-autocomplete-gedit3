from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gedit
from gi.repository import GObject

import os
import re
import subprocess
import helper

separators = re.escape("&\"'{([-|`)]} .,;:!?/^$\n\r*+#=<>	")
supported_langs = ('python', 'c', 'ruby')
opening = ('(', '{', '[', "'", '"')
closing = (')', '}', ']', "'", '"')
keywords_map = {
	'c' : helper.c_list,
	'python' : helper.python_list,
	'ruby' : helper.ruby_list
}

def keypress_to_char(keypress):
	if isinstance(keypress, str):
		return keypress
	return chr(keypress) if 0 < keypress < 128 else None
	
class AutoCompletePlugin(GObject.Object, Gedit.WindowActivatable):
	
	ViewHandler = 'auto_complete_handler'
	window = GObject.property(type=Gedit.Window)
	
	def __init__(self):
		GObject.Object.__init__(self)
		self.language_id = 'none'
		self.do_reset()
	
	def do_activate(self):
		self.do_update_state()
		
	def do_deactivate(self):
		for view in self.window.get_views():
			 handler_id = getattr(view, self.ViewHandler, None)
			 if handler_id != None:
			 	view.disconnect(handler_id)
			 setattr(view, self.ViewHandler, None)
	
	def do_update_state(self):
		self.update_ui()
		
	def update_ui(self):
		view = self.window.get_active_view()
		document = self.window.get_active_document()
		if isinstance(view, Gedit.View) and document:
			if getattr(view, self.ViewHandler, None) is None:
				handler_id = view.connect('key-press-event', 
								self.on_key_press, document)
				setattr(view, self.ViewHandler, handler_id)
	
	def pressed_enter(self, event):
		# Returns True if Enter is pressed
		return event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter)
			
	def pressed_ctrl_space(self, event):
		# Returns True if Ctrl + Space are pressed
		return (event.keyval == Gdk.KEY_space and
			event.get_state() & Gdk.ModifierType.CONTROL_MASK)
			
	def pressed_tab(self, event):
		# Returns True if Tab is pressed
		return (event.keyval == Gdk.KEY_Tab)
	
	def is_language_supported(self, doc):
		# Returns True if language is supported by plug-in
		language = doc.get_language()
		lang_id = language.get_id() if language is not None else 'none'
		self.language_id = lang_id
		return lang_id in supported_langs		
	
	def get_line_indent(self, doc):
		# Returns indentation of the current line
		start = doc.get_iter_at_mark(doc.get_insert())
		start.set_line_offset(0)
		mark = start.copy()
		end = start.copy()
		end.forward_to_line_end()
		ch = mark.get_char()
		while ch.isspace():
			if mark.compare(end) < 0:
				mark.forward_char()
				ch = mark.get_char()
		indentation = start.get_slice(mark)
		return indentation
	
	def	is_opening(self, char):
		# Returns True if char belongs to the tuple opening
		return char in opening
	
	def is_closing(self, char):
		# Returns True if char belongs to the tuple closing
		return char in closing
	
	def get_matching_opening(self, closer):
		# Returns matching opening character
		return opening[closing.index(closer)]
		
	def get_matching_closing(self, opener):
		# Return matching closing character
		return closing[opening.index(opener)]
	
	def char_under_cursor(self, doc):
		# Returns the character under(or after) the cursor
		itr = doc.get_iter_at_mark(doc.get_insert())
		return itr.get_char()
	
	def forward_cursor(self, doc):
		# Moves cursor forward by one position
		doc.begin_user_action()
		itr = doc.get_iter_at_mark(doc.get_insert())
		itr.forward_char()
		doc.place_cursor(itr)
		doc.end_user_action()
		return True
	
	def check_balance(self, doc, closer):
		# Checks the balance between opening and closing characters
		itr = doc.get_iter_at_mark(doc.get_insert())
		opener = self.get_matching_opening(closer)
		balance = 1
		while balance != 0 and not itr.is_start():
			itr.backward_char()
			if itr.get_char() == opener:
				balance -= 1
			elif itr.get_char() == closer:
				balance += 1
		return balance == 0
	
	def auto_close_paren(self, doc, opener):
		# Auto completes opening character with a closing character
		closer = self.get_matching_closing(opener)
		doc.begin_user_action()
		doc.insert_at_cursor(opener + closer)
		itr = doc.get_iter_at_mark(doc.get_insert())
		itr.backward_char()
		doc.place_cursor(itr)
		doc.end_user_action()
		return True
		
	def insert_with_indent(self, doc, indent):
		# Inserts new lines with proper indentation
		text = '\n' + indent
		doc.begin_user_action()
		itr = doc.get_iter_at_mark(doc.get_insert())
		doc.place_cursor(itr)
		doc.insert_at_cursor(text)
		doc.insert_at_cursor(text)
		itr = doc.get_iter_at_mark(doc.get_insert())
		itr.backward_chars(len(text))
		doc.place_cursor(itr)
		doc.insert_at_cursor('\t')
		itr = doc.get_iter_at_mark(doc.get_insert())
		doc.place_cursor(itr)
		doc.end_user_action()
		return True
	
	def delete_parens(self, doc):
		# Deletes matching opening and closing characters
		doc.begin_user_action()
		start = doc.get_iter_at_mark(doc.get_insert())
		end = start.copy()
		start.backward_char()
		end.forward_char()
		doc.delete(start, end)
		doc.end_user_action()
		return True
	
	def should_delete_both_parens(self, doc, event):
		# Checks whether opening and closing characters should be deleted.
		if event.keyval == Gdk.KEY_BackSpace:
			itr = doc.get_iter_at_mark(doc.get_insert())
			current_char = itr.get_char()
			if self.is_closing(current_char):
				itr.backward_char()
				previous_char = itr.get_char()
				matching_paren = self.get_matching_opening(current_char)
				return previous_char == matching_paren
		return False

	def insert_snippet(self, doc):
		# Insert appropriate snippet
		if self.language_id == 'c':
			styles = helper.C_STYLES
		if self.language_id == 'python':
			styles = helper.PY_STYLES
		itr = doc.get_iter_at_mark(doc.get_insert())
		word = self.extract_word_before_cursor(doc)
		if word in styles.keys():
			snippet = styles[word]
		else:
			return False
		doc.begin_user_action()
		doc.place_cursor(itr)
		if snippet[2]:
			indent = self.get_line_indent(doc)
			text = snippet[0] + '\n\n' + indent + snippet[1]
		else:
			text = snippet[0] + snippet[1]
		doc.insert_at_cursor(text)
		itr = doc.get_iter_at_mark(doc.get_insert())
		itr.backward_chars(len(text))
		itr.forward_char()
		doc.place_cursor(itr)
		doc.end_user_action()
		return True
		
	def extract_word_before_cursor(self, doc):
		# Extracts the word before the cursor
		end = doc.get_iter_at_mark(doc.get_insert())
		start = end.copy()
		while start.backward_char():
			char = start.get_char()
			if not char.isalpha():
				start.forward_char()
				break
		word = doc.get_text(start, end, False)
		return word
		
	def pair_completion(self, doc, event):
		# Completes opening-closing charcter pairs
		handled = False
		# Perform pair completion
		ch = keypress_to_char(event.keyval)
		if self.is_closing(ch):
			# Skip over closing paren if balance 
			# of parens is maintained
			if self.char_under_cursor(doc) == ch and self.check_balance(doc, ch):
				handled = self.forward_cursor(doc)		
		if not handled and self.is_opening(ch):
			# Insert matching closing paren
			handled = self.auto_close_paren(doc, ch)	
		if not handled and self.pressed_enter(event):
			char = self.char_under_cursor(doc)
			if self.is_closing(char) and self.check_balance(doc, char):
				indent = self.get_line_indent(doc)
				handled = self.insert_with_indent(doc, indent)
		if not handled and self.should_delete_both_parens(doc, event):
			handled = self.delete_parens(doc) 
		
		return handled

	def do_reset(self):
		# Resets variables for word completion
		self.loop = False
		self.words = []
		self.word_index = 0

	def word_completion(self, doc, event):	
		# This method completes the words	
		cursor_iter = doc.get_iter_at_mark(doc.get_insert())
		line_iter = cursor_iter.copy()
		word_iter = cursor_iter.copy()
		line_iter.set_line_offset(0)
		line = doc.get_text(line_iter, cursor_iter, False)
		if not self.loop:
			# Find the partially completed word before the cursor
			match = re.search("[^%s]+$" % separators, line)
			if not match:
				return False
			partial_word = match.group()
			if not partial_word:
				return False
			self.line_index = cursor_iter.get_line_index() - len(partial_word)
			kwords = keywords_map[self.language_id]
			keywords = []
			for keyword in kwords:
				keywords.append([keyword, 'keyword', ''])
			del(kwords)
			taglist = self.get_tag_list(doc)
			self.words = keywords + taglist
			self.words = [word for word in self.words if(word[0].startswith(partial_word) and word[0] != partial_word)]
			self.words.sort()
			self.words.append([partial_word, 'w', ''])
		
		word_count = len(self.words)
		if word_count > 1:
			if self.loop:
				self.word_index = (self.word_index + 1) % word_count
			word_iter.set_line_index(self.line_index)
			doc.delete(word_iter, cursor_iter)
			doc.insert_at_cursor(self.words[self.word_index][0])
			inserted_word = self.words[self.word_index]
			self.insert_function_skeleton(inserted_word, doc)
			self.loop = True
			return True
		else:
			self.do_reset()
			return False
			
	def insert_function_skeleton(self, word, doc):
		kind = word[1]
		desc = word[2]
		def get_skeleton(desc):
			comma_count = desc.count(',')
			text = '('
			for i in range(comma_count):
				text += ' ,'
			text += ' )'
			if comma_count == 0:
				text = '()'
			return text
		if self.language_id in ('python', 'ruby') and kind == 'm':
			text_to_insert = get_skeleton(desc)
			doc.insert_at_cursor(text_to_insert)
			return True
		if self.language_id in ('c', 'python') and kind == 'f':
			text_to_insert = get_skeleton(desc)
			doc.insert_at_cursor(text_to_insert)
			return True
		return False
			
			
	def on_key_press(self, view, event, doc):
		# All the key press events are handled here
		if not self.is_language_supported(doc):
			# Return False if the file is not supported by the plug-in
			return False
		if self.pressed_tab(event):
			# Performs word completion
			return self.word_completion(doc, event)
		elif self.pressed_ctrl_space(event):
			# Perform snippet insertion
			self.do_reset()
			return self.insert_snippet(doc)
		else:
			# Opening-closing pair completion
			self.do_reset()
			return self.pair_completion(doc, event)
					
	def get_tag_list(self, doc):
		# Uses CTAGS to create tag file. The reads the tag
		# file to retrieve the list of all the tags.
		uri = doc.get_uri_for_display()
		name = doc.get_short_name_for_display()
		path = uri.replace(name, '')
		os.chdir(path)
		tag_list = []
		cmd_start = ['ctags', '--fields=k'] 
		cmd_mid = []
		cmd_end = ['-f', '.tags', uri]
		
		if (self.language_id == 'c'):
			cmd_mid = ['--c-kinds=+defglnmstuv']
			cmd_end += self.get_headers_for_c_file(doc)
		elif (self.language_id == 'python'):
			cmd_mid = ['--python-kinds=+cfmvi']
		elif (self.language_id == 'ruby'):
			cmd_mid = ['--ruby-kinds=+cfmF']
		else:
			return []
		command = cmd_start + cmd_mid + cmd_end
		try:
			# Creates the tag file
			subprocess.Popen(command)
			# Command for reading the tag file and extracting tags
			command = 'grep -v "!" .tags | cut --complement -f 2 | sort | uniq'
			output = subprocess.Popen(command, stdout=subprocess.PIPE, 
												shell=True).communicate()[0]
			temp_list = output.decode()
			temp_list = temp_list.split('\n')	
			temp_list.pop()
			temp_list = [item.split('\t') for item in temp_list]
			# Formatting tag information to get 
			# [tag-name, tag-kind, tag-description]
			for item in temp_list:
				tag_list.append([item[0], item[-1], 
								''.join(item[1: len(item) - 1])])
			del(temp_list)
		except Exception as e:
			return []
		return tag_list
		
	def get_headers_for_c_file(self, doc):
		# Returns a list of user headers in a C code
		begin = doc.get_start_iter()
		end = doc.get_end_iter()		
		text = doc.get_text(begin, end, False)
		header_list = re.findall("#include\\s*\"([^\"]+)\"", text)
		return header_list
				

