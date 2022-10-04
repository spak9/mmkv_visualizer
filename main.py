from starlette.responses import FileResponse 
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles


app = FastAPI()


@app.get("/")
async def read_index():
    return FileResponse('src/frontend/pre_index.html')


