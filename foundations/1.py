import os 
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.1-8b-instant"

if not groq_api_key :
    print("API key missing")
    exit()


client = OpenAI(
    api_key=groq_api_key,
    base_url= "https://api.groq.com/openai/v1"
)

def get_reponce(client, query) :
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role" : "user", "content" : query}
        ]
    )

    result = response.choices[0].message.content

    print("query", query)
    print("result", result)
    print("============")

    return result



query = "what is 2*9, just resturn the number!"
query = get_reponce(client, query) + " now add 54 to it, just resturn the number!"
query = get_reponce(client, query) + " now divide it by 3, just resturn the number!"
query = get_reponce(client, query) + " now make a square of it, just resturn the number!"
query = get_reponce(client, query) + " now it with multiply -2, just resturn the number!"
