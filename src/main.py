from starlette.responses import FileResponse 
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount('/', StaticFiles(directory="frontend/dist", html=True), name='frontend')



# @app.get("/")
# async def root():
#     return FileResponse('frontend/pre_index.html')


# @app.get('/mmkv_parser.py')
# async def mmkv_parser():
#     return FileResponse('mmkv_parser.py')


# @app.get('/style.css')
# async def style():
#     return FileResponse('frontend/src/style.css')