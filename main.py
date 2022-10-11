from starlette.responses import FileResponse 
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# @app.get('/sample_data')
# async def sample_data():
	

app.mount('/', StaticFiles(directory="frontend/dist", html=True), name='frontend')

