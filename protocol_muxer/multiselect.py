from .multiselect_muxer_interface import IMultiselectMuxer
from .multiselect_communicator import MultiselectCommunicator

MULTISELECT_PROTOCOL_ID = "/multistream/1.0.0"
PROTOCOL_NOT_FOUND_MSG = "na"

class Multiselect(IMultiselectMuxer):

    def __init__(self):
        self.handlers = {}

    def add_handler(self, protocol, handler):
        self.handlers[protocol] = handler

    async def negotiate(self, stream):
        # Create a communicator to handle all communication across the stream
        communicator = MultiselectCommunicator(stream)

        # Perform handshake to ensure multiselect protocol IDs match
        await self.handshake(communicator)

        # Read and respond to commands until a valid protocol ID is sent
        while True:
            # Read message
            command = await communicator.read_stream_until_eof()

            # Command is ls or a protocol
            if command == "ls":
                # TODO: handle ls command
                pass
            else:
                protocol = command
                if protocol in self.handlers:
                    # Tell counterparty we have decided on a protocol
                    await communicator.write(protocol)

                    # Return the decided on protocol
                    return protocol, self.handlers[protocol]
                # Tell counterparty this protocol was not found
                await communicator.write(PROTOCOL_NOT_FOUND_MSG)

    async def handshake(self, communicator):
        # TODO: Use format used by go repo for messages

        # Send our MULTISELECT_PROTOCOL_ID to other party
        await communicator.write(MULTISELECT_PROTOCOL_ID)

        # Read in the protocol ID from other party
        handshake_contents = await communicator.read_stream_until_eof()

        # Confirm that the protocols are the same
        if not self.validate_handshake(handshake_contents):
            raise MultiselectError("multiselect protocol ID mismatch")

        # Handshake succeeded if this point is reached

    def validate_handshake(self, handshake_contents):
        # TODO: Modify this when format used by go repo for messages
        # is added
        return handshake_contents == MULTISELECT_PROTOCOL_ID

class MultiselectError(ValueError):
    """Raised when an error occurs in multiselect process"""
