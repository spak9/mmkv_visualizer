from starlette.responses import FileResponse 
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount('/', StaticFiles(directory="frontend/dist", html=True), name='frontend')
