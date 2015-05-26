import Tkinter as Tk
import thread
import readline
import code
import sys

class console(Tk.Frame):

	def __init__(self, master, var):

		Tk.Frame.__init__(self, master)
		self.temp = sys.stderr
		self.incomplete = False
		self.ps1 = '>>> '
		self.ps2 = '... '
		self.ps = lambda x: self.ps2 if x else self.ps1
		self.master = master
		self.ttyText = Tk.Text(self, wrap='word', bg = 'black', fg = 'green', insertbackground = 'blue')
		self.ttyText.insert('end',"Simple Python Interpreter\nSpectrum Analysis Tool\nJack O'Brien 2015\n=========================\n\n")
		self.ttyText.pack(expand = 1, fill = Tk.BOTH)
		self.shell = code.InteractiveConsole(var)
		self.ttyText.bind('<Return>', self.read)
		self.ttyText.bind('<BackSpace>', self.stop)
		self.ttyText.bind('<Left>', lambda event: None)
		self.ttyText.bind('<Right>', lambda event: None)
		self.ttyText.bind('<Down>', lambda event: None)
		self.ttyText.bind('<Up>', lambda event: None)
		self.ttyText.bind('<Key>', self.on_key)

	def stop(self, event):

		self.on_key(event)
		if "".join(('\n', self.ps(self.incomplete))) == self.ttyText.get('%s-5c' % Tk.INSERT, Tk.INSERT):
			return 'break'

	def on_key(self, event):

		
		if int(float(self.ttyText.index('insert'))) != int(float(self.ttyText.index('end')))-1 or int(self.ttyText.index('insert')[self.ttyText.index('insert').find('.')+1:]) < 4: 
			self.ttyText.mark_set("insert", self.ttyText.index('end'))

	def write(self, string):

		self.ttyText.insert('end', string)
		self.ttyText.see('end')

	def read(self, event):
		self.ttyText.insert('end','\n')
		sys.stdout = self	
		sys.stderr = self
		command = self.ttyText.get('insert -1 line linestart','insert -1 line lineend')[4:]
		self.incomplete = self.shell.push(command)
		if command == '' and self.incomplete:
			if self.shell.buffer[0].strip().endswith(':'):
				self.incomplete = self.shell.push('	raise IndentationError("expected an indented block")\n')
		sys.stdout = sys.__stdout__
		sys.stderr = self.temp
		self.write(self.ps(self.incomplete))
		return 'break'
