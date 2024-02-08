# Listeners.py

import sys
# TEST
PY3 = sys.version_info[0] >= 3
if PY3:
	from .OSC3 import OSCMessage
else:
	from .OSC import OSCMessage

from datetime import datetime

import Live

def ptrStr(ptr):
	ptrString = str(ptr)
	return ptrString[:-1] if ptrString.endswith('L') else ptrString

SPECIALLISTENERS = ['*BeatTime', '*MIDINotes', '*Selection']

class Listeners:
	"""
	Watch Registry tracks and optimizes Live object watch requests
	"""

	# region Init

	def __init__(self, client):
		self.client = client
		self.codeContext = client.context
		self.registry = {} # (lomExpression, property, returnAddress):
							# {'registrants': set(requesterID),
							#	'callback': callback,
							#	'setterIndex': setterIndex,
							# 	'liveObject': lomExpression result
							# }
		self.setters = []
		self.selectionListenerRemovers = [] # used by *Selection mode
		self.debug = self.codeContext['TDA'].debug

	@property
	def debugging(self):
		return self.codeContext['TDA'].debugging

	def add(self, lomExpression, property, returnAddress, id, extra=''):
		"""
		Add an item to the registry
		Set up listener callback
		:param lomExpression: Python expression to reach Live object, e.g.:
									'SONG.tracks[1].devices[3].parameters[2]'
		:param property: property of object that has watcher, e.g.: 'Value'
		:param returnAddress: OSC address to send updates to. "" = no return
		:param id: unique ID of watcher
		:param extra: an extra string with instructions.
				'noinit' = don't send initial value message
				'str_for_value' = add a str_for_value listener if available
					(return address for it is returnAddress + '/str')
		"""

		# trying to make this as fast as possible because it will probably get
		# called many times per frame
		# self.debug('add', lomExpression, property, returnAddress, extra)
		registryKey = (lomExpression, property, returnAddress, extra)
		createListener = True
		registrants = {id}
		context = dict(locals())
		context.update(self.codeContext)
		context['OSCMessage'] = OSCMessage
		if registryKey in self.registry:
			# self.debug('reg', lomExpression, property, returnAddress) # debug
			self.registry[registryKey]['registrants'].add(id)
			if lomExpression in SPECIALLISTENERS or \
					eval(lomExpression, context) == \
									self.registry[registryKey]['liveObject']:
				setterIndex = self.registry[registryKey]['setterIndex']
				createListener = False
			else:
				# object has changed
				registrants = self.registry[registryKey]['registrants'].copy()
				createListener = True
				self.remove(lomExpression, property, returnAddress, id, extra)

		if createListener:
			if lomExpression in SPECIALLISTENERS:
				self.registry[registryKey] = \
									self.addSpecial(lomExpression, property,
											 				returnAddress, id)
				setterIndex = self.registry[registryKey]['setterIndex']
			else:
				liveObject = eval(lomExpression, context)
				callbackCode = \
				"def watchCallback():" \
				"\n\tself.client.send(OSCMessage('" + returnAddress + \
							"'," + lomExpression + "." + property + "))"
				if 'str_for_value' in extra and property == 'value' and \
										hasattr(liveObject,'str_for_value'):
					callbackCode += "\n\tself.client.send(OSCMessage('""" + \
							returnAddress + "/str'," + lomExpression + \
							".str_for_value(" + \
									lomExpression + '.' + property + ")))"
				addCode = lomExpression + ".add_" + property + \
												'_listener(watchCallback)'
				fullCode = '\n'.join([callbackCode, addCode])
				try:
					exec(fullCode, context)
				except:
					self.codeContext['TDA'].sendError(
							'Error creating listener from OP id: ' + str(id),
							self.client)
					raise
				watchCallback = context['watchCallback']
				# create setter
				try:
					setterIndex = self.setters.index('')
				except ValueError:
					setterIndex = len(self.setters)
					self.setters.append('')
				propVal = getattr(liveObject, property)
				# convert val only if non-float
				if type(propVal) != float:
					valCode = type(propVal).__name__ + '(val)'
				else:
					valCode = 'val'
				setterCode = \
				"""def setter(val):
						""" + lomExpression + '.' + property + ' = ' + valCode
				fullCode = '\n'.join([setterCode,
									  "self.setters[setterIndex] = setter"])
				locals().update(self.codeContext)
				exec(fullCode, locals())
				# self.debug('add', registryKey)
				self.registry[registryKey] = {'registrants':{id},
											  'callback': watchCallback,
											  'setterIndex': setterIndex,
											  'liveObject': liveObject}
		# initial value callback
		if 'noinit' not in extra:
			self.registry[registryKey]['callback']()
		# send listener confirm
		if setterIndex is None:
			setterIndex = -1
		self.client.send(OSCMessage(
				'/listener' + registryKey[2] + '/setterIndex',
					[setterIndex, lomExpression, property, returnAddress,
					 id, extra] if extra is not None else
					[setterIndex, lomExpression, property, returnAddress,
					 id]))

	def remove(self, lomExpression, property, returnAddress, id=None, extra=''):
		"""
		Remove an item from the registry, stop callbacks if there are no
			remaining ids waiting for it.
		:param lomExpression: Python expression to reach Live object, e.g.:
									'SONG.tracks[1].devices[3].parameters[2]'
		:param property: property of object that has watcher, e.g.: 'Value'
		:param returnAddress: OSC address to send updates to
		:param id: unique ID of watcher. If None, remove listener.
		:param extra: an extra string with instructions.
				'noinit' = don't send initial value message
		"""
		registryKey = (lomExpression, property, returnAddress, extra)
		# remove listener
		# self.debug('remove', lomExpression, property, returnAddress)  # debug
		if registryKey not in self.registry:
			# if lomExpression in SPECIALLISTENERS:
			# 	self.debug('NOTINREG', lomExpression, registryKey)
			#self.debug('NOTINREG', lomExpression, property, returnAddress)
			return
		registryInfo = self.registry[registryKey]
		if id is None:
			registeredIDs = []
		else:
			registeredIDs = registryInfo['registrants']
			if id in registeredIDs:
				registeredIDs.remove(id)
		# if lomExpression in SPECIALLISTENERS:
		# 	self.debug(lomExpression, registeredIDs)
		if not registeredIDs:
			if lomExpression in SPECIALLISTENERS:
				self.removeSpecial(lomExpression, property, returnAddress, id,
								   							extra, registryInfo)
			# remove listener
			# self.debug('DO REMOVE', lomExpression, property, returnAddress) # debug
			try:
				getattr(registryInfo['liveObject'],
							"remove_" + property + "_listener")\
													(registryInfo['callback'])
			except:
				# import traceback; self.debug(traceback.format_exc()) #debug
				pass
			# clear setter
			if registryInfo['setterIndex'] is not None:
				self.setters[registryInfo['setterIndex']] = ''
			del self.registry[registryKey]
		# self.debug('remove', registryKey)

	def disconnect(self):
		"""
		Remove all listeners
		"""
		for key in list(self.registry.keys()):
			self.remove(key[0], key[1], key[2])

	def set(self, setterIndex, value):
		"""
		Set a listened-to value
		:param setterIndex: index of setter
		:param value: value to set to
		:return:
		"""
		# self.debug(setterIndex, value)
		# self.debug(self.setters)
		try:
			self.setters[setterIndex](value)
		except Exception as e:
			if 'Value cannot be set, the parameter is disabled' in str(e):
			 	pass
			else:
				for key, info in self.registry.items():
					if info['setterIndex'] == setterIndex:
						import sys
						newMessage = '\nError setting ' + key[0] \
										+ ' property: ' + key[1] \
										+ ' - value: ' + str(value) \
										+ ' - returnAddress:' + key[2]
						if PY3:
							if len(e.args) >= 1:
								e.args = (e.args[0] + newMessage,) + e.args[1:]
							raise
						else:
							exec("raise type(e), type(e)(e.message + "\
									"newMessage), sys.exc_info()[2]")											
			return # deleted setter

	def addSpecial(self, lomExpression, property, returnAddress, id, extra=''):
		"""
		Set up whatever is needed for special .
		:param lomExpression: Special ID. Starts with '*'
		:param property: Any relevant info
		:param returnAddress: OSC address to send updates to
		:param id: unique ID of watcher
		:returns registry info
		"""
		addFunction = getattr(self, 'add' + lomExpression[1:], None)
		setterIndex = None
		liveObject = None
		addInfo = addFunction(property, returnAddress, extra)
		setterIndex = addInfo.get('setterIndex')
		liveObject = addInfo.get('liveObject')
		callback = addInfo['callback']
		return {'registrants': {id},
				'callback': callback,
				'setterIndex': setterIndex,
				'liveObject': liveObject}

	def removeSpecial(self, lomExpression, property, returnAddress, id, extra,
					  										registryInfo):
		"""
		Remove a special item from the registry, stop callbacks if there are no
			remaining ids waiting for it.
		:param lomExpression: Special ID. Starts with '*'
		:param property: Any relevant info
		:param returnAddress: OSC address to send updates to
		:param id: unique ID of watcher
		"""
		removeFunction = getattr(self, 'remove' + lomExpression[1:], None)
		if removeFunction:
			removeFunction(property, returnAddress, extra, registryInfo)

	# region Selection

	def addSelection(self, property, returnAddress, extra=''):
		# self.debug('addSel')
		context = dict(self.codeContext)
		context['OSCMESSAGE'] = OSCMessage
		context['self'] = self
		callback = self.selectionCallback
		self.codeContext['SONG'].view.add_selected_track_listener(
														self.selectionCallback)
		self.codeContext['SONG'].view.add_selected_parameter_listener(
														self.selectionCallback)
		self.codeContext['SONG'].view.add_selected_scene_listener(
														self.selectionCallback)
		return {'callback': callback}

	def removeSelection(self, property, returnAddress, extra, registryInfo):
		# self.debug('remSel')
		self.codeContext['SONG'].view.remove_selected_track_listener(
													registryInfo['callback'])
		self.codeContext['SONG'].view.remove_selected_scene_listener(
													registryInfo['callback'])
		self.codeContext['SONG'].view.remove_selected_parameter_listener(
													registryInfo['callback'])
		for remover in self.selectionListenerRemovers:
			try:
				remover(self.selectionCallback)
			except:
				# remover not found, probably deleted
				pass
		self.selectionListenerRemovers = []

	def selectionCallback(self):
		song = self.codeContext['SONG']
		selectedTrack = song.view.selected_track
		ptrs = {}
		selectionInfo = {'trackIndex':-1, 'deviceIndex':-1, 'chainIndex':-1,
						 'parameterIndex':-1, 'sceneIndex':-1,
						 'ptrs':ptrs}
		for remover in self.selectionListenerRemovers:
			try:
				remover(self.selectionCallback)
			except:
				# remover not found, probably deleted
				pass
		self.selectionListenerRemovers = []
		# track
		for i, t in enumerate(song.tracks):
			if t == selectedTrack:
				selectionInfo['trackIndex'] = i
				if not t.view.selected_device_has_listener(
														self.selectionCallback):
					t.view.add_selected_device_listener(self.selectionCallback)
					self.selectionListenerRemovers.append(
										t.view.remove_selected_device_listener)
				break
		ptrs['track'] = selectedTrack._live_ptr
		# device
		selectedDevice = selectedTrack.view.selected_device
		if selectedDevice:
			for i, d in enumerate(selectedDevice.canonical_parent.devices):
				if d == selectedDevice:
					selectionInfo['deviceIndex'] = i
					break
			ptrs['device'] = selectedDevice._live_ptr
			# chain
			if hasattr(selectedDevice.view, 'selected_chain'):
				if not selectedDevice.view.selected_chain_has_listener(
														self.selectionCallback):
					selectedDevice.view.add_selected_chain_listener(
														self.selectionCallback)
					self.selectionListenerRemovers.append(
							selectedDevice.view.remove_selected_chain_listener)
				selectedChain = selectedDevice.view.selected_chain
				if selectedChain:
					for i,c in enumerate(selectedDevice.chains):
						if c == selectedChain:
							selectionInfo['chainIndex'] = i
					ptrs['chain'] = selectedChain._live_ptr
		# parameter
		selectedParameter = song.view.selected_parameter
		if selectedParameter:
			if hasattr(selectedParameter.canonical_parent, 'parameters'):
				for i, p in \
						enumerate(
								selectedParameter.canonical_parent.parameters):
					if p == selectedParameter:
						selectionInfo['parameterIndex'] = i
						break
			ptrs['parameter'] = selectedParameter._live_ptr
		# scene
		selectedScene = song.view.selected_scene
		if selectedScene:
			for i, s in enumerate(song.scenes):
				if s == selectedScene:
					selectionInfo['sceneIndex'] = i
					break
		self.client.send(OSCMessage('/song/info/selectedIndex/track',
										[selectionInfo['trackIndex']]))
		self.client.send(OSCMessage('/song/info/selectedIndex/device',
		 								[selectionInfo['deviceIndex']]))
		self.client.send(OSCMessage('/song/info/selectedIndex/chain',
		 								[selectionInfo['chainIndex']]))
		self.client.send(OSCMessage('/song/info/selectedIndex/parameter',
										[selectionInfo['parameterIndex']]))
		self.client.send(OSCMessage('/song/info/selectedIndex/scene',
										[selectionInfo['sceneIndex']]))
		self.client.send(OSCMessage('/song/info/selectionData',
		 											[str(selectionInfo)]))



	# endregion

	# region Beat Time

	def addBeatTime(self, property, returnAddress, extra=''):
		context = dict(self.codeContext)
		context['OSCMessage'] = OSCMessage
		context['self'] = self
		callbackCode = \
		"def callbackBeatTime():\n" \
		"	time = SONG.get_current_beats_song_time()\n" \
		"	self.client.send(OSCMessage('" + returnAddress + "/bars', "\
													"[time.bars]))\n"\
		"	self.client.send(OSCMessage('" + returnAddress + "/beats', "\
													"[time.beats]))\n"\
		"	self.client.send(OSCMessage('" + returnAddress + "/sixteenths', "\
													"[time.sub_division]))\n"\
		"	self.client.send(OSCMessage('" + returnAddress + "/time', "\
												"[SONG.current_song_time]))\n"
		exec(callbackCode, context)
		callback = context['callbackBeatTime']
		self.codeContext['SONG'].add_current_song_time_listener(callback)
		return {'callback': callback }

	def removeBeatTime(self, property, returnAddress, extra, registryInfo):
		self.codeContext['SONG'].remove_current_song_time_listener(
												registryInfo['callback'])

	# endregion

	# region MIDI notes

	def addMIDINotes(self, property, returnAddress, extra=''):
		global PY3
		context = dict(self.codeContext)
		context['OSCMessage'] = OSCMessage
		context['self'] = self
		if PY3:
			clip = eval(property[:property.find('get_notes_extended')-1], 
					context)
			callbackCode = \
			"def callbackMIDINotes():\n" \
			"	noteVector = " + property + "\n" \
			"	notes = tuple((n.pitch, n.start_time, n.duration, n.velocity," \
										"n.mute) for n in noteVector)\n"\
			"	self.client.send(OSCMessage('" + returnAddress + "', "\
														"[notes]))\n"
		else:
			clip = eval(property[:property.find('get_notes')-1], context)
			callbackCode = \
			"def callbackMIDINotes():\n" \
			"	notes = " + property + "\n" \
			"	self.client.send(OSCMessage('" + returnAddress + "', "\
														"[notes]))\n"
		exec(callbackCode, context)
		callback = context['callbackMIDINotes']
		clip.add_notes_listener(callback)
		return {'callback': callback }

	def removeMIDINotes(self, property, returnAddress, extra, registryInfo):
		global PY3
		if PY3:
			clip = eval(property[:property.find('get_notes_extended')-1],
													dict(self.codeContext))
		else:
			clip = eval(property[:property.find('get_notes')-1],
													dict(self.codeContext))
		if clip:
			clip.remove_notes_listener(registryInfo['callback'])


	# endregion

	pass