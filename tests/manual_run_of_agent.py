from app.dependencies import get_deepinfra_client, get_langgraph_google_gen_ai_model, get_pinecone_index
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.tracers import ConsoleCallbackHandler

def get_embedding(text) -> list[float]:
    deepinfra_client = get_deepinfra_client()
    embeddings = deepinfra_client.embeddings.create(
        model="sentence-transformers/all-MiniLM-L6-v2",
        input=text,
        encoding_format="float"
    )
    return embeddings.data[0].embedding


def search_vector_database(vector_query):
    pinecone_index = get_pinecone_index()

    if (vector_query['requires_search']):

        # turn get embedding into a tool
        @tool
        def get_embedding_for_query(query: str) -> list[float]:
            """Turn a natural language query into an embedding to search a vector database."""
            query_embedding = get_embedding(query)
            return query_embedding
        
        # tunr querying into a tool
        @tool
        def query_pinecone_vector_database(query_embedding: list[float]) -> str:
            """Use a query embedding to search the vector database for medical articles."""
            query_results = pinecone_index.query(
                namespace="__default__",
                vector=query_embedding,
                top_k=5,
                include_metadata=True,
                include_values=False,
            )
            print(query_results)

            database_search_results = ""

            for match in query_results['matches']: # type: ignore (this is fine because this requires a special type. it's fine.)
                match_text = "Title: " + match['metadata']['title'] + "\n"
                match_text += "Snippet: " + match['metadata']['text'] + "\n"
                match_text += "URL: " + match['metadata']['source_url'] + "\n"
                database_search_results += match_text + "\n"

            return database_search_results  
    
        model = get_langgraph_google_gen_ai_model(model="gemini-2.5-flash")
        agent = create_agent(
            model, 
            tools=[get_embedding_for_query, query_pinecone_vector_database],
            system_prompt="You are an agent that gets database queries and returns if they're relevant. You get a vector_query. First embed the query. Then search the database. If the info is relevant to answering the query, then return the output database_search_results. Otherwise, create another query to possibly look into the database again to find better fitting information for the original query. When you're done, only return the output from the query_pinecone_vector_database tool.")

        result = agent.invoke(
            {"messages": [{"role": "user", "content": f"Search for medical articles relevant to: {vector_query['query']}"}]},
            config={"callbacks": [ConsoleCallbackHandler()]})
        
        output = result["messages"][-1].content[0]['text']
        return output

yo = search_vector_database({
    "query": "back pains",
    "requires_search": True
})
print(yo)
print(type(yo))