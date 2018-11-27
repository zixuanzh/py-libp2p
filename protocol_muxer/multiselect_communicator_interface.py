from abc import ABC, abstractmethod

"""
Communicator helper class that ensures both the client
and multistream module will follow the same protocol,
which is necessary for them to work
"""
class IMultiselectCommunicator(ABC):

    @abstractmethod
    def write(self, msg_str):
        """
        Write message to stream
        :param msg_str: message to write
        """
        pass

    @abstractmethod
    def read_stream_until_eof(self):
        """
        Reads message on stream until EOF
        """
        pass
