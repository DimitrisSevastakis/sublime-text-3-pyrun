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


class PyRunCommand(sublime_plugin.TextCommand):
	
	def on_done(self, index):
		if index < 0:
			return
		print("selected " + str(index) + " - " + str(list(self.python_shells.values())[index]))
		ss = self.view.settings()
		ss.set("py_target", list(self.python_shells.keys())[index])
		if self.command == "run":
			self.run(0)


	def is_python_running(self, term):
		bashCommand = "ps -o pid= -o command= -p " + term
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()
		# print ("1-"+output.decode("utf-8"))
		output = output.decode("utf-8").replace("\t", " ").split(" ")[2].replace("\n", "")
		# print ("2-"+output)
		if output == "python" or output == "python3":
			return output
		return False

	def term_exists(self, term):
		if term in self.get_term_list():
			print("terminal exists!!")
			return True
		print("terminal does not exist")
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
			# parts = re.split(r'\t+', output)
			parts = output.replace("  ", " ").split(" ")
			# print(" TERM " + term)
			# print (parts)
			if len(parts) == 3:
				is_p = self.is_python_running(parts[2])
				if is_p:
					#check if python is running
					self.python_shells[term] = [is_p, parts[2]]
					print(str([is_p, parts[2]]))


	def get_term_list(self):
		terminals = [f for f in listdir("/dev/pts/")]
		return terminals

	def select_terminal(self):
		window = sublime.active_window()
		names = []
		for name, idd in list(self.python_shells.values()):
			names.append(name)
		print(list(self.python_shells.values()))
		window.show_quick_panel(names, self.on_done)


	def num_tabs(self, stri):
		for i in range(stri):
			if stri[i]!= '\t':
				return i
		return 0

	def run(self, edit,**kwargs):
		
		self.get_py_shells()
		if(kwargs):
			self.command = kwargs['run']
			if kwargs['run'] == "select_term":
				print("selecting term")
				self.select_terminal()
				return
				
		#get selected terminal from settings
		ss = self.view.settings()
		target = ss.get("py_target")
		# print("settings target: "+ str(target))
		if(target):
			#check if terminal is running python
			if( (not self.term_exists(target))):
				if (not self.is_python_running(target[1])):
					self.select_terminal()
		else:
			# print("selecing")
			self.select_terminal()
		print ("hello")
		target = ss.get("py_target")[0]
		print("sending text to terminal " + target)
		with open("/dev/pts/" + target, 'w') as fd:
			window = sublime.active_window()
			view = window.active_view()
			sel = view.sel()
			for region in sel:
				selectionText = view.substr(region)
				print(selectionText)
				for c in selectionText:
					fcntl.ioctl(fd, termios.TIOCSTI, c)
					if c == '\n':
						time.sleep(0.05)
			
			last_region_text = view.substr(sel[-1])

			# for i in range(self.num_tabs(last_region_text.split('\n')[-1])):
			if last_region_text[-1] != '\n':
				fcntl.ioctl(fd, termios.TIOCSTI, '\n' )


		# return
		# terminals = self.get_term_list()
		
		# print(self.python_shells.values())
		# 