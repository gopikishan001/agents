from dotenv import load_dotenv
from openai import OpenAI
import json
import os 
from pypdf import PdfReader 
import gradio as gr 

load_dotenv(override= True)
groq_api_key = os.getenv("GROQ_API_KEY")

openai = OpenAI(
    api_key= groq_api_key,
    base_url= "https://api.groq.com/openai/v1"
)

# tool 1 
def record_user_details(email, name = "Name not provided", notes = "Not provided") :
    return {"record_states" : "ok"}

def record_unknown_question(question) :
    return {"record_states" : "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]


def handel_tool_calls(tool_calls) :

    results = []
    for tool_call in tool_calls:

        print("==========================")
        print(tool_call)
        
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results

reader = PdfReader("/home/gopi/Downloads/Gopikishan_Mahto_Resume.pdf")
data = ""

for page in reader.pages: 
    text = page.extract_text()
    if text : 
        data += text 

name = "Gopikishan Mahto"

system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a Resume of {name}'s background which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

system_prompt += f"\n\n## Resume:\n{data}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."


def chat(message, history) :

    for i in range(len(history)) : # not supported by groq
        try : 
            del history[i]['metadata'] 
            del history[i]['options']
        except : 
            pass 

    messages = [{"role" : "system", "content" : system_prompt}] +  history + [{"role": "user", "content" : message}]

    done = False 

    while not done :

        response = openai.chat.completions.create(
            model= "llama-3.1-8b-instant",
            messages= messages,
            tools= tools
        )

        finish_reason = response.choices[0].finish_reason

        if finish_reason == "tool_calls" :
            message  = response.choices[0].message 
            tool_calls = message.tool_calls

            tool_results = handel_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(tool_results)

        else :
            done = True 
    
    return response.choices[0].message.content


gr.ChatInterface(chat, type="messages").launch()
