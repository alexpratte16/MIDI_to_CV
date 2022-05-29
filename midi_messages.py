from dataclasses import dataclass
from enum import Enum

class MidiType(Enum):
    """ Easy reference for MIDI message types"""
    NOTE_ON = 144
    NOTE_OFF = 128
    CONTROL_CHANGE = 176


@dataclass
class MidiMessage:
    """ Midi message base class """
    raw_type : MidiType # raw number of message type
    channel : int # channel that the message came from
    timestamp : int # timestamp of message
    

@dataclass
class KeyPressMidiMessage(MidiMessage):
    """ Note on or off message """
    on : bool # Note on or off
    velocity : int # velocity
    note : int # Note pressed or released

@dataclass
class ControlChangeMidiMessage(MidiMessage):
    """ Control change message """
    control : int # Which control changed
    value : int # value of the control



