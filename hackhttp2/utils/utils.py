import contextlib
import time

@contextlib.contextmanager
def timer(name=""):
    st = time.time()
    yield
    info(f"{name} %.3f" % (time.time()-st))