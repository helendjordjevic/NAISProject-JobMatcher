import os
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()  

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

client = OpenAI(api_key=OPENAI_API_KEY)

pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pc.Index(INDEX_NAME)

#try:
    #indexes = pc.list_indexes().names()  
    #if INDEX_NAME in indexes:
    #    print(f"Povezano! Index '{INDEX_NAME}' postoji.")
    #else:
    #    print(f"Povezano, ali index '{INDEX_NAME}' ne postoji još.")
#except Exception as e:
    #print(f"Greška pri konekciji: {e}")
