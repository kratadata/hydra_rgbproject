# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

import azureSTT

azureKey = "b6753e8ce553483dbb48036101d6db57" # microsoft azure key
azureRegion = "westeurope" # microsoft azure region code
maxWords = 9
active = False
azure_stt = None

def onOffToOn(channel, sampleIndex, val, prev):	
	global active
	
	if not active:
		global azure_stt
		azure_stt = azureSTT.AzureSTT(subscription_key=azureKey, region=azureRegion, maximumWords = maxWords)
		active = True
	
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	global active
	active = False
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	return
	