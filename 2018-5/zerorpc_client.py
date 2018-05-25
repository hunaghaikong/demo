import zerorpc

c = zerorpc.Client()
c.connect("tcp://127.0.0.1:8001")

for item in c.streaming_range(10, 100, 1):
    try:
        print(item)
    except Exception as exc:
        print(exc)


class RPCProxy(object):
    def __init__(self, connect_to=None, context=None, timeout=30, heartbeat=5, passive_heartbeat=False):
        self._client = zerorpc.Client(connect_to, context, timeout, heartbeat, passive_heartbeat)
        self.endpoint = connect_to
        self.context = context
        self.timeout = timeout
        self.heartbeat = heartbeat
        self.passive_heartbeat = passive_heartbeat

        def connect(self, endpoint, resolve=True):
            self.endpoint = endpoint
            return self._client.connect(endpoint, resolve)

        def bind(self, endpoint, resolve=True):
            self.endpoint = endpoint
            return self._client.bind(endpoint, resolve)

        def __call__(self, method, *args, **kwargs):
            if self._client._events._socket.closed:
                self._client = zerorpc.Client(self.endpoint, self.context, self.timeout,
                                              self.heartbeat, self.passive_heartbeat)
            try:
                result = self._client(method, *args, **kwargs)
                return result
            except zerorpc.exceptions.LostRemote as e:
                self._client.close()
                raise e
            except zerorpc.exceptions.TimeoutExpired as e:
                self._client.close()
                raise e

        def __getattr__(self, method):
            return lambda *args, **kargs: self(method, *args, **kargs)
