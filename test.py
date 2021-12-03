from hackhttp2 import hackhttp
hh = hackhttp()
hh.globals.https = True
hh.globals.kwargs = {
    "verify":False,
}
hh.globals.set_proxy("127.0.0.1:8080")


# req = hh.load_raw("/Users/flag/misc/messages/awd.txt")
# resp = req.send().text

# the following code use "application/json"
# but in burp the body is "a=1"
resp = hh.globals.client.post("http://www.baidu.com",
                              headers={"Content-Type":"application/json"},
                              data={"a":1},
                              proxies=hh.globals.proxies)
