from app.config import get_settings

def test_settings_with_all_env_vars(monkeypatch):
    monkeypatch.setenv("RUNPOD_PROJECT_ID", "test_project_123")
    monkeypatch.setenv("RUNPOD_API_KEY", "test_runpod_key")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test_deepinfra_key")
    monkeypatch.setenv("PINECONE_API_KEY", "test_pinecone_key")
    monkeypatch.setenv("PINECONE_INDEX_NAME", "test_articles")

    get_settings.cache_clear()

    settings = get_settings()

    assert settings.runpod_project_id == "test_project_123"
    assert settings.runpod_api_key == "test_runpod_key"
    assert settings.gemini_api_key == "test_gemini_key"
    assert settings.deepinfra_api_key == "test_deepinfra_key"
    assert settings.pinecone_api_key == "test_pinecone_key"
    assert settings.pinecone_index_name == "test_articles"

def test_pinecone_index_default_value(monkeypatch):
    monkeypatch.setenv("RUNPOD_PROJECT_ID", "test_project_123")
    monkeypatch.setenv("RUNPOD_API_KEY", "test_runpod_key")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test_deepinfra_key")
    monkeypatch.setenv("PINECONE_API_KEY", "test_pinecone_key")

    get_settings.cache_clear()

    settings = get_settings()

    assert settings.runpod_project_id == "test_project_123"
    assert settings.runpod_api_key == "test_runpod_key"
    assert settings.gemini_api_key == "test_gemini_key"
    assert settings.deepinfra_api_key == "test_deepinfra_key"
    assert settings.pinecone_api_key == "test_pinecone_key"
    assert settings.pinecone_index_name == "house-md-medicine-wiki-articles"

def test_get_settings_returns_cached_instance(monkeypatch):
    monkeypatch.setenv("RUNPOD_PROJECT_ID", "test_project")
    monkeypatch.setenv("RUNPOD_API_KEY", "test_key")
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test_key")
    monkeypatch.setenv("PINECONE_API_KEY", "test_key")
    
    get_settings.cache_clear()
    
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2
