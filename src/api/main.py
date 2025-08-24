from fastapi import FastAPI
from app.core import test_url

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/url/test")
def test_url_endpoint(url: str, render: bool = False):
    return test_url(url, render)