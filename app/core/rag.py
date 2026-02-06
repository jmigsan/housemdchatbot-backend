from app.dependencies import get_deepinfra_client, get_pinecone_index


def get_embedding(text, deepinfra_client) -> list[float]:
    embeddings = deepinfra_client.embeddings.create(
        model="sentence-transformers/all-MiniLM-L6-v2",
        input=text,
        encoding_format="float"
    )
    return embeddings.data[0].embedding


def search_vector_database(vector_query):
    deepinfra_client = get_deepinfra_client()
    pinecone_index = get_pinecone_index()

    database_search_results = ""

    if (vector_query['requires_search']):
        
        query_embedding = get_embedding(vector_query['query'], deepinfra_client)

        query_results = pinecone_index.query(
            namespace="__default__",
            vector=query_embedding,
            top_k=5,
            include_metadata=True,
            include_values=False,
        )

        print(query_results)

        for match in query_results['matches']: # type: ignore (this is fine because this requires a special type. it's fine.)
            match_text = "Title: " + match['metadata']['title'] + "\n"
            match_text += "Snippet: " + match['metadata']['text'] + "\n"
            match_text += "URL: " + match['metadata']['source_url'] + "\n"
            database_search_results += match_text + "\n"

    return database_search_results