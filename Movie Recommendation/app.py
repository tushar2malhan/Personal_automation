"""
     Description : Movie Recommendation System
     Date        : 16/11/2022
"""

# import streamlit as st
import pickle
import requests
import re
import joblib
import pandas as pd
from loguru import logger
from bs4 import BeautifulSoup
from urllib.request import urlopen



# st.header('Movie Recommender System')

model_= joblib.load("similar_movies.pkl")
movies = pd.DataFrame(model_)  

similarity = joblib.load("similarity_column.pkl")

# print(movies.title)           # List of all movies title
# print(similarity)               # Measurement and similarity for each movie
# print(    sorted(   list(enumerate(similarity[0])) , key= lambda x:x[1]   )[-1:-6:-1]  )


def get_posters(movie):
          url = f'https://www.imdb.com/find?q={movie}&ref_=nv_sr_sm'


          response = requests.get(url)

          soup = BeautifulSoup(response.content, 'html.parser')

          return soup.findAll('img')[1]['src']
          # import pdb;pdb.set_trace()

     

def recommend(movie):
     ''' function to give prediction of the movie '''

     movie_index = movies[movies.title == movie].index[0]
     # getting the max predictions for this movie_index 

     similar_movies = sorted(   list(enumerate(similarity[0])) , key= lambda x:x[1]   )[-2:-7:-1]


     for each_movie in similar_movies:
          print({

               "title": movies.iloc[each_movie[0]].title ,
               "poster":get_posters(movies.iloc[each_movie[0]].title)
          })
     
     return movie

RESULT =  recommend('Avatar')
print(end='')
logger.info(f"\n\nRecommended Movies Based on your interest {RESULT} \n")
