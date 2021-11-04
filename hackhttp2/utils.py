import netifaces
from pwn import error, info
import contextlib
import time
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

