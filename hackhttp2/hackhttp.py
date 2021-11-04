import requests as r
import urllib
import urllib3
from http.cookies import SimpleCookie
from copyheaders import headers_raw_to_dict
from requests_toolbelt.adapters import source
import urllib3
import netifaces
from threading import Thread
import contextlib
import os
import httpx
import asyncio
import time
import netifaces
from pwn import info, success, error, warnings

urllib3.disable_warnings()
# TODO choose long conn & short conn in hackhttp
# TODO conn pool
# TODO proxy pool
# TODO migrating global settings in hackhttp TO self.globals
# TODO use fixed num of threads

j = os.path.join

def eth2ip(interface: str) -> (bool, str):
    """
    Get interface ip by device name

    :param interface: network interface
    :return:  statue, ip
    """
    ifs = netifaces.interfaces()
    if interface in ifs:
        if netifaces.AF_INET in netifaces.ifaddresses(interface):
            ip_matrix = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]
            info(f"using [{interface}]: {ip_matrix['addr']}")
            return ip_matrix['addr']
        else:
            error('Interface Do Not Have Ipv4 Address!')
    else:
        error('Interface Not Exists!')

class Request:
    def __init__(self, globals, base_args):
        self.globals = globals
        self.__dict__.update(base_args)
        self.kwargs = {}
        self.hook_func = None
        
    def _send(self):
        resp = self.globals.client.request(self.method, self.url, 
                headers=self.headers, params=self.params,
                cookies=self.cookies, data=self.data, 
                **self.kwargs)
        return resp

    async def _send_async(self):
        resp = await self.globals.client.request(self.method, self.url, 
                headers=self.headers, params=self.params,
                cookies=self.cookies, data=self.data, 
                **self.kwargs)
        return resp

    def send(self):
        self.apply_global_settings()
        resp = self._send()
        resp.cookies_dict = r.utils.dict_from_cookiejar(resp.cookies)
        if self.hook_func:
            self.hook_func(resp)          
        return resp
    
    async def send_async(self):
        self.apply_global_settings()
        resp = await self._send_async()
        # resp.cookies_dict = r.utils.dict_from_cookiejar(resp.cookies)
        if self.hook_func:
            self.hook_func(resp)          
        return resp

    def apply_global_settings(self):
        
        self.headers.update({"Connection":"Keep-alive"}) if self.globals.long_conn else self.headers.update({"Connection":"close"})
        if self.cookies and self.headers.get("Cookie",""): # remove cookie in header or it'll be recovered by headers
            del self.headers["Cookie"]
        self.kwargs.update(self.globals.kwargs)
        self.cookies.update(self.globals.cookies)
        self.headers.update(self.globals.headers)

class hack_cookie(SimpleCookie):
    def __init__(self, raw):
        SimpleCookie.__init__(self)
        self.load(raw)
        self.dict = {i:j.value for i,j in self.items()}

class Globals:
    cookies = {}
    headers = {}
    kwargs = {}
    long_conn = True
    https=True
    root=""
    client = r.Session() # client.trust_env = True # by default
    def set_proxy(self, proxies):
        """
        input string or dict
        """
        if type(proxies) == str:
            proxies = {
                "http": f"http://{proxies}",
                "https": f"https://{proxies}"
            }
        self.kwargs.update({"proxies":proxies})

    def via_eth(self, eth="", ip=""):
        """
        input eth or ip.
        """
        if eth or ip:
            if eth:
                ip = eth2ip(eth)
            target = source.SourceAddressAdapter(ip)
            self.client.mount('http://', target)
            self.client.mount('https://', target) 

class Pool_Thread:
    def __init__(self):
        self.pool = []
    
    def add_reqs(self, reqs:list):
        # hook_func can be used in thread mode, 
        # or there will be nothing can be return
        count = 0
        for req in reqs:
            if not req.hook_func:
                count += 1 
        if count:
            print(f"{count} of {len(reqs)} have no hook_func, you will lost resp of them.")
        for req in reqs:
            self.pool.append(Thread(target=req.send))


    def start_all(self):
        [i.start() for i in self.pool]
    
    def join_all(self):
        [i.join() for i in self.pool]

class Pool_Coroutine:
    def __init__(self):
        self.pool = []

    def add_reqs(self, reqs):
        for req in reqs:
            self.pool.append(req.send_async())
    
    def start_all(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(self.pool))
        loop.close()

class hackhttp():
    def __init__(self):
        self.globals = Globals()

    def load_raw(self, path):
        with open(j(self.globals.root, path),"r") as f:
            method, path_qs, ver_http = f.readline().strip().split()
            content = f.read()
        headers = headers_raw_to_dict(content)
        
        # cookie
        cookies = hack_cookie(headers.get("Cookie","")).dict
        # params
        path, qs = urllib.parse.splitquery(path_qs)
        params = urllib.parse.parse_qs(qs)
        # url
        Host = headers.get("Host")
        base_url = f"https://{Host+path}" if self.globals.https else f"http://{Host+path}"
        # data
        data = ""
        if method == "POST":
            lines = content.split("\n")
            url_encode_data = lines[lines.index("")+1]
            content_type = headers.get("Content-Type","")
            if content_type == 'application/x-www-form-urlencoded':
                data = dict([item.split('=') for item in url_encode_data.split('&')])

        args_dict = {
            "method":   method,
            "url":      base_url,
            "headers":  headers,
            "params":   params,
            "data":     data,
            "cookies":  cookies
        }
        return Request(self.globals, args_dict)

    @contextlib.contextmanager
    def create_pool_thread(self):
        yield Pool_Thread()

    @contextlib.contextmanager
    def create_pool_coroutine(self):
        self.globals.client = httpx.AsyncClient()
        yield Pool_Coroutine()
        self.globals.client = r.Session()

