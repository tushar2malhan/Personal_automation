'''
    Description : Loading Artifcats - Model and Location names
'''

import json
import pickle
from loguru import logger
import numpy as np



def artifacts():
    """ Loading Model name 
        and all the locations
    """

    try:
        with open(".\models\columns.json") as f:
            __data_columns = json.load(f)['data_columns']
            __locations = __data_columns[3:]
    except:
        print("Issue in json file for returning \
                the columns name")
    try:
        with open(r'.\models\banglore_home_prices_model.pickle', 'rb') as f:
            __model = pickle.load(f)
    except Exception as e :
        logger.info(e,"\nIssue in  returning the Model file")

    return {'location': __locations, "model": __model, 'data_column':__data_columns}


def get_locations():
    """ 
        Returning Locations
    """
    return artifacts().get('location')

def load_ML_model():
    """ 
        Returning Model name 
    """
    return artifacts().get('model')


def get_estimated_price(location,sqft,bhk,bath):
    try:
        loc_index =  artifacts().get('data_column').index(location.lower())
    except:
        loc_index = -1

    x = np.zeros(len(artifacts().get('data_column')))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index>=0:
        x[loc_index] = 1
    print(round(artifacts().get('model').predict([x])[0],2))
    return round(artifacts().get('model').predict([x])[0],2)
