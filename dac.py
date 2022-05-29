class Dac:
    """ DAC base class """

    class channelNotFound(Exception):
        """ Thrown if channel not found on DAC """
        pass

    def __init__(self, bits, channels):
        """ Constructor 

            bits -- Number of bits of DAC resolution
            channels -- Number of channels the DAC has
        """
        self.bits = bits # Number of bits, set by subclass
        self.channels = channels # Number of DAC channels, set by subclass
        self.maxval = 0 # All 1s
        for iBit in range(self.bits):
            self.maxval |= 1 << iBit
    
    def set(self, channel, value):
        """ Set a value for a specific channel 
        
        channel -- Channel to set the value of
        value -- Value to set the channel to

        """ 
        pass
    
    def get(self, channel):
        """ Return the value of a specific channel 

            channel -- Channel to get the value of
        """
        pass

    def checkChannel(self, channel):
        """ Raises `channelNotFound` exception if channel does not exist 

            channel -- Channel to check
        """
        if channel < 0 or channel > self.channels-1:
            raise channelNotFound

    def clipValue(self, value):
        """ returns the value clipped between 0 and max value of DAC 

            value -- Value to clip
        """
        return value & self.maxval


class MCP4728(Dac):
    """ MCP4728 class """
    
    def __init__(self, i2cBus, address):
        """ Constuctor 

            i2cBus -- i2c bus to be used
            address -- i2c address of MCP4728
        """
        self.bus = i2cBus
        self.address = address
        super().__init__(12, 4)

    def set(self, channel, value):
        """ Inherit documentation """
        self.checkChannel(channel)
        clippedVal = self.clipValue(value)
        data = []
        data.append(0x40 | channel << 1) # Multi-write no EEPROM, channel, UDAC = 0
        data.append(value >> 8) # VREF = 0, PD = 0, G = 0, first 4 bits of value
        data.append(value & 0xFF) # last 8 bits of data
        self.bus.write_i2c_block_data(self.address, data[0], data[1:])

    def get(self, channel):
        """ Inherit Documentation """
        self.checkChannel(channel)
        bytes_per_channel = 6
        contents = self.bus.read_i2c_block_data(self.address, 0) # that 0 does nothing the DAC just dumps all its guts
        msb = contents[channel*bytes_per_channel+1] & 0x0F
        lsb = contents[channel*bytes_per_channel+2] & 0xFF
        return (msb << 8) | lsb

if __name__ == "__main__":
    import smbus
    import time
    import math

    class sineGen:
        """ Sine wave generator """ 
        
        def __init__(self, amplitude, phase, period, offset):
            """ Constructor 
                amplitude -- amplitude of sine wave
                phase -- phase of sine wave (in radians)
                period -- number of points in wave
                offset -- offset of sine wave
            """
            self.amp = amplitude
            self.phase = phase
            self.per = period
            self.offset = offset
            self.delta = 2 * math.pi / period # steps per period
            self.counter = self.phase / self.delta # starting value

        def next(self):
            """ Returns next value of sine wave """
            base_val = math.sin(self.counter*self.delta)
            self.counter = self.counter+1 % self.per
            return self.amp * base_val + self.offset



    dacMCP4728 = MCP4728(smbus.SMBus(1), 0x60)
    sin0 = sineGen(2047, 0*(2*math.pi/4), 4096, 2048)
    sin1 = sineGen(2047, 1*(2*math.pi/4), 4096, 2048)
    sin2 = sineGen(2047, 2*(2*math.pi/4), 4096, 2048)
    sin3 = sineGen(2047, 3*(2*math.pi/4), 4096, 2048)
    print(dacMCP4728.__dict__)
    while True:
            val0 = int(sin0.next())
            val1 = int(sin1.next())
            val2 = int(sin2.next())
            val3 = int(sin3.next())
            dacMCP4728.set(0, val0)
            dacMCP4728.set(1, val1)
            dacMCP4728.set(2, val2)
            dacMCP4728.set(3, val3)



