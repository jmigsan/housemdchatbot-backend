import pytest

from app.dependencies import get_deepinfra_client, get_gemini_client, get_housemd_client, get_pinecone_index

@pytest.mark.parametrize('get_client_func', [get_deepinfra_client, get_gemini_client, get_housemd_client, get_pinecone_index])
def test_client_cache(get_client_func):
    client1 = get_client_func
    client2 = get_client_func
    assert client1 is client2


@pytest.mark.parametrize('get1,get2', [
    (get_deepinfra_client, get_gemini_client),
    (get_deepinfra_client, get_housemd_client),
    (get_deepinfra_client, get_pinecone_index),
    (get_gemini_client, get_housemd_client),
    (get_gemini_client, get_pinecone_index),
    (get_housemd_client, get_pinecone_index)
])
def test_client_independence(get1, get2):
    assert get1 is not get2


@pytest.mark.integration
class TestLiveAPI:
    def test_gemini_connection(self):
        client = get_gemini_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents="Say 'OK'"
        )
        assert response is not None
        assert response.text is not None

    def test_housemd_connection(self):
        client = get_housemd_client()
        models = client.models.list()
        assert len(models.data) > 0
    
    def test_deepinfra_connection(self):
        client = get_deepinfra_client()
        model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5
        )
        assert response.choices[0].message.content

    def test_pinecone_connection(self):
        index = get_pinecone_index()
        stats = index.describe_index_stats()
        assert stats is not None