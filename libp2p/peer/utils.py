from multiaddr import Multiaddr
from multiaddr.protocols import protocol_with_code, read_varint_code

def size_for_addr(proto, buf):
    if proto.size >= 0:
        return proto.size // 8
    size, num_bytes_read = read_varint_code(buf)
    return size + num_bytes_read

def bytes_split(buf):
    ret = []
    while buf:
        code, num_bytes_read = read_varint_code(buf)
        proto = protocol_with_code(code)
        size = size_for_addr(proto, buf[num_bytes_read:])
        length = size + num_bytes_read
        ret.append(buf[:length])
        buf = buf[length:]
    return ret

def split(_multiaddr):
    """Return the sub-address portions of a multiaddr"""
    addrs = []
    splitted_addrs = bytes_split(_multiaddr.to_bytes())
    for addr in splitted_addrs:
        addrs.append(Multiaddr(addr))
    return addrs


def join(multiaddrs):
    addr_list = []
    for addr in multiaddrs:
        addr_list.append(addr.to_bytes())
    return Multiaddr(b''.join(addr_list))
