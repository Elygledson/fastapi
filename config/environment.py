from dotenv import load_dotenv
import os

load_dotenv()

config = {
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'MONGODB_URI': os.getenv('MONGODB_URI'),
    'COLLECTION': os.getenv('COLLECTION')
}
