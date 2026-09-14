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
        # Shared asynchronous queue
        self.message_queue = asyncio.Queue()

    async def publish_message(self, topic, message):
        # Enqueue the message
        await self.message_queue.put({"topic": topic, "message": message})

    async def process_messages(self):
        while True:
            # Process all messages in the queue
            while not self.message_queue.empty():
                message = await self.message_queue.get()
                topic, message_data = message["topic"], message["message"]

                # Process the received message
                print(f"Received from '{topic}': {message_data}")

            # Wait for some time before checking for new messages
            await asyncio.sleep(5)

    async def run(self):
        # Run the message processing coroutine concurrently
        await asyncio.gather(self.process_messages())


if __name__ == "__main__":
    pubsub = PubSub()


    async def publish_task():
        try:
            while True:
                # Publish a sample message to the "example_topic"
                message_data = {"data": "Hello, subscribers!"}
                await pubsub.publish_message("example_topic", message_data)

                await asyncio.sleep(5)

        except KeyboardInterrupt:
            print("Publisher disconnected.")

    async def foo():
        return await asyncio.gather(pubsub.run(), publish_task())

    asyncio.run(foo())
