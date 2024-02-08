# TDA.py

# OSC Ableton Remote

import threading
import argparse
import sys
import json
import os.path
from collections import OrderedDict
import textwrap
from datetime import datetime
import traceback

import Live
from _Framework.ControlSurface import ControlSurface 

from .Shell import Shell
from .Listeners import Listeners, ptrStr

# from pythonosc import udp_client, dispatcher, osc_server

TDA_VERSION = '1.50'
DEFAULT_RECEIVE_PORT = 58888
DEFAULT_SEND_PORT = 58811
DEBUG = True
DEBUG_PREFIX = '###'

PY3 = sys.version_info[0] >= 3
if PY3:
	from . import OSC3 as OSC
else:
	from . import OSC


class TDA(ControlSurface):

	# region Main

	def __init__(self, c_instance):
		ControlSurface.__init__(self, c_instance)
		self.__c_instance = c_instance
		self.debugging = DEBUG
		self.clients = {}
		self.clientSourceDict = {}
		self.watchedObjects = set() # objects with TDA watchers on them
		self.TDAMasterDevice = None # TDA_Master max device
		self.server = None
		self.songHasChanged = False
		self.startSongListeners()
		self.deviceDict = {} # dictionary of '<name>': deviceObject
		# add default client and wait for connections
		# self.addClient()
		self.listenerSetMsgs = {}
		self.ptrStr = ptrStr
	
		self.schedule_message(1, self.postInit)	

	def postInit(self):
		self.setServer()

	def __del__(self):
		self.disconnect()

	def debug(self, *args, **kwargs):
		"""
		send a debug message to Ableton's log.txt
		"""
		self.log_message(DEBUG_PREFIX, *args, **kwargs)

	def setupTDAMaster(self):
		self.TDAMasterDevice = None
		for device in self.song().master_track.devices:
			for par in device.parameters:
				if par.name == 'ID_TDA_Master':
					self.TDAMasterDevice = device
					break
			if self.TDAMasterDevice:
				break
		if self.TDAMasterDevice:
			for p in self.TDAMasterDevice.parameters:
				if p.name == 'abletonPort':
					if not p.value_has_listener(self.portChanged):
						p.add_value_listener(self.portChanged)
					if not self.server or p.value != self.server.address()[1]:
						self.portChanged()
				if p.name == 'connected':
					try:
						p.value = bool(self.clients)
					except:
						pass
					self.schedule_message(1, self.checkClients)

	def checkClients(self):
		if self.TDAMasterDevice:
			for p in self.TDAMasterDevice.parameters:
				if p.name == 'abletonPort':
					if not p.value_has_listener(self.portChanged):
						p.add_value_listener(self.portChanged)
					if not self.server or p.value != self.server.address()[1]:
						self.portChanged()
				if p.name == 'connected':
					p.value = bool(self.clients)
			# attempt to get IP address
			# try:
			# 	import socket
			# 	import encodings
			# 	from . import idna
			# 	encodings.idna = idna
			# 	hostname = socket.gethostname()
			# 	self.debug('!', hostname)
			# 	address = socket.gethostbyname(hostname)
			# 	ip = [int(s) for s in address.split('.')]
			# 	for p in self.TDAMasterDevice.parameters:
			# 		if p.name.startswith('myHost'):
			# 			index = int(p.name[-1])
			# 			p.value = ip[index]
			# except:
			# 	# if anything goes wrong, set everything to 0
			# 	for p in self.TDAMasterDevice.parameters:
			# 		if p.name.startswith == 'myHost':
			# 			p.value = 0
			# 	raise

	def portChanged(self):
		if self.TDAMasterDevice:
			for p in self.TDAMasterDevice.parameters:
				if p.name == 'abletonPort':
					if self.server and p.value != self.server.address()[1]:
						self.disconnectClients()
					self.setServer()

	# endregion

	# region Networking

	def addClient(self, address='localhost', sendPort=None,
	                        sourcePort=None, clearOthers=False):
		"""
		add an OSC client at address:sendPort
		if sendPort is None use DEFAULT_SEND_PORT

		If this was initiated by a client, that client should have sent a
		sourcePort. If not, tell client we want to connect.
		"""
		if sendPort is None:
			sendPort = DEFAULT_SEND_PORT # port to send messages to
		if clearOthers:
			self.clients = {}
			self.clientSourceDict = {}
		if address == 'localhost':
			address = '127.0.0.1'
		client = self.clients.get((address, sendPort), None)
		if client is None:
			# set up client object
			client = OSC.OSCClient()
			client.connect((address, sendPort))
			client.context = {   'APP': Live.Application.get_application(),
								 'SONG': self.song(),
								 'TDA': self,
								 'CLIENT': client,
								 'OSC': OSC,
								 'Live': Live
								 }
			client.shell = Shell(self, client)
			client.listeners = Listeners(client)

			if self.debugging: self.debug("addClient:", address, sendPort)
			self.clients[client.address()] = client
		else:
			client.listeners.disconnect()
		client.sourcePort = sourcePort # the port that client sends from
		if sourcePort:
			self.clientSourceDict[(client.address()[0], sourcePort)] = client
			self.schedule_message(1, self.setupTDAMaster)
		else:
			self.send(client, self.server.address(), '/info/serverInit')
		return client

	def removeClient(self, address='localhost', sendPort=None,
	                        sourcePort=None, clearOthers=False):
		"""
		remove an OSC client at address:sendPort
		"""
		if address == 'localhost':
			address = '127.0.0.1'
		if self.debugging: self.debug('removeClient:', (address, sendPort))
		client = self.clients.get((address, sendPort))
		if client is not None:
			client.listeners.disconnect()
			del self.clientSourceDict[client.address()[0], sourcePort]
			del self.clients[(address, sendPort)]
		self.schedule_message(1, self.setupTDAMaster)


	def setServer(self, address='0.0.0.0', receivePort=None):
		"""
		add an OSC server at address:receivePort
		if receivePort is None use DEFAULT_RECEIVE_PORT
		"""
		if receivePort is None:
			if self.TDAMasterDevice:
				for p in self.TDAMasterDevice.parameters:
					if p.name == 'abletonPort':
						receivePort = int(p.value)
			else:
				receivePort = DEFAULT_RECEIVE_PORT
		if self.server:
			if self.server.address() == (address, receivePort):
				return
			self.server.close()
		server = OSC.OSCServer((address, receivePort))
		server.timeout = 0
		server.sendError = self.sendError
		try:
			self.addHandlers(server)
			self.server = server
			self.schedule_message(1, self.processServerMsgs)
			# if self.debugging: self.debug("setServer:", address, receivePort)
		except:
			server.close()
			raise

	def disconnect(self):
		"""
		disconnect all OSC connections
		"""
		if self.server:
			self.server.close()
			self.server=None
		self.disconnectClients()
		self.clients = {}
		try:
			ControlSurface.disconnect(self)
		except:
			pass
		if self.debugging: self.debug("disconnect")

	def disconnectClients(self):
		for client in self.clients.values():
			client.listeners.disconnect()
			self.send(client, [''], '/info/serverDisconnect')

	def processServerMsgs(self):
		if self.songHasChanged:
			self.setupTDAMaster()
			for client in self.clients.values():
				client.listeners.disconnect()
				self.sendSongInfo(client)
		self.songHasChanged = False
		while True:
			try:
				self.server.handle_request()
			except:
				self.debug(traceback.format_exc())
			if self.server.empty:
				break
		try:
			self.processListenerSetMsgs()
		except:
			self.debug(traceback.format_exc())

		self.schedule_message(0.000001, self.processServerMsgs)

	def processListenerSetMsgs(self):
		for source, msgs in self.listenerSetMsgs.items():
			try:
				client = self.clientSourceDict[source]
			except:
				self.debug("Msgs from unknown client:",
						   					source, "-", '/listener/set')
				continue
			usedIndexes = set()
			for msg in reversed(msgs):
				if msg[0] not in usedIndexes:
					try:
						client.listeners.set(msg[0], msg[1]) # setterIndex,value
					except:
						error = str(msg[0]) + ' ' + \
								str(msg[1])  + '\n' + \
								traceback.format_exc()
						self.sendError(error, source)
						self.debug(error)
					usedIndexes.add(msg[0])
		self.listenerSetMsgs = {}

	def send(self, client, message, OSCaddress=None):
		try:
			client.send( message)
		except:
			try:
				message = OSC.OSCMessage(OSCaddress, message)
				client.send(message)
			except:
				if self.debugging: self.debug("Failed to send message! Msg:",
						message, "OSC Addr:", OSCaddress, "Client:", client )
				raise

	# endregion

	# region Message Handlers

	def addHandlers(self, server):
		server.addMsgHandler('default', self.onMsgUnknown)
		server.addMsgHandler('/shell/consoleLine', self.onMsgShell)
		server.addMsgHandler('/shell/runCode', self.onMsgShell)
		server.addMsgHandler('/shell/requestData', self.onMsgShell)
		server.addMsgHandler('/listener/add', self.onMsgListener)
		server.addMsgHandler('/listener/remove', self.onMsgListener)
		server.addMsgHandler('/listener/set', self.onMsgListenerSet)
		server.addMsgHandler('/tda/ping', self.onMsgPing)
		server.addMsgHandler('/tda/command', self.onMsgCommand)

	def onMsgUnknown(self, addr, tags, msg, source):
		if addr.startswith('/tdamax/'):
			pass
		if self.debugging: self.debug('onMsgUnknown', 'addr:', addr,
			  	'data:', repr(msg), 'source:', source, 'tags:', tags, 'time:',
	                    str(datetime.now()))

	def onMsgMax(self, addr, tags, msg, source):
		pass

	def onMsgListenerSet(self, addr, tags, msg, source):
		try:
			self.listenerSetMsgs[source].append(msg)
		except:
			self.listenerSetMsgs[source] = [msg]

	def onMsgListener(self, addr, tags, msg, source):
		try:
			client = self.clientSourceDict[source]
		except:
			self.debug("Msg from unknown client:", source, "-", addr, msg)
			return
		if addr.endswith('/add'):
			# if self.debugging and len(msg) == 4: self.debug(addr, msg, source)
			client.listeners.add(msg[0], msg[1], msg[2], msg[3],
								 msg[4] if len(msg) > 4 else '')
		elif addr.endswith('/remove'):
			# if self.debugging and len(msg) == 4: self.debug(addr, msg, source)
			# self.debug(addr, msg, source)
			client.listeners.remove(msg[0], msg[1], msg[2], msg[3])


	def onMsgShell(self, addr, tags, msg, source):
		# if self.debugging: self.debug(addr, msg, source)
		client = self.clientSourceDict[source]
		if addr.endswith('/consoleLine'):
			client.shell.pushLine(msg[0])
		elif addr.endswith('/runCode'):
			client.shell.runCode(msg[0])
		elif addr.endswith('requestData'):
			client.shell.requestData(msg)

	def onMsgCommand(self, addr, tags, msg, source):
		# if self.debugging: self.debug(addr, msg, source)
		command = msg[0]
		if command == 'connect':
			client = self.addClient(source[0], msg[1], source[1])
			self.sendConnectInfo(client)
			self.log_message("Connected to TouchDesigner at " +
							 	source[0] + ':' + str(msg[1]) +
							' (TDA version ' + (str(msg[2])
							 			if len(msg) > 2 else 'unknown') + ')')
		elif command == 'disconnect':
			self.removeClient(source[0], msg[1], source[1])
			self.log_message("Disconnected from TouchDesigner at " +
								 	source[0] + ':' + str(msg[1]))
		elif command == 'addDevice':
			self.addDevice(self.clientSourceDict[source],
						   msg[1], msg[2], msg[3],
						   	eval(msg[4]) if msg[4] else None)
		elif command == 'setDeviceNetworking':
			self.setDeviceNetworking(self.clientSourceDict[source], msg[1])
		elif command == 'setDebugging':
			self.debugging = msg[1]
			for client in self.clients.values():
				self.send(client, [self.debugging], '/info/debugging')
		elif command == 'songDump':
			self.songHasChanged = True

	def onMsgPing(self, addr, tags, msg, source):
		if self.debugging: self.debug(addr, msg, source)
		self.send(self.clientSourceDict[source],
								[str(datetime.now()), msg[0]], '/debug/ping')

	# endregion

	# region Commands

	def setDeviceNetworking(self, client, lomExpression):
		"""
		Automatically set up networking parameters of a TDA Max device.
		Autoset network parameters are: host0-3, port, inport
		:param client: requesting client
		:param lomExpression: of device
		"""
		address = None
		port = None
		if self.TDAMasterDevice:
			for p in self.TDAMasterDevice.parameters:
				if p.name == 'tdaBroadcast':
					if p.value:
						address = ['255.255.255.255']
				if p.name == 'tdaBroadcastPort':
					port = p.value
		if address:
			address.append(port)
		else:
			address = client.address()
		ip = [int(s) for s in address[0].split('.')]
		networkPars = {
			'host0': ip[0],
			'host1': ip[1],
			'host2': ip[2],
			'host3': ip[3],
			'port': address[1],
			'inport': self.server.address()[1]
		}
		device = eval(lomExpression, client.context)
		for p in device.parameters:
			if p.name in networkPars:
				p.value = networkPars[p.name]
				# self.debug(lomExpression, p.name, networkPars[p.name])

	def setupDeviceDict(self):
		self.deviceDict = {} # dictionary of '<name>': deviceObject
		def addDevices(folder):
			for c in folder.iter_children:
				# self.debug('      file:', c.name)
				if c.name.endswith('.amxd') or c.name.endswith('.adg') \
															or c.is_loadable:
					# self.debug('         isDevice!')
					self.deviceDict[c.name] = c
				#addDevices(c)

		for folder in Live.Application.get_application().browser.user_folders:
			if folder.name == "TouchDesigner":
				# self.debug('deviceSearch Folder:', folder.name)
				addDevices(folder)
				for subfolder in folder.children:
					# self.debug('   deviceSearch subFolder:', subfolder.name)
					if subfolder.name == "TDA Project":
						# self.debug('      project subfolder!')
						addDevices(subfolder)

	def addDevice(self, client, fileName, lomExpression, deviceName=None,
				  												parDict=None):
		"""
		Add a max device
		:param client: requesting client
		:param fileName: device filename
		:param lomExpression: LOM expression of chain to add to
		:param deviceName: new name for device
		:param parDict: dict of par:value for initial parameter values
		"""
		self.setupDeviceDict()
		if PY3 and fileName.endswith('.amxd'):
			fileName = fileName[:-5]
		deviceItem = self.deviceDict.get(fileName)
		if not deviceItem:
			self.debug('deviceDict:', self.deviceDict)
			raise Exception(fileName + ' device not found!\n' + \
														str(self.deviceDict))
		selected = self.song().view.selected_track
		insertMode = selected.view.device_insert_mode
		addChain = eval(lomExpression, client.context)
		self.song().view.selected_track = addChain
		chainIgnoreDevice = None
		for chainDevice in addChain.devices:
			if len(chainDevice.parameters) > 1 and \
					chainDevice.parameters[1].name == 'ID_TDA_Ignore':
				chainIgnoreDevice = chainDevice
				break
		if chainIgnoreDevice is not None:
			addChain.selected_device = chainIgnoreDevice
			selected.view.device_insert_mode = True
		else:
			selected.view.device_insert_mode = False
		Live.Application.get_application().browser.load_item(deviceItem)
		device = None
		for d in reversed(addChain.devices):
			if d.name == fileName.split('.')[0]:
				device = d
				break
		if device is None:
			self.song().view.selected_track = selected
			selected.view.device_insert_mode = insertMode
			raise Exception('Error creating ' + fileName)
		# move to before any ignore devices

		# set name
		if deviceName:
			device.name = deviceName
		if parDict:
			for parName, parVal in parDict.items():
				for p in device.parameters:
					if p.name == parName:
						p.value = parVal
		self.song().view.select_device(device)
#		self.song().view.selected_track = selected
		selected.view.device_insert_mode = insertMode
		self.songChanged()

	def sendConnectInfo(self, client):
		self.sendSongInfo(client)

	def sendError(self, error, client_address=None):
		oscAddr = '/debug/error'
		self.debug(error)
		if client_address in self.clientSourceDict:
			self.send(self.clientSourceDict[client_address], error, oscAddr)
		elif client_address in self.clients:
			self.send(self.clients[client_address], error, oscAddr)
		else:
			for client in self.clients.values():
				self.send(client, error, oscAddr)

	def sendSongInfo(self, client):
		songInfo = OrderedDict()
		if self.TDAMasterDevice:
			songInfo['name'] = self.TDAMasterDevice.name
		else:
			songInfo['name'] = None
		app = Live.Application.get_application()
		version = str(app.get_major_version()) + '.' + \
				  str(app.get_minor_version())
		if app.get_bugfix_version():
			version += '.' + str(app.get_bugfix_version())
		songInfo['liveVersion'] = version
		songInfo['tdaVersion'] = TDA_VERSION
		songInfo['filepath'] = os.path.abspath(__file__)
		tracks = songInfo['tracks'] = OrderedDict()
		cuePoints = songInfo['cuePoints'] = OrderedDict()
		scenes = songInfo['scenes'] = OrderedDict()
		#scenes
		for sindex, scene in enumerate(self.song().scenes):
			key = ptrStr(scene._live_ptr)
			scenes[key] = OrderedDict()
			scenes[key]['name'] = scene.name
			scenes[key]['tempo'] = scene.tempo
			scenes[key]['index'] = sindex
			scenes[key]['expression'] = 'scenes[' + str(sindex) + ']'
			scenes[key]['ptr'] = scene._live_ptr
		# cuepoints
		for lindex, cue_point in enumerate(self.song().cue_points):
			key = ptrStr(cue_point._live_ptr)
			cuePoints[key] = OrderedDict()
			cuePoints[key]['name'] = cue_point.name
			cuePoints[key]['time'] = cue_point.time
			cuePoints[key]['index'] = lindex
			cuePoints[key]['expression'] = 'cue_points[' + str(lindex) + ']'
			cuePoints[key]['ptr'] = cue_point._live_ptr
		# normal tracks
		for tIndex, track in enumerate(self.song().tracks):
			key = ptrStr(track._live_ptr)
			tracks[key] = self.getTrackOrChainInfo(track, tIndex, track.name,
											   'tracks[' + str(tIndex) +']')
		# return tracks
		for rIndex, track in enumerate(self.song().return_tracks):
			key = ptrStr(track._live_ptr)
			tracks[key] = self.getTrackOrChainInfo(track, rIndex,
											'Return: ' + track.name,
											'return_tracks[' + str(rIndex) +']')
		# master track
		track = self.song().master_track
		key = ptrStr(track._live_ptr)
		tracks[key] = self.getTrackOrChainInfo(track, None,
											   '# Master Track #',
											   'master_track')

		self.send(client, [], '/info/songDump/start')

		songText = json.dumps(songInfo)
		for chunk in \
				[songText[i:i+1024] for i in range(0, len(songText), 1024)]:
			self.send(client, chunk, '/info/songDump/chunk')
		self.send(client, [], '/info/songDump/end')
		self.send(client, [-1], '/song/info/triggered_scene')

	def getTrackOrChainInfo(self, chain, index, name, expression):
		# use the word chain for convenience to represent track or chain
		chainInfo = OrderedDict()
		chainInfo['name'] = name
		chainInfo['index'] = index
		chainInfo['expression'] = expression
		chainInfo['hasMIDIInput'] = chain.has_midi_input
		chainInfo['hasMIDIOutput'] = chain.has_midi_output
		chainInfo['ptr'] = chain._live_ptr
		# clipSlots
		try:
			chain.clip_slots
		except:
			pass
		else:
			clipSlots = []
			for cIndex, clipSlot in enumerate(chain.clip_slots):
				clipSlotInfo = {}
				clipSlots.append(clipSlotInfo)
				clipSlotInfo['index'] = cIndex
				clipSlotInfo['expression'] = 'clip_slot[' + str(cIndex) + ']'
				clipSlotInfo['ptr'] = clipSlot._live_ptr
				if clipSlot.has_clip:
					clipInfo = OrderedDict()
					clipInfo['name'] = clipSlot.clip.name
					if clipSlot.clip.is_midi_clip:
						clipInfo['filePath'] = ''
					else:
						clipInfo['filePath'] = clipSlot.clip.file_path
					clipInfo['color'] = clipSlot.clip.color
					clipInfo['ptr'] = clipSlot.clip._live_ptr
				else:
					clipInfo = {}
				clipSlotInfo['clip'] = clipInfo
			chainInfo['clipSlots'] = clipSlots
		# devices
		devices = OrderedDict()

		#mixer device
		device = chain.mixer_device
		key = ptrStr(device._live_ptr)
		devices[key] = OrderedDict()
		devices[key]['name'] = '# Mixer #'
		devices[key]['index'] = None
		devices[key]['expression'] = 'mixer_device'
		devices[key]['ptr'] = device._live_ptr
		devices[key]['aPars'] = self.getMixerParametersInfo(device)
		devices[key]['chainType'] = ''
		devices[key]['chains'] = {}

		# normal devices
		for dIndex, device in enumerate(chain.devices):
			if len(device.parameters) > 1 and \
								device.parameters[1].name == 'ID_TDA_Ignore':
				self.setupIgnoreListener(device)
				if device.parameters[0].value:
					break

			key = ptrStr(device._live_ptr)
			devices[key] = OrderedDict()
			devices[key]['name'] = device.name
			devices[key]['index'] = dIndex
			devices[key]['class'] = device.class_name
			devices[key]['expression'] = 'devices[' + str(dIndex) + ']'
			devices[key]['ptr'] = device._live_ptr
			devices[key]['aPars'] = self.getDeviceParametersInfo(device)
			devices[key]['chainType'] = 'chains' if device.can_have_chains else\
								'drumPads' if device.can_have_drum_pads else ''
			devices[key]['chains'] = self.getChainsInfo(device)

		chainInfo['devices'] = devices
		return chainInfo

	def setupIgnoreListener(self, device):
		if str(device.parameters[0]._live_ptr) + 'i' not in self.watchedObjects:
			self.watchedObjects.add(str(device.parameters[0]._live_ptr)+'i')
			device.parameters[0].add_value_listener(self.ignoreToggle)

	def ignoreToggle(self):
		self.songChanged()

	def getChainsInfo(self, device):
		chains = OrderedDict()
		if device.can_have_chains or device.can_have_drum_pads:
			for cIndex, chain in enumerate(device.chains):
				key = ptrStr(chain._live_ptr)
				chains[key] = self.getTrackOrChainInfo(chain, cIndex,
								   chain.name, 'chains[' + str(cIndex) + ']')
		return chains

	def getParameterInfo(self, parameter, index, name, expression):
		parameterInfo = OrderedDict()
		parameterInfo['name'] = name
		parameterInfo['index'] = index
		parameterInfo['expression'] = expression
		parameterInfo['ptr'] = parameter._live_ptr
		parameterInfo['min'] = parameter.min
		parameterInfo['max'] = parameter.max
		parameterInfo['value'] = parameter.value
		return parameterInfo

	def getDeviceParametersInfo(self, device):
		parameters = OrderedDict()
		for pIndex, parameter in enumerate(device.parameters):
			key = ptrStr(parameter._live_ptr)
			parameters[key] = self.getParameterInfo(parameter, pIndex,
							parameter.name, 'parameters[' + str(pIndex) + ']')
		return parameters

	def getMixerParametersInfo(self, device):
		parameters = OrderedDict()
		for name in ['Crossfader', 'Cue Volume', 'Panning', 'Track Activator',
					 												'Volume']:
			expression = name.lower().replace(' ', '_')
			try:
				parameter = getattr(device, expression)
			except:
				continue
			key = ptrStr(parameter._live_ptr)
			parameters[key] = self.getParameterInfo(parameter, None, name,
																	expression)
		try:
			device.sends
		except:
			pass
		else:
			aChar = ord('A')
			for sIndex, send in enumerate(device.sends):
				key = ptrStr(send._live_ptr)
				parameters[key] = self.getParameterInfo(send, sIndex,
											'Send ' + chr(aChar + sIndex),
											'sends[' + str(sIndex) + ']')
		return parameters

	# endregion

	# region Song Listeners

	def startSongListeners(self):
		self.song().add_tracks_listener(self.tracksChanged)
		self.song().add_return_tracks_listener(self.returnTracksChanged)
		self.song().add_cue_points_listener(self.cuePointsChanged)
		#self.song().add_is_playing_listener(self.playPoint)
		for cue_point in self.song().cue_points:
			self.setupCuePointListeners(cue_point)
		for track in self.song().tracks:
			self.setupChainListeners(track)
			self.setupClipSlotListeners(track)
		for track in self.song().return_tracks:
			self.setupChainListeners(track)
		self.setupChainListeners(self.song().master_track)
		self.song().add_scenes_listener(self.scenesChanged)
		for scene in self.song().scenes:
			self.setupSceneListeners(scene)
		self.schedule_message(1, self.setupTDAMaster)

	def playPoint(self):
		# send time that playing started for cuepoint passing info
		if self.song().is_playing:
			self.debug(self.song().current_song_time, self.song().is_playing)

	def tracksChanged(self):
		for track in self.song().tracks:
			if track._live_ptr not in self.watchedObjects:
				self.setupChainListeners(track)
				self.setupClipListeners(track)
				# if self.debugging: self.debug('addlistenerto', track.name)
		self.songChanged()
		# if self.debugging: self.debug('trackschanged')

	def returnTracksChanged(self):
		for track in self.song().return_tracks:
			if track._live_ptr not in self.watchedObjects:
				self.setupChainListeners(track)
				# if self.debugging: self.debug('addlistenerto', track.name)
		self.songChanged()

	def scenesChanged(self):
		for scene in self.song().scenes:
			if scene._live_ptr not in self.watchedObjects:
				self.setupSceneListeners(scene)
		self.songChanged()

	def setupSceneListeners(self, scene):
		def sceneTriggered():
			self.sceneTriggered(scene)
		def sceneNameChanged():
			self.nameChanged(scene)
			self.songChanged()
		scene.add_name_listener(sceneNameChanged)
		scene.add_is_triggered_listener(sceneTriggered)
		self.watchedObjects.add(scene._live_ptr)

	def sceneTriggered(self, scene):
		sceneIndex = list(self.song().scenes).index(scene)
		if not scene.is_triggered:
			for client in self.clients.values():
				self.send(client, [sceneIndex], '/song/info/started_scene')
			sceneIndex = -1
		for client in self.clients.values():
			self.send(client, [sceneIndex], '/song/info/triggered_scene')

	def chainsChanged(self, device):
		self.setupDeviceChainsListeners(device)
		self.songChanged()

	def setupDeviceChainsListeners(self, device):
		try:
			device.chains
		except:
			pass
		else:
			for chain in device.chains:
				if chain._live_ptr not in self.watchedObjects:
					self.setupChainListeners(chain)

	def cuePointsChanged(self):
		for cue_point in self.song().cue_points:
			if cue_point._live_ptr not in self.watchedObjects:
				self.setupCuePointListeners(cue_point)
				# self.debug('changed', cue_point.name)
		self.songChanged()

	def setupCuePointListeners(self, cuePoint):
		def cuePointNameChanged():
			self.nameChanged(cuePoint)
		cuePoint.add_name_listener(cuePointNameChanged)
		def cuePointTimeChanged():
			self.cuePointTimeChanged(cuePoint)
		cuePoint.add_time_listener(cuePointTimeChanged)
		self.watchedObjects.add(cuePoint._live_ptr)

	def cuePointTimeChanged(self, cuePoint):
		for client in self.clients.values():
			# string pointers for OS safety
			self.send(client, [ptrStr(cuePoint._live_ptr), cuePoint.time],
					  								'/info/cuePointTimeChanged')

	def setupChainListeners(self, chain):
		def devicesChanged():
			self.devicesChanged(chain)
		chain.add_devices_listener(devicesChanged)

		def chainNameChanged():
			self.nameChanged(chain)
		chain.add_name_listener(chainNameChanged)

		self.setupDeviceListeners(chain)
		self.watchedObjects.add(chain._live_ptr)

	def setupClipSlotListeners(self, chain):
		def clipSlotsChanged():
			self.setupClipListeners(chain)
		chain.add_clip_slots_listener(clipSlotsChanged)
		self.setupClipListeners(chain)

	def setupClipListeners(self, chain):
		for clipSlot in chain.clip_slots:
			if clipSlot._live_ptr not in self.watchedObjects:
				context = {'self': self, 'clipSlot': clipSlot}
				exec(	"def clipSlotChanged():\n"
					 	"	self.clipSlotChanged(clipSlot)\n"
					 	"clipSlot.add_has_clip_listener(clipSlotChanged)\n"
						"if clipSlot.has_clip:\n"
						"	clipSlot.clip.add_name_listener(clipSlotChanged)\n"
						"	clipSlot.clip.add_color_listener(clipSlotChanged)\n"
						"	if not clipSlot.clip.is_midi_clip:\n"
						"		clipSlot.clip.add_file_path_listener"
						 								"(clipSlotChanged)\n"
						"	self.watchedObjects.add"
						 						"(clipSlot.clip._live_ptr)"
						,context)
			self.watchedObjects.add(clipSlot._live_ptr)

	def clipSlotChanged(self, clipSlot):
		for client in self.clients.values():
			if clipSlot.has_clip:
				self.send(client, [ptrStr(clipSlot._live_ptr),
								   clipSlot.clip.name,
					  			   '' if clipSlot.clip.is_midi_clip
					  							else clipSlot.clip.file_path,
									clipSlot.clip.color],
						 '/info/clipSlotChanged')
			else:
				self.send(client, [ptrStr(clipSlot._live_ptr)],
						 '/info/clipSlotChanged')
		if clipSlot.has_clip and \
							clipSlot.clip._live_ptr not in self.watchedObjects:
				context = {'self': self, 'clipSlot': clipSlot}
				exec("def clipSlotChanged():\n"
					 	"	self.clipSlotChanged(clipSlot)\n"
					 "clipSlot.clip.add_name_listener(clipSlotChanged)\n"
					 "clipSlot.clip.add_color_listener(clipSlotChanged)\n"
					 "if not clipSlot.clip.is_midi_clip:\n"
					 "	clipSlot.clip.add_file_path_listener"
													"(clipSlotChanged)\n"
					 "self.watchedObjects.add(clipSlot.clip._live_ptr)",
					 context)

	def setupDeviceListeners(self, chain):
		for device in chain.devices:
			if device._live_ptr not in self.watchedObjects:
				context = {'self': self, 'device': device}
				exec(	"def deviceNameChanged():\n"
						"	self.nameChanged(device)\n"
						"device.add_name_listener(deviceNameChanged)\n"

						"def parametersChanged():\n"
						"	self.parametersChanged(device)\n"
						"device.add_parameters_listener(parametersChanged)\n"

						"def chainsChanged():\n"
						"	self.chainsChanged(device)\n"
						"try:\n"
						"	device.add_chains_listener(chainsChanged)\n"
						"except:\n"
						"	pass\n"
						, context)
				self.setupDeviceChainsListeners(device)
				self.setupParameterListeners(device)
				self.watchedObjects.add(device._live_ptr)

	def setupParameterListeners(self, device):
		for parameter in device.parameters:
			if parameter._live_ptr not in self.watchedObjects:
				context = {'self': self, 'parameter': parameter}
				exec(	"def parameterNameChanged():\n"
						"	self.nameChanged(parameter)\n"
						"parameter.add_name_listener(parameterNameChanged)\n"
						, context)
				self.watchedObjects.add(parameter._live_ptr)

	def parametersChanged(self, device):
		self.setupParameterListeners( device)
		self.songChanged()

	def nameChanged(self, liveObject):
		self.schedule_message(2, self.sendNameChanged,
						([ptrStr(liveObject._live_ptr), liveObject.name],
					  								'/info/nameChanged'))

	def sendNameChanged(self, args):
		for client in self.clients.values():
			# string pointers for OS safety
			self.send(client, args[0], args[1])
			# self.songChanged()

	def devicesChanged(self, track):
		# if self.debugging: self.debug('deviceschanged on ' + track.name)
		try:
			self.TDAMasterDevice.name
		except:
			self.setupTDAMaster()
			self.disconnectClients()
		self.setupDeviceListeners(track)
		self.songChanged()

	def songChanged(self):
		self.songHasChanged = True

	# endregion

	# region Testing

	def sendTest(self, client):
		self.send(client, ['TDA sendTest', str(datetime.now())], '/debug')
		if self.debugging: self.debug('sendTest', str(datetime.now()))


	# endregion
