import time
import os
import traceback
import time
import sys
import glob
import serial
from serial.tools.list_ports import comports


import pygame.midi as midi
from midi_messages import *


class Midi_Host:
    def __init__(self):
        self.connections = []
        midi.init()
        self.try_connect_devices()
        
    def try_connect_devices(self):
        for p in range(midi.get_count()):
            found = False
            
            devInfo = midi.get_device_info(p)
            if devInfo[2] != 1:
                continue # not an Input

            print(f"dev {p}: {devInfo})")
            
            try: 
                dev = midi.Input(p) 
            except:
                continue
            for c in self.connections:
                    if c == dev:
                            found = True
                            break
            if not found:
                self.connections.append(dev)


    def handle_midi(self):

        act = False
        message = None
        for idx, conn in enumerate(self.connections):
            try:
                if conn.poll():
                    r = conn.read(1)
                    print(f"got: {r}") 
                    act = True
                    message_contents = r[0][0][1:]
                    message_type = MidiType(r[0][0][0])
                    timestamp = r[0][1]
                    
                    # Convert to MidiMessage objects
                    if message_type == MidiType.NOTE_ON:
                        message = KeyPressMidiMessage(
                                raw_type = message_type,
                                channel = message_contents[2],
                                timestamp = timestamp,
                                on = True,
                                velocity = message_contents[1],
                                note = message_contents[0]
                                )

                    if message_type == MidiType.NOTE_OFF:
                        message = KeyPressMidiMessage(
                                raw_type = message_type,
                                channel = message_contents[2],
                                timestamp = timestamp,
                                on = False,
                                velocity = message_contents[1],
                                note = message_contents[0]
                                )

                    if message_type == MidiType.CONTROL_CHANGE:
                        message = ControlChangeMidiMessage(
                                raw_type = message_type,
                                channel = message_contents[2],
                                timestamp = timestamp,
                                control = message_contents[0],
                                value = message_contents[1]
                                )                 
                    print(message)
            except Exception as e:
                print("Connection lost to {}".format(conn))
                print(e)
                del self.connections[idx]
                traceback.print_exc()
        return (act, message)

    def start(self):
        while(1):
            try:
                if not self.handle_midi():
                    if len(self.connections) == 0:
                        time.sleep(1)
                    
            except Exception as e:
                print("exception!")
                traceback.print_exc()
                time.sleep(1)


if __name__ == '__main__':
    mh = Midi_Host()
    mh.start()

