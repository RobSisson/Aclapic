import asyncio, random, aiohttp
import janus

async def process(token):
    return print(token*token)

async def rnd_sleep(t):
    # sleep for T seconds on average
    await asyncio.sleep(t * random.random() * 2)


async def producer(queue):
    while True:
        # produce a token and send it to a consumer
        token=random.random()
        print(f'produced {token}')
        if token<.05:
            break
        await queue.put(token)
        await rnd_sleep(.1)



async def consumer(queue):
    while True:
        token = await queue.get()
        try:
            # this uses aiohttp or whatever
            await process(token)
        except aiohttp.ClientError as e:
            print(f"Error processing token {token}: {e}")
            # If it makes sense, return the token to the queue to be
            # processed again. (You can use a counter to avoid
            # processing a faulty token infinitely.)
            #await queue.put(token)
        queue.task_done()
        print(f'consumed {token}')


async def main():
    queue=asyncio.Queue()

    # fire up the both producers and consumers
    producers=[asyncio.create_task(producer(queue))
               for _ in range(3)]
    consumers=[asyncio.create_task(consumer(queue))
               for _ in range(10)]

    # with both producers and consumers running, wait for
    # the producers to finish
    await asyncio.gather(*producers)
    print('---- done producing')

    # wait for the remaining tasks to be processed
    await queue.join()

    # cancel the consumers, which are now idle
    for c in consumers:
        c.cancel()


asyncio.run(main())
