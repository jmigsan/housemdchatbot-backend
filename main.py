import re
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
import json
from openai import OpenAI
from datetime import datetime, timezone

load_dotenv()

client = genai.Client()

housemd_client = OpenAI(
    base_url=f"https://api.runpod.ai/v2/{os.getenv('RUNPOD_PROJECT_ID')}/openai/v1",
    api_key=os.getenv("RUNPOD_API_KEY")
)

model = SentenceTransformer("all-MiniLM-L6-v2")

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("house-md-medicine-wiki-articles")

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str
    timestamp: str

def now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

@app.websocket('/api/ws/chat/runpod')
async def chat_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    messages: list[Message] = []

    initialMessage: Message = Message(
        role="model",
        content="If you're here to ask for directions, you're at the wrong place. If you're here to ask me for a doctor, you're also at the wrong place.",
        timestamp=now_iso()
    )
    messages.append(initialMessage)

    try:
        while True:
            data = await websocket.receive_json()

            time_now_iso = now_iso()

            # Get previous  messages, and recent message, formatted into Gemini to query
            conversation_to_query = [types.Content(role=msg.role, parts=[types.Part(text=msg.content)]) for msg in messages]
            conversation_to_query.append(types.Content(role=data['role'], parts=[types.Part(text=data['content'])]))

            search_llm_prompt = """You are an expert at identifying search queries from a conversation with a Dr Gregory House chatbot. Your task is to analyze the conversation and determine if a database search is necessary for any medical knowledge queries.

Respond with a single, complete JSON object. The JSON must contain two keys:
1.  `requires_search` (boolean): `true` if a database search is needed to answer the user's query, `false` otherwise.
2.  `query` (string): A concise, specific query for a semantic search of the database. This should be a single sentence that captures the user's intent. If `requires_search` is `false`, this field should be empty.

Example 1:
User: "I've had a dry cough for three weeks, but no fever or sore throat. Should I be worried?"
Response:
{
  "requires_search": true,
  "query": "persistent dry cough lasting 3 weeks, no fever, no sore throat, causes and evaluation"
}

Example 2:
User: "Hi, how are you?"
Response:
{
  "requires_search": false,
  "query": ""
}

Example 3:
User: "My hands feel numb and tingly, especially at night. Could this be carpal tunnel?"
Response:
{
  "requires_search": true,
  "query": "numbness and tingling in hands at night, possible carpal tunnel syndrome, diagnosis and management"
}"""

            # read convrsation to create a good search term
            vector_query = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=conversation_to_query,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["query"],
                        properties = {
                            "requires_search": genai.types.Schema(
                                type = genai.types.Type.BOOLEAN,
                            ),
                            "query": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                        },
                    ),
                    system_instruction=search_llm_prompt,
                ),
            )

            print(vector_query.text)

            vector_query_json = json.loads(vector_query.text)

            database_search_results = ""

            if (vector_query_json['requires_search']):
                query_embedding = model.encode(vector_query_json['query']).tolist()

                query_results = dense_index.query(
                    namespace="__default__",
                    vector=query_embedding,
                    top_k=5,
                    include_metadata=True,
                    include_values=False,
                )

                print(query_results)

                for match in query_results['matches']:
                    match_text = "Title: " + match['metadata']['title'] + "\n"
                    match_text += "Snippet: " + match['metadata']['text'] + "\n"
                    match_text += "URL: " + match['metadata']['source_url'] + "\n"
                    database_search_results += match_text + "\n"

            rag_input =f"""<database_search_results>
{database_search_results if database_search_results else "No relevant documents found."}</database_search_results>

<user_question>
{data['content']}
</user_question>"""
            
            conditional_instruction = """You are Dr. Gregory House, the brilliant but unconventional diagnostician from the TV show House M.D. Respond in character, using House's sharp wit, sarcasm, and blunt demeanor. Prioritize clever, insightful, and often provocative answers that reflect his diagnostic genius and disdain for conventional niceties. Always aim to uncover the truth behind medical or personal queries, even if it means challenging the user or making bold assumptions. If a database search is provided, use it to inform your answers, but filter the information through House's skeptical and analytical lens, questioning its reliability if appropriate. Avoid breaking character or providing out-of-character explanations unless explicitly requested. If faced with incomplete information, make educated guesses or demand clarification in House's abrasive style."""
            
            # Get all messages, and most recent message, and system prompt, to query Dr House endpoint
            contents = [{"role": "system", "content": conditional_instruction}]
            contents.extend([{"role": msg.role, "content": msg.content} for msg in messages])
            contents.append({"role": "user", "content": rag_input})

            print(contents)

            response = housemd_client.chat.completions.create(
                model="migsoneural/qwen3-4b-housemd-not2507",
                messages=contents,
                temperature=0.7,
                max_tokens=1024
            )

            response_text = response.choices[0].message.content

            print('Response:',response_text)

            def clean_response(text):
                # Remove <think> tags and any trailing newline or whitespace
                cleaned_text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
                return cleaned_text.strip()  # Remove any leading/trailing whitespace
            
            cleaned_response_text = clean_response(response_text)

            messages.append(Message(role=data['role'], content=data['content'], timestamp=data['timestamp']))

            messages.append(Message(role="model", content=cleaned_response_text, timestamp=time_now_iso))

            print(messages)

            await websocket.send_json(
                {
                    "role": "model",
                    "content": cleaned_response_text,
                    "timestamp": time_now_iso
                }
            )

    except Exception as e:
        print(e)
    finally:
        await websocket.close()
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)