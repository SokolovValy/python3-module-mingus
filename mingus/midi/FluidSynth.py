"""

================================================================================

	mingus - Music theory Python package, MIDI sequencer
	Copyright (C) 2008, Bart Spaans

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

================================================================================

   This module provides a [refMingusExtraMidisequencer MidiSequencer] which will take the objects from 
   mingus.containers and turn them into MIDI messages.

================================================================================

"""

from datetime import datetime
from mingus.containers.Instrument import MidiInstrument
import fluidsynth as fs
from time import sleep

class MidiSequencer:
	"""A simple MidiSequencer for FluidSynth"""

	output = None


	def __init__(self):
		self.fs = fs.Synth()

	def start_audio_output(self, driver=None):
		"""The optional driver argument can be any of 'alsa', \
'oss', 'jack', 'portaudio', 'sndmgr', 'coreaudio', 'Direct Sound'. \
Not all drivers will be available for every platform."""
		self.fs.start(driver)

	def load_sound_font(self, sf2):
		"""Loads a sound font. This function should be called \
before your audio can be played, since the instruments are kept in the \
sf2 file. Retuns True on success, False on failure."""
		self.sfid = self.fs.sfload(sf2)
		if self.sfid == -1:
			return False
		return True


	def set_instrument(self, channel, instr):
		"""Sets the channel to the instrument _instr_."""
		self.fs.program_select(channel, self.sfid, 0, instr)
		return True

	def control_change(self, channel, control, value):
		if control < 0 or control > 128:
			return False
		if value < 0 or value > 128:
			return False
		self.fs.cc(channel, control, value)
		return True


	def play_Note(self, note, channel = 1, velocity = 100):
		"""Plays a Note object on a channel[1-16] with a \
velocity[0-127]. You can either specify the velocity and channel \
here as arguments or you can set the Note.velocity and Note.channel \
attributes, which will take presedence over the function arguments."""
		if hasattr(note, 'velocity'):
			velocity = note.velocity
		if hasattr(note, 'channel'):
			channel = note.channel
		self.fs.noteon(channel, int(note) + 12, velocity)
		return True

	def stop_Note(self, note, channel = 1):
		"""Stops a note on a channel."""
		return self.fs.noteoff(channel, int(note) + 12)




	def stop_everything(self):
		"""Stops all the notes on all channels."""
		for x in range(118):
			for c in range(16):
				self.stop_Note(x, c)


	def play_NoteContainer(self, nc, channel = 1, velocity = 100):
		"""Plays the Notes in the NoteContainer nc."""
		for note in nc:
			if not self.play_Note(note, channel, velocity):
				return False
		return True



	def stop_NoteContainer(self, nc, channel = 1):
		"""Stops playing the notes in NoteContainer nc."""
		for note in nc:
			if not self.stop_Note(note, channel):
				return False
		return True



	def play_Bar(self, bar, channel = 1, bpm = 120):
		"""Plays a Bar object. If the channel attribute on a Note\in the Bar has been set it will take presedence over the one you can \
add here."""

		# length of a quarter note
		qn_length = 60.0 / bpm

		for nc in bar:

			if not self.play_NoteContainer(nc[2], channel, 100):
				return False
			
			sleep(qn_length * (4.0 / nc[1]))
			self.stop_NoteContainer(nc[2], channel)

		return True


	def play_Bars(self, bars, channels, bpm = 120):
		"""Plays several bars (a list of Bar objects) at the same time. A list of \
channels should also be provided."""

		duration = 60.0 / bpm * 4
		tick = 0.0  # place in beat from 0.0 to bar.length
		cur = []    # keeps the index of the note needing investigation in each of bars
		playing = [] # keeps track of the notecontainers being played right now.


		# Prepare cur list
		for x in bars:
			cur.append(0)

		n = datetime.now()
		
		while tick < bars[0].length:

			# Check each bar in bars and investigate index in cur.
			for x in range(len(bars)):

				bar = bars[x]
				current_nc = bar[cur[x]]

				# Should note be played?
				if current_nc[0] <= tick and \
					current_nc[0] + \
					(1.0 / current_nc[1]) >= tick \
					and [current_nc[0], current_nc[1], current_nc[2],\
						channels[x]] not in playing:

					self.play_NoteContainer(current_nc[2], channels[x])
					playing.append([current_nc[0], current_nc[1],\
							current_nc[2], channels[x]])
					if cur[x] != len(bar) - 1:
						cur[x] += 1

			# Should any notes stop playing?
			for p in playing:
				if p[0] + (1.0 / p[1]) <= tick:
					self.stop_NoteContainer(p[2], p[3])
					playing.remove(p)

			

			# Milliseconds so far
			a = datetime.now()
			millis = (a - n).microseconds / 1000.0 + (a - n).seconds * 1000.0

			# Calculate new tick
			tick = (millis / duration) * bars[0].length
			
		# Stop all the notes that are still playing
		for p in playing:
			self.stop_NoteContainer(p[2], p[3])
			playing.remove(p)

		return True


	def play_Track(self, track, channel = 1):
		"""Plays a Track object."""
		for bar in track:
			# bpm attribute needed? Or just another argument?
			if not self.play_Bar(bar, channel, 2000):
				return False
		return True

	def play_Tracks(self, tracks, channels, keep_playing_func = True):
		"""Plays a list of Tracks. keep_playing_func can be used to pass a function, \
which will determine if the tracks should keep playing after each played bar."""
		
		# Set the right instruments
		for x in range(len(tracks)):
			instr = tracks[x].instrument
			if isinstance(instr, MidiInstrument):
				try: 
					i = instr.names.index(instr.name)
				except:
					i = 1
				self.set_instrument(channels[x], i)
			else:
				self.set_instrument(channels[x], 1)

		
		current_bar = 0
		max_bar = len(tracks[0])

		# Play the bars
		while keep_playing_func and current_bar < max_bar:
			playbars = []
			for tr in tracks:
				playbars.append(tr[current_bar])
			if not self.play_Bars(playbars, channels):
				return False
			current_bar += 1

		return True
			

	def play_Composition(self, composition, channels = None, keep_playing_func = True):
		"""Plays a Composition object."""

		if channels == None:
			channels = map(lambda x: x + 1, range(len(composition.tracks)))
		return self.play_Tracks(composition.tracks, channels, keep_playing_func)


	## MIDI CONTROLLER TYPE 'SHORTCUTS'

	def modulation(self, channel, value):
		"""Sets the modulation"""
		return self.control_change(channel, 1, value)

	def main_volume(self, channel, value):
		"""Sets the main volume."""
		return self.control_change(channel, 7, value)

	def pan(self, channel, value):
		"""Sets the panning."""
		return self.control_change(channel, 10, value)


midi = MidiSequencer()

def init(sf2):
	"""This function needs to be called before you can have any \
audio. The sf2 argument should be the location of a valid soundfont 
file. Returns True on success, False on failure."""
	global midi
	midi.start_audio_output()
	return midi.load_sound_font(sf2)


def play_Note(note, channel = 1, velocity = 100):
	"""Sends a Note object as midi signal to the fluidsynth server. \
The channel and velocity can be set as Note attributes as well. If that's \
the case those values take presedence over the ones given here as function \
arguments.
{{{
>>> n = Note("C", 4)
>>> n.channel = 9
>>> n.velocity = 50
>>> FluidSynth.play_Note(n)
}}}"""
	return midi.play_Note(note, channel, velocity)


def stop_Note(note, channel = 1, velocity = 100):
	"""Stops the Note playing at channel."""
	return midi.stop_Note(note, channel)


def play_NoteContainer(nc, channel = 1, velocity = 100):
	"""Plays the Notes in the NoteContainer nc."""
	return midi.play_NoteContainer(nc, channel, velocity)

def stop_NoteContainer(nc, channel = 1):
	"""Stops playing the notes in NoteContainer nc."""
	return midi.stop_NoteContainer(nc, channel)

def play_Bar(bar, channel = 1, bpm = 120):
	"""Plays a Bar object."""
	return midi.play_Bar(bar, channel, duration)

def play_Bars(bars, channels, bpm = 120):
	"""Plays a list of bars on the given list of channels."""
	return midi.play_Bars(bars, channels)

def play_Track(track, channel = 1):
	"""Plays a Track object."""
	return midi.play_Track(track, channel)

def play_Tracks(tracks, channels):
	"""Plays a list of Tracks on the given list of channels."""
	return midi.play_Tracks(tracks, channels)

def play_Composition(composition, channels = None):
	"""Plays a composition."""
	return midi.play_Composition(composition, channels)

def control_change(channel, control, value):
	"""Sends a control change event on channel."""
	return midi.control_change(channel, control, value)


def set_instrument(channel, midi_instr):
	"""Sets the midi instrument on channel."""
	return midi.set_instrument(channel, midi_instr)

def stop_everything():
	"""Stops all the playing notes on all channels"""
	return midi.stop_everything()

def modulation(channel, value):
	return midi.modulation(channel, value)

def pan(channel, value):
	return midi.pan(channel, value)

def main_volume(channel, value):
	return midi.main_volume(channel, value)

def enable_reverb():
	return midi.write("reverb on\nrev_setroomsize 1\n")

def disable_reverb():
	return midi.write("reverb off\n")

def set_instrument(channel, instr):
	return midi.set_instrument(channel, instr)