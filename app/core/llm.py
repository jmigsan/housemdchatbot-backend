from google import genai
from google.genai import types
import json
import re
from app.dependencies import get_gemini_client, get_housemd_client


def generate_vector_query(data, messages):
    conversation_to_query = [types.Content(role=msg.role, parts=[types.Part(text=msg.content)]) for msg in messages]
    conversation_to_query.append(types.Content(role=data.role, parts=[types.Part(text=data.content)]))

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

    gemini_client = get_gemini_client()

    # read convrsation to create a good search term
    vector_query = gemini_client.models.generate_content(
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

    vector_query_json = json.loads(vector_query.text) # type: ignore (this is fine because this requires a special type. it's fine.)
    return vector_query_json 


def generate_housemd_response(database_search_results, data, messages):
    rag_input =f"""<database_search_results>
{database_search_results if database_search_results else "No relevant documents found."}</database_search_results>

<user_question>
{data.content}
</user_question>"""
            
    conditional_instruction = """You are Dr. Gregory House, the brilliant but unconventional diagnostician from the TV show House M.D. Respond in character, using House's sharp wit, sarcasm, and blunt demeanor. Prioritize clever, insightful, and often provocative answers that reflect his diagnostic genius and disdain for conventional niceties. Always aim to uncover the truth behind medical or personal queries, even if it means challenging the user or making bold assumptions. If a database search is provided, use it to inform your answers, but filter the information through House's skeptical and analytical lens, questioning its reliability if appropriate. Avoid breaking character or providing out-of-character explanations unless explicitly requested. If faced with incomplete information, make educated guesses or demand clarification in House's abrasive style."""
    
    # Get all messages, and most recent message, and system prompt, to query Dr House endpoint
    contents = [{"role": "system", "content": conditional_instruction}]
    contents.extend([{"role": msg.role, "content": msg.content} for msg in messages])
    contents.append({"role": "user", "content": rag_input})

    print(contents)

    housemd_client = get_housemd_client()

    response = housemd_client.chat.completions.create(
        model="migsoneural/qwen3-4b-housemd-not2507",
        messages=contents, # type: ignore (this is fine because this requires a special type. it's fine.)
        temperature=0.7,
        max_tokens=1024
    )

    response_text = response.choices[0].message.content
    print('Response:',response_text)

    def clean_housemd_response(text):
        # Remove <think> tags and any trailing newline or whitespace
        cleaned_text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
        return cleaned_text.strip()  # Remove any leading/trailing whitespace
    
    cleaned_response_text = clean_housemd_response(response_text)
    return cleaned_response_text