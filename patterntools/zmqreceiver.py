import zmq
import numpy as np
import matplotlib.pyplot as plt

# helper function to go from number of bits
# to numpy data type
def to_dtype(n_bits):
    if n_bits == 8:
        return np.uint8
    elif n_bits == 16:
        return np.uint18
    elif n_bits == 32:
        return np.uint32


class ZmqReceiver:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.connect()

    def receive_one_frame(self):
        header = self.socket.recv_json()
        print(header["data"],header["frameIndex"])
        #print(header)
        if header["data"]>0:
            buff = self.socket.recv()
            #print(len(buff),to_dtype(header["bitmode"]))
            data = np.frombuffer(buff, dtype=to_dtype(header["bitmode"]))
            print("ok")
            return data, header
        else:
            return None, header


    def disconnect(self):
        self.socket.disconnect(self.endpoint)

    def connect(self):
        self.socket.connect(self.endpoint)
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")

    def close(self):
        # This can normally be left to the garbage collector
        self.disconnect()
        self.context.destroy()
