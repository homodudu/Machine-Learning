import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

# you need to do a pip install of LangChain, you can just use the text splitter
# pip install -qU langchain-text-splitters
from langchain.text_splitter import RecursiveCharacterTextSplitter
from _embed_chunks import embed_chunks


load_dotenv()

oa = OpenAI()
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index_name = 'pe-tax-info'

# This will be used to retrieve chunks from Pinecone
# Default chunks to retrieve is 5
def retrieve_chunks(query=None, no_of_chunks=5):

    # The query is embedded before querying Pinecone
    embedding = embed_chunks(query)

    index = pc.Index(index_name)

    response = index.query(
        vector= embedding,
        top_k=no_of_chunks,
        include_metadata=True
    )

    retrieved_chunks = ""

    for match in response['matches']:

        retrieved_chunks += "________________________________\n"
        retrieved_chunks += "EXCERPT\n"
        retrieved_chunks += "-------\n"
        retrieved_chunks += match['metadata']['chunk'] + '\n'

    return retrieved_chunks
