import zmq

class Flow(object):
    def __init__(self, context, endpoint, key, fieldset = []):
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.HWM, 10)
        self.socket.connect(endpoint)
        self.key = key

        if fieldset:
            for field in fieldset:
                self.socket.setsockopt(zmq.SUBSCRIBE,
                    "%s %s" % (key, field))
        else:
            self.socket.setsockopt(zmq.SUBSCRIBE, key)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            envelope, data = self.socket.recv_multipart(zmq.NOBLOCK)
        except zmq.ZMQError, e:
            raise StopIteration

        key, field, timestamp = envelope

        return (field, data)

class Client(object):
    def __init__(self, requests, export):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(requests)
        self.export = export

    def subscribe(self, uri, timeout, ttl):
        self.socket.send('loop %d %d %s' % (timeout, ttl, uri))
        result = self.socket.recv()
        
        if not result.startswith('e'):
            return Flow(self.context, sub_ep, result)
        else:
            raise RuntimeError(result)

    def unsubscribe(flow):
        self.socket.send('unloop %s' % flow.key)
        flow.socket.close()