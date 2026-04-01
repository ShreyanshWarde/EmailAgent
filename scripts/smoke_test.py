from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

print("GET /health ->", client.get('/health').json())
print("GET / ->", client.get('/').json())
