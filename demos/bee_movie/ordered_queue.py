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
        # print("Put " + str(item))
        seqno = item[0]
        await self.queue.put(item)
        # print("Added to queue " + str(item))
        if self.last_gotten_seqno + 1 == seqno and self.task is not None:
            # Allow get future to return the most recent item that is put
            # print("Set called")
            self.task.set()

    async def get(self):
        if self.queue.qsize() > 0:
            front_item = await self.queue.get()

            if front_item[0] == self.last_gotten_seqno + 1:
                # print("Trivial get " + str(front_item))
                self.last_gotten_seqno += 1
                return front_item
            else:
                # Put element back as it should not be delivered yet
                # print("Front item put back 1")
                # print(str(self.last_gotten_seqno))
                # print(front_item[1])
                await self.queue.put(front_item)
                # print("Front item put back 2")

        # print("get 2")
        # Wait until 
        self.task = asyncio.Event()
        # print("get 3")
        await self.task.wait()
        # print("get 4")
        item = await self.queue.get()
        # print("get 5")
        # print(str(item) + " got from queue")

        # Remove task
        self.task = None

        self.last_gotten_seqno += 1

        return item