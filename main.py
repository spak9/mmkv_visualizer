from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount('', StaticFiles(directory="src/", html=True), name="static")
