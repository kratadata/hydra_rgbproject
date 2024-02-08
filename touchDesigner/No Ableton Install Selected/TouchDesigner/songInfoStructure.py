"""
{
	'name': '<song name as defined by TDA Master name>' or None,
	'liveVersion': '<Ableton Live version number>',
	'scenes': {
		'<scene name>': { # scene info
			'name': '<scene name>',
			'tempo': scene tempo,
			'index': '<scene index>',
			'expression': '<LOM expression within parent>',
			'ptr': LOM Pointer (not persistent across saves)
		}
		... all scenes
	}
	'cuePoints': {
		'<cuePoint name>': { # cuePoint info
			'name': '<cuePoint name>',
			'time': cuePoint time,
			'index': '<cuePoint index>',
			'expression': '<LOM expression within parent>',
			'ptr': LOM Pointer (not persistent across saves)
		}
		... all cuePoints
	}
	'tracks': {
		'<track name>': { # track info
			'name': '<track name>',
			'index': track index (if applicable),
			'expression': '<LOM expression within parent>',
			'hasMIDIInput': True if track has MIDI input,
			'hasMIDIOutput': True if track has MIDI output,
			'ptr': LOM Pointer (not persistent across saves),
			'parentInfo': info of object parent
			'clipSlots': [
				{ # clipSlot info
				'index': <clip slot index>,
				'expression': '<LOM expression within parent>',
				'ptr': LOM Pointer (not persistent across saves),
				'parentInfo': info of object parent',
				'clip': {
					'name': '<clip name>',
					'filepath': '<clip file path>',
					'color': RGB int,
					'ptr': LOM Pointer (not persistent across saves)
				}
				... all clipSlots
			]
			'devices': {
				'<device name>': { # device info
					'name': '<device name>',
					'index': device index (if applicable),
					'expression': '<LOM expression within parent>',
					'ptr': LOM Pointer (not persistent across saves),
					'parentInfo': info of object parent
					'aPars': {
						'<parameter name>': { # parameter info
							'name': '<device name>',
							'index': device index (if applicable),
							'expression': '<LOM expression within parent>',
							'ptr': LOM Pointer (not persistent across saves),
							'min': minimum value,
							'max': maximum value,
							'value': value at time of dump
							'parentInfo': info of object parent
						},
						... all parameters
					},
					'chainType': 'chains', 'drumpads', or ''
					'chains': {
						'<chain name>': {
							# chain info (exactly like track info),
						}
						... all chains
					}
				},
				... all devices

				'# Mixer #': {
					'name': '# MIXER #',
					'index': None,
					'expression': 'mixer_device',
					'ptr': LOM Pointer (not persistent across saves),
					'parentInfo': info of object parent
					'aPars': {
						'Crossfader': {
							# parameter info (see above)
						},
						'Cue Volume': {
							# parameter info (see above)
						},
						'Panning': {
							# parameter info (see above)
						},
						'Track Activator': {
							# parameter info (see above)
						},
						'Volume': {
							# parameter info (see above)
						},

						'Send <send letter>' {
							# parameter info (see above)
						},
						... all sends
					},
					'chainType: '',
					'chains': {}
				}
			}
			... all tracks
		},
		'Return: <return track name>': {
			# track info (see above)
		},
		... all return tracks
		'# Master Track #': {
			# track info (see above)
		}
	}
}
"""