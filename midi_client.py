from midi_messages import *

class MidiClient:
    """ Midi message client, glue to polyphonzer"""

    def __init__(self, poly):
        self.poly = poly
        self.scale = int(self.poly.dac.maxval/128)

    def process(self, msg):
        msg_type = type(msg)

        if msg_type is KeyPressMidiMessage:
            note = msg.note
            if msg.on:
                self.poly.note_on(note*self.scale)
            else:
                self.poly.note_off(note*self.scale)
