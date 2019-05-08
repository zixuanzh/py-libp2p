import asyncio

"""
NOTE: ISSUE IS THAT THERE task IS BLOCKING SINCE IT IS WAITING ON SAME COROUTINE THAT 
WE ARE RUNNING ON
"""
class OrderedQueue():

    def __init__(self):
        self.last_gotten_seqno = 0
        self.queue = asyncio.PriorityQueue()
        self.task = None

    async def put(self, item):
        seqno = item[0]
        await self.queue.put(item)
        if self.last_gotten_seqno + 1 == seqno and self.task is not None:
            # Allow get future to return the most recent item that is put
            self.task.set()

    async def get(self):
        if self.queue.qsize() > 0:
            front_item = await self.queue.get()

            if front_item[0] == self.last_gotten_seqno + 1:
                self.last_gotten_seqno += 1
                return front_item
            else:
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
