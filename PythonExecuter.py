import sublime_plugin
import sublime
from os import listdir
from os.path import isfile, join
import subprocess
import re
import fcntl
import time
import termios
import json
import array
import struct


class PyRunCommand(sublime_plugin.TextCommand):
	
	def on_done(self, index):
		if index < 0:
			return
		print("selected " + str(index) + " - " + str(list(self.python_shells.values())[index]))
		ss = self.view.settings()
		ss.set("py_target", list(self.python_shells.keys())[index])
		if self.command and self.command == "run":
			self.run(0)


	def is_python_running(self, term):
		bashCommand = "ps -o pid= -o command= -p " + term
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()
		output = output.decode("utf-8").replace("\t", " ").split(" ")[1].replace("\n", "")
		if output == "python" or output == "python3":
			return output
		return False


	def get_py_shells(self):
		self.python_shells = {}
		terminals = [f for f in listdir("/dev/pts/")]
		terminals.remove("ptmx")
		for term in terminals:
			#check if process is running on terminal
			bashCommand = "fuser /dev/pts/" + term
			process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
			output, error = process.communicate()
			output = output.decode("utf-8")
			parts = output.replace("  ", " ").split(" ")
			if len(parts) == 3:
				is_p = self.is_python_running(parts[2])
				if is_p:
					#check if python is running
					self.python_shells[term] = [is_p, parts[2]]
					print(str([is_p, parts[2]]))


	def select_terminal(self):
		window = sublime.active_window()
		names = []
		for name, idd in list(self.python_shells.values()):
			names.append(name)
		print(list(self.python_shells.values()))
		window.show_quick_panel(names, self.on_done)


	def write_to_console(self, text, target):
		with open("/dev/pts/" + target, 'w') as fd:
			for c in text:
				fcntl.ioctl(fd, termios.TIOCSTI, c)
				if c == '\n':
					time.sleep(0.05)
			if text[-1] != '\n':
				fcntl.ioctl(fd, termios.TIOCSTI, '\n' )


	def run(self, edit,**kwargs):
		window = sublime.active_window()
		view = window.active_view()
		self.get_py_shells()
		if(kwargs):
			self.command = kwargs['run']
			if kwargs['run'] == "select_term":
				self.select_terminal()
				return	
		#get selected terminal from settings
		ss = self.view.settings()
		target = ss.get("py_target")
		if(target):
			#check if target terminal is running python
			if( (not target in [f for f in listdir("/dev/pts/")])):
				if (not self.is_python_running(target[1])):
					self.select_terminal()
		else:
			self.select_terminal()
		
		#get target terminal from settings
		target = ss.get("py_target")[0]
		#get selected region
		sel = view.sel()
		total_text = []
		#if only one cursor exists with no selection
		#execute the line where the cursor is
		if len(sel) == 1 and view.substr(sel[0]) == "":
			#if only one cursor exists with no selection
			#execute the line where the cursor is
			line = view.line(sel[0])
			total_text = view.substr(line)
		else:
			#concatenate all selected regions as text
			for region in sel:
				total_text += view.substr(region)
			total_text = "".join(total_text)

		self.write_to_console(total_text, target)
		