
from dotenv import load_dotenv
from openai import OpenAI
import os 
import json

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

class Test_Agents :

    def __init__(self, clients_init):

        self.clients = {}    
        self.clients_map = {}
        self.clients_map_rev = {}

        for ind, data in enumerate(clients_init) :
            self.clients[ind] = OpenAI(api_key= data["api_key"], base_url= data["base_url"])
            self.clients_map[data["client_id"]] = ind
            self.clients_map_rev[ind] = data["client_id"]
    
    def query_all_clients(self, query_list):
        all_responces = {}
        messages = query_list['message']

        for client in query_list["clients"] :
            responce = self.clients[self.clients_map[client["client_id"]]].chat.completions.create(
                model = client["model_name"],
                messages = messages
            )

            all_responces[self.clients_map[client["client_id"]]] = responce.choices[0].message.content

        return all_responces

    def eval_responces(self, messages, agents_responces , eval_client_info):
        inp = f"""Hey you are a Judge. There is a query asked to some auto generate models\n
                you have to judge them and give rank as per there answer accuracy\n\n
                
                send data in JSON format. ONLY IN JSON FORMAT\n
                return format {{rank : client ID}}\n

                example : 
                {{1: 2, 2: 3, 3: 1, 4:0}}

                return only JSON nothing else\n

                same query is send to all models\n
                query = {str(messages)}\n\n

                =======================================
                """
        
        for client_id, responce in agents_responces.items() :
            inp += f"""
                    
                    CLIENT_ID : {client_id} 
                    CLIENT_RESPONCE : {responce}
                    =======================================
                    """

        # print(inp)
        eval_client = OpenAI(api_key= eval_client_info["api_key"], base_url= eval_client_info["base_url"])
        responce = eval_client.chat.completions.create(
            model = eval_client_info["model_name"],
            messages = [{"role" : "user", "content" :inp}]
        )

        result = {} 
        
        try : 
            for rank, client_ind in json.loads(responce.choices[0].message.content).items() :
                result[rank] = [int(client_ind), self.clients_map_rev[int(client_ind)]]
        except Exception as e : 
            print(f"{e} :: ", responce.choices[0].message.content)

        return result



init_clients = [{"client_id" : "groq_1", "api_key" : groq_api_key, "base_url" : "https://api.groq.com/openai/v1"},
                {"client_id" : "groq_2", "api_key" : groq_api_key, "base_url" : "https://api.groq.com/openai/v1"},
                {"client_id" : "ollama_1", "api_key" : "ollama", "base_url" : "http://localhost:11434/v1"},
                {"client_id" : "ollama_2", "api_key" : "ollama", "base_url" : "http://localhost:11434/v1"}]

query = {"message" : [{"role" : "user", "content" : "what is the capital of INDIA? \n reply only capital name !!" }] , 
         "clients" : [{"client_id" : "groq_1", "model_name" : "llama-3.1-8b-instant"},
                      {"client_id" : "groq_2", "model_name" : "llama-3.1-8b-instant"},
                      {"client_id" : "ollama_1", "model_name" : "tinyllama"},
                      {"client_id" : "ollama_2", "model_name" : "tinyllama"}]}

test_agents = Test_Agents(init_clients)
agents_responces = test_agents.query_all_clients(query)

print(agents_responces)

result = test_agents.eval_responces(query["message"], agents_responces, eval_client_info={"api_key" : groq_api_key, "base_url": "https://api.groq.com/openai/v1", "model_name" : "llama-3.1-8b-instant"})

print("result : ", result)