# TODO: change to a deque instead of a list


from dataclasses import dataclass

@dataclass
class NoteChannelPair:
    """ Pairing nof note and DAC/GPIO channels """
    note: int
    channel : int


class Polyphonizer:
    """ Turns a series of notes into a polyphonic CV output """    
    def __init__(self, dac, gpio):
        """ Constructor
            
            dac -- DAC for CV signals
            gpio -- GPIOs for gate signals

        """
        # assert dac.channels == gpio.channels #TBD

        self.dac = dac
        self.gpio = gpio
        self.buf = [] # note, dac channel pairs
        self.filled_channels = 0 # Number of channels used up
        self.max_channels = dac.channels # maximum number of channels should be min(da.channels, gpio.channels)

    def note_on(self, note):
        """ Turns on a note 

            note -- midi note to turn on
        """
        for iPair in self.buf:
            if iPair.note == note:
                return # already on

        if self.filled_channels == self.max_channels:
            gone_note = self.buf.pop(0) # note that was last updated use it's channel 
            self.buf.append(NoteChannelPair(note, gone_note.channel))
            self.dac.set(gone_note.channel, note)
            # don't change GPIO, don't change filled_channels
            return 

        if self.filled_channels != self.max_channels:
            # find a channel that isn't used and use it
            channel = None
            for iChannel in range(self.max_channels):
                found = True
                for iPair in self.buf:
                    if iChannel == iPair.channel:
                        found = False

                if found:
                    channel = iChannel
                    break

            if channel == None:
                raise # couldn't find a free channel, this shouldn't happen
            self.buf.append(NoteChannelPair(note, channel))
            self.dac.set(channel, note)
            self.filled_channels += 1
            # self.gpio.set(channel, 1)

    def note_off(self, note):
        """ Turn off a note

            note -- midi note to turn off
        """
        if self.filled_channels == 0:
            return # no channels to turn off

        for iPair in self.buf:
            # if it is not in the buffer, it is already off
            if iPair.note == note:
                self.buf.remove(iPair)
                self.dac.set(iPair.channel, 0) # turn off DAC channel, should I do this?
                # self.gpio.set(channel, 0) # definitley need to do this
                self.filled_channels -= 1


if __name__ == "__main__":
        from dac import MCP4728
        from smbus import SMBus
        from time import sleep

        dac = MCP4728(SMBus(1), 0x60)
        poly = Polyphonizer(dac, None)
        
        clear = False

        while True:
            for iNote in range(4096):
                poly.note_on(iNote)

                if iNote % 4 == 0:
                    if clear: # Test clearing ech channel
                        for iChannel in range(poly.max_channels):
                            poly.note_off(iNote)

            clear = not clear
