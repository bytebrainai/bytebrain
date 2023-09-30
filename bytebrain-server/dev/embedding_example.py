from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.storage import LocalFileStore
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
underlying_embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

fs = LocalFileStore("./cache/")
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings, fs, namespace=underlying_embeddings.model
)


print(list(fs.yield_keys()))


text = """
In the heart of a bustling metropolis, the cityscape stretches as far as the eye can see, a concrete jungle where dreams are both made and broken. Skyscrapers pierce the heavens, their glass facades reflecting the sun's radiant rays. People from all walks of life traverse the labyrinthine streets, each with their own story to tell.

Amidst the cacophony of honking horns and hurried footsteps, street vendors hawk their wares, filling the air with the tantalizing aromas of sizzling street food. The city's parks provide a welcome respite from the urban hustle and bustle, where families gather for picnics and children play on swings beneath the shade of towering trees.

As day turns to night, the city undergoes a transformation. Neon lights and billboards illuminate the skyline, turning it into a shimmering tapestry of colors. The nightlife comes alive with music pouring out of bars and clubs, inviting revelers to dance the night away.

In the quieter corners of the city, historic landmarks stand as silent witnesses to centuries gone by. Ancient cathedrals, grand museums, and stately government buildings hold the secrets of the past, waiting to be discovered by those who seek a deeper connection to the city's heritage.

But beyond the glitz and glamour, the city has its share of challenges. Traffic jams snarl the streets during rush hour, and the constant hum of activity can leave its residents yearning for a moment of solitude. Yet, it is precisely these challenges that give the city its unique character and energy.

In this sprawling metropolis, the fusion of cultures and ideas is palpable. Different languages fill the air, and the cuisine is a global feast that tantalizes the taste buds. Diversity is celebrated, and the city thrives on the rich tapestry of its people.

Whether you're a newcomer, a long-time resident, or just passing through, this city has a way of leaving an indelible mark on your soul. It's a place where dreams are pursued with unwavering determination, where the past meets the present, and where the future is written one day at a time. This city, with all its complexities and contradictions, is a microcosm of the world, a place where life's journey unfolds in a myriad of ways."

Feel free to use this text for embedding or any other natural language processing task you have in mind.
"""
Chroma.from_documents(documents=[Document(page_content=text)], embedding=cached_embedder)
