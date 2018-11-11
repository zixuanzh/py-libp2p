import asyncio
from .stream_interface import IStream

class Stream(IStream):

    def __init__(self, peer_id, multi_addr, connection):
        IStream.__init__(self, peer_id, multi_addr, connection)
        self.peer_id = peer_id

        self.multi_addr = multi_addr

        self.stream_ip = multi_addr.get_protocol_value("ip4")
        self.stream_port = multi_addr.get_protocol_value("tcp")

        self.reader = connection.reader
        self.writer = connection.writer

        # TODO should construct protocol id from constructor
        self.protocol_id = None

    def get_protocol(self):
        """
        :return: protocol id that stream runs on
        """
        return self.protocol_id

    def set_protocol(self, protocol_id):
        """
        :param protocol_id: protocol id that stream runs on
        :return: true if successful
        """
        self.protocol_id = protocol_id
