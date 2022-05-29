import concurrent.futures
import logging
import queue
import random
import threading
import time

from polyphonizer import Polyphonizer
from dac import MCP4728
from smbus import SMBus
from midi_client import MidiClient
from midi_server import Midi_Host

def producer(queue, event, midi_server):
    """Pretend we're getting a number from the network."""
    while not event.is_set():
        act, message = midi_server.handle_midi()
        if act:
            logging.info("Producer got message: %s", message)
            queue.put(message)

    logging.info("Producer received event. Exiting")

def consumer(queue, event, midi_client):
    """Pretend we're saving a number in the database."""
    while not event.is_set() or not queue.empty():
        try:
            message = queue.get()
            logging.info(
                "Consumer storing message: %s (size=%d)", message, queue.qsize()
            )
            midi_client.process(message)
        except Exception as e:
            print("******************************")
            print("******************************")
            print("******************************")
            print("********ERROR*****************")
            print("******************************")
            print("******************************")
            print("******************************")
            print(e)
        
    logging.info("Consumer received event. Exiting")

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    pipeline = queue.Queue(maxsize=10)
    event = threading.Event()

    dac = MCP4728(SMBus(1), 0x60)
    poly = Polyphonizer(dac, None)
    client = MidiClient(poly) 

    server = Midi_Host()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(producer, pipeline, event, server)
        executor.submit(consumer, pipeline, event, client)
        
        logging.info("Main: about to set event")
        try:
            while(1):
                time.sleep(0.1)
        except:
            event.set()
            exit()
