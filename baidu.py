from hackhttp.hackhttp import hackhttp
from pwn import  pause, success, info
import os
import requests as r
import time
import pyperclip as ppc
import logging
from http.client import HTTPConnection
import asyncio
import time
import httpx

# HTTPConnection.debuglevel = 1
logging.basicConfig(level="DEBUG")

def hook(resp):
    data.append(resp)

hh = hackhttp() 
# hh.globals.https=False
hh.globals.client.trust_env = False
hh.globals.root = "messages"
hh.globals.long_conn = False
hh.globals.kwargs.update({"allow_redirects":False})

data = []
req = hh.load_raw("baidu.txt")
req.hook_func = hook

ppc.copy(f'watch -n 0.1 "lsof -p {os.getpid()} | grep TCP"')

def test_coroutine(num):
    with hh.create_pool_coroutine() as p:
        p.add_reqs([req]*num)
        st = time.time()
        p.start_all()

    info(str(time.time()-st))

def test_thread(num):
    with hh.create_pool_thread() as p:
        p.add_reqs([req]*num)
        st = time.time()
        p.start_all()
        p.join_all()

    info(str(time.time()-st))

def test_origin(num):
    st = time.time()
    for i in range(num):
        req.send()
    info(str(time.time()-st))

def test_plain(num):
    st = time.time()
    for i in range(10):
        r.get("http://www.baidu.com/s?wd=python+PreparedRequest", allow_redirects=False)
    

time.sleep(3)
# test_thread(10) # 同时建立起多条连接
test_origin(10)
# test_coroutine(10) # 同时建立起多条连接


