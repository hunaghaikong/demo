import zerorpc
import time

class StreamingRPC(object):
    @zerorpc.stream
    def streaming_range(self, fr, to, step):
        for i in range(fr, to, step):
            try:
                yield i
                time.sleep(1)
            except Exception as exc:
                print(exc)

s = zerorpc.Server(StreamingRPC())
s.bind("tcp://0.0.0.0:8001")
s.run()
