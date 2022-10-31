""" 
    Author : Tushar Malhan
    Description : Machine Learning Application
    Date : 10/24/2022

"""

import os
import json
import sys
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from loguru import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util import get_locations, get_estimated_price

app = FastAPI(debug = True)
templates = Jinja2Templates(directory="frontend/")
app.mount(
    "/frontend",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "frontend"),
    name="frontend")


@app.get('/')
def hello(request: Request):
    print('\n')
    logger.info('FastAPI Home Price Machine Learning Application\n')
    result = 'result'
    return templates.TemplateResponse('app.html', context = {'request': request, 'result': result})

@app.get('/get_location_names')
def get_location_names(request: Request):
    logger.info("All locations presented")
    response = get_locations()
    return response

@app.post('/predict_home_price')
async def predict_home_price(request: Request):
    body = await request.body()
    text: str = bytes.decode(body).split('&')
    total_sqft = int(text[0].split('=')[1])
    bhk = int(text[1].split('=')[1])
    bath = int(text[2].split('=')[1])
    location = text[3].split('=')[1].replace('+',' ')

    return get_estimated_price(location,total_sqft,bhk,bath)