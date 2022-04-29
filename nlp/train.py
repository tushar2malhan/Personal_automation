import numpy as np
import random
import json

    # open python interpreter from command line
    # >>> import nltk
    # >>> nltk.download()
    # choose and install all or some corpora
    # TERMNIAL > import nltk ; nltk.download('punkt')
import torch
import torch.nn as nn

from torch.utils.data import Dataset, DataLoader
from nltk_utils import bag_of_words, tokenize, stem
# from model import NeuralNet

with open('intents.json') as json_data:
    intents = json.load(json_data)

all_words = []
tags = []
xy = []
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    # print(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
    # print('********************',end='\n\n')
        xy.append((w,tag))

# STEM AND LOWER CASE
ignore_words = ['?','.','!',',']
all_words = sorted(set([stem(w) for w in all_words if w not in ignore_words]))
tags = sorted(set(tags))


# print(len(xy), "patterns")
# print(len(tags), "tags:", tags)
# print(len(all_words), "unique stemmed words:", all_words)

# create training data
X_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    # X: bag of words for each pattern_sentence
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    # y: PyTorch CrossEntropyLoss needs only class labels, not one-hot
    label = tags.index(tag)
    y_train.append(label)


X_train = np.array(X_train)
y_train = np.array(y_train)
print(X_train)
print(y_train)