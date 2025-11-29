from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os 
import json

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

class Test_Agent :

    def __init__(self, client_info):
        self.client = OpenAI(api_key= client_info["api_key"], base_url= client_info["base_url"])
    
    def query(self, query_info):
        
        message = query_info['message']

        responce = self.client.chat.completions.create(
            model = query_info["model_name"],
            messages = message,
            )

        return responce.choices[0].message.content

    def eval_responces(self, query, agent_responce, client_info):
        inp = f"""Hey you are a Judge. There is a query asked to one auto generate model\n
                you have to judge and give answer is accepted or not\n 
                if not you can give your feedback\n\n
                
                query = {str(query)}\n\n

                agent responce = {str(agent_responce)}\n\n

                =======================================
                """

        responce = self.client.beta.chat.completions.parse(
            model = client_info["model_name"],
            messages = [{"role" : "user", "content" :inp}],
            # response_format= Evaluation,                                 # not supported by groq
        )
        return responce.choices[0].message.content


data = {"message" : [{"role" : "user", "content" : "what is the capital of INDIA? \n reply only capital name !!" }] , 
        "model_name" : "llama-3.1-8b-instant",
        "client_id" : "groq_1", 
        "api_key" : groq_api_key, 
        "base_url" : "https://api.groq.com/openai/v1"}

test_agent = Test_Agent(data)
agents_responce = test_agent.query(data)

print(agents_responce)

result = test_agent.eval_responces(data["message"][0]["content"], agents_responce, data)

print(f"result ->\n{result}")