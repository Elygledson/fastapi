from dotenv import load_dotenv
import os

load_dotenv()

config = {
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
}
