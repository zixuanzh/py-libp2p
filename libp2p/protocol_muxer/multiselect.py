from .multiselect_muxer_interface import IMultiselectMuxer
from .multiselect_communicator import MultiselectCommunicator


MULTISELECT_PROTOCOL_ID = "/multistream/1.0.0"
PROTOCOL_NOT_FOUND_MSG = "na"


class Multiselect(IMultiselectMuxer):
    """
    Multiselect module that is responsible for responding to
    a multiselect client and deciding on
    a specific protocol and handler pair to use for communication
    """

    def __init__(self):
        self.handlers = {}

    def add_handler(self, protocol, handler):
        """
        Store the handler with the given protocol
        :param protocol: protocol name
        :param handler: handler function
        """
        self.handlers[protocol] = handler

    async def negotiate(self, stream):
        print("negotiate")
        """
        Negotiate performs protocol selection
        :param stream: stream to negotiate on
        :return: selected protocol name, handler function
        :raise Exception: negotiation failed exception
        """
        # Create a communicator to handle all communication across the stream
        communicator = MultiselectCommunicator(stream)

        print("sender pre handshake")

        # Perform handshake to ensure multiselect protocol IDs match
        await self.handshake(communicator)

        print("sender post handshake")

        # Read and respond to commands until a valid protocol ID is sent
        while True:
            # Read message
            command = await communicator.read_stream_until_eof()
            print("sender command " + command)

            # Command is ls or a protocol
            if command == "ls":
                # TODO: handle ls command
                pass
            else:
                protocol = command
                print("sender checking protocol in handlers")
                if protocol in self.handlers:
                    # Tell counterparty we have decided on a protocol
                    print("sender writing protocol " + protocol)
                    await communicator.write(protocol)
                    print("sender protocol written")

                    # Return the decided on protocol
                    return protocol, self.handlers[protocol]
                print("sender protocol not found")
                # Tell counterparty this protocol was not found
                await communicator.write(PROTOCOL_NOT_FOUND_MSG)

    async def handshake(self, communicator):
        """
        Perform handshake to agree on multiselect protocol
        :param communicator: communicator to use
        :raise Exception: error in handshake
        """

        # TODO: Use format used by go repo for messages

        print("sender pre write " + MULTISELECT_PROTOCOL_ID)

        # Send our MULTISELECT_PROTOCOL_ID to other party
        await communicator.write(MULTISELECT_PROTOCOL_ID)

        print("sender pre read")

        # Read in the protocol ID from other party
        handshake_contents = await communicator.read_stream_until_eof()

        print("sender pre validate " + handshake_contents)

        # Confirm that the protocols are the same
        if not validate_handshake(handshake_contents):
            print("sender multiselect protocol ID mismatch")
            raise MultiselectError("multiselect protocol ID mismatch")

        # Handshake succeeded if this point is reached


def validate_handshake(handshake_contents):
    """
    Determine if handshake is valid and should be confirmed
    :param handshake_contents: contents of handshake message
    :return: true if handshake is complete, false otherwise
    """

    # TODO: Modify this when format used by go repo for messages
    # is added
    return handshake_contents == MULTISELECT_PROTOCOL_ID


class MultiselectError(ValueError):
    """Raised when an error occurs in multiselect process"""
