'''
2020, Copyright Ilya Kurinov
LUT University
============================
This is a module for communicating with RL algorithm.
'''

import zmq
import json

class Worker:

    def __init__(self, port):
        
        self.port = port
        
        # Create zmq socket on specific port
        self.context = zmq.Context()
        self.context = self.context or zmq.Context.instance()
        self.worker = self.context.socket(zmq.REQ) 
        self.worker.connect("tcp://localhost:{}".format(self.port))


    def recv(self):
        b_request = self.worker.recv() 
        return json.loads(b_request)
    
    def send (self, reply):
        b_reply = json.dumps(reply).encode()
        self.worker.send(b_reply)
        pass

    def communicate(self, msg):

        self.send(msg)
        reply = self.recv()

        return reply