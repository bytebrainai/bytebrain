# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio


class PubSub:
    def __init__(self):
        self.topic_subscribers = {}
        self.message_queue = asyncio.Queue()
        self.shutdown_event = asyncio.Event()

    async def publish(self, topic, message):
        # Publish a message to all subscribers of the given topic
        await self.message_queue.put((topic, message))
        await asyncio.gather(*[subscriber(message) for subscriber in self.topic_subscribers.get(topic, set())])

    async def subscribe(self, topic, subscriber):
        # Add a new subscriber to the given topic
        if topic not in self.topic_subscribers:
            self.topic_subscribers[topic] = set()
        self.topic_subscribers[topic].add(subscriber)

    async def unsubscribe(self, topic, subscriber):
        # Remove a subscriber from the given topic
        if topic in self.topic_subscribers:
            self.topic_subscribers[topic].discard(subscriber)

    async def run(self):
        while not self.shutdown_event.is_set():
            # Wait for a message or the shutdown event
            await asyncio.wait([self.message_queue.get(), self.shutdown_event.wait()],
                               return_when=asyncio.FIRST_COMPLETED)

            # Process messages if available
            while not self.message_queue.empty():
                topic, message = await self.message_queue.get()
                print(f"Received on topic '{topic}': {message}")

    async def shutdown(self):
        # Set the shutdown event
        self.shutdown_event.set()
        # Wait for the run method to complete
        await asyncio.gather(
            *{subscriber for subscribers in self.topic_subscribers.values() for subscriber in subscribers})


async def subscriber1(message):
    print(f"Subscriber 1 received: {message}")
    await asyncio.sleep(2)
    print("Subscriber 1 done processing")


async def subscriber2(message):
    print(f"Subscriber 2 received: {message}")
    await asyncio.sleep(1)
    print("Subscriber 2 done processing")


async def main():
    pubsub = PubSub()

    # Subscribe to topics
    await pubsub.subscribe("topic1", subscriber1)
    await pubsub.subscribe("topic2", subscriber2)

    # Publish messages to topics
    await pubsub.publish("topic1", "Hello, Topic 1!")
    await pubsub.publish("topic2", "Hello, Topic 2!")

    # Wait for a while to simulate other asynchronous tasks
    await asyncio.sleep(3)

    # Unsubscribe and shutdown
    await pubsub.unsubscribe("topic1", subscriber1)
    await pubsub.unsubscribe("topic2", subscriber2)
    await pubsub.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
