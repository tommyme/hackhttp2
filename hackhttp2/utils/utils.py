import contextlib
import time

@contextlib.contextmanager
def timer(name=""):
    st = time.time()
    yield
    info(f"{name} %.3f" % (time.time()-st))

def headers_raw_to_dict(headers_raw):

    if headers_raw is None:
        return None
    headers = headers_raw.splitlines()
    headers_tuples = [header.split(":", 1) for header in headers]

    result_dict = {}
    for header_item in headers_tuples:
        if not len(header_item) == 2:
            continue

        item_key = header_item[0].strip()
        item_value = header_item[1].strip()
        result_dict[item_key] = item_value

    return result_dict