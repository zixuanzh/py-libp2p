import asyncio

class OrderedQueue():
    """
    asyncio.queue wrapper that delivers messages in order of subsequent sequence numbers,
    so if message 1 and 3 are received and the following get calls occur:
    get(), get(), get()
    the queue will deliver message 1, will wait until message 2 is received to deliver message 2,
    and then deliver message 3
    """

    def __init__(self):
        self.last_gotten_seqno = 0
        self.queue = asyncio.PriorityQueue()
        self.task = None

    async def put(self, item):
        """
        :param item: put item tuple (seqno, data) onto queue
        """
        seqno = item[0]
        await self.queue.put(item)
        if self.last_gotten_seqno + 1 == seqno and self.task is not None:
            # Allow get future to return the most recent item that is put
            self.task.set()

    async def get(self):
        """
        Get item with last_gotten_seqno + 1 from the queue
        :return: (seqno, data)
        """
        if self.queue.qsize() > 0:
            front_item = await self.queue.get()

            if front_item[0] == self.last_gotten_seqno + 1:
                self.last_gotten_seqno += 1
                return front_item
            # Put element back as it should not be delivered yet
            await self.queue.put(front_item)

        # Wait until item with subsequent seqno is put on queue
        self.task = asyncio.Event()
        await self.task.wait()
        item = await self.queue.get()

        # Remove task
        self.task = None

        self.last_gotten_seqno += 1

        return item
