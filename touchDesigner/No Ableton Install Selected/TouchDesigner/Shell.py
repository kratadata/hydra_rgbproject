# Console.py

import sys
import code
from contextlib import contextmanager

PY3 = sys.version_info[0] >= 3
if PY3:
	from io import StringIO
	from . import OSC3 as OSC
else:
	from cStringIO import StringIO
	from . import OSC

import Live

class Shell:
	"""
	Shell simulates a Python shell, giving direct access to the Live API
	"""
	
	def __init__(self, tda, client):
		self.stdout = StringIO()
		self.stderr = StringIO()
		
		self.tda = tda
		self.client = client
		self.debug = self.tda.debug
		self.context = client.context

		self.interpreter = code.InteractiveConsole(self.context)
			
	def pushLine(self, cmd):
		"""
		Incoming console line
		"""
		old_out, sys.stdout = sys.stdout, self.stdout 
		old_err, sys.stderr = sys.stderr, self.stderr
		continues = self.interpreter.push(cmd)
		if continues:
			self.client.send(OSC.OSCMessage('/shell/reply',[1, '', '']))
		else:
			self.client.send(OSC.OSCMessage('/shell/reply',[0,
			                                    self.stdout.getvalue(),
												self.stderr.getvalue()]))
		sys.stdout = old_out
		sys.stderr = old_err
		self.stdout = StringIO()
		self.stderr = StringIO()

	def runCode(self, codeString):
		"""
		Run the provided codeString.
		Returns (stdout, stderr)
		"""
		old_out, sys.stdout = sys.stdout, self.stdout
		old_err, sys.stderr = sys.stderr, self.stderr
		self.interpreter.runcode(codeString)
		retVal = (self.stdout.getvalue(), self.stderr.getvalue())
		sys.stdout = old_out
		sys.stderr = old_err
		self.stdout = StringIO()
		self.stderr = StringIO()
		if retVal[1]:
			raise Exception(retVal[1])
		return retVal

	def requestData(self, requestInfo):
		"""
		Send data back via OSC
		:param requestInfo: (codeString, asRepr, id)
		"""
		old_out, sys.stdout = sys.stdout, self.stdout
		old_err, sys.stderr = sys.stderr, self.stderr
		self.interpreter.runcode("__retVal__ = " + requestInfo[0])
		error = self.stderr.getvalue()
		sys.stdout = old_out
		sys.stderr = old_err
		self.stdout = StringIO()
		self.stderr = StringIO()
		if error:
			raise Exception(error)
		retVal = self.interpreter.locals['__retVal__']
		if requestInfo[1]:
			retVal = repr(retVal)
		self.client.send(OSC.OSCMessage('/shell/data',
										[requestInfo[2], retVal]))