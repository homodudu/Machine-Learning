import os.path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

load_dotenv()

oa = OpenAI()
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index_name = 'pe-tax-info'

# We'll use this function to embed the chunk
# We'll also use it to embed the question for query
def embed_chunks(text):

    response = oa.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )

    # print(response)

    embedding = response.data[0].embedding

    return embedding
