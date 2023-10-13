# -*- coding: utf-8 -*-
"""
Created on Thu May  3 11:11:13 2018

@author: Frank
"""

from DataHandler import DataHandler
from surprise import SVD
from surprise import KNNBasic
from surprise import NormalPredictor
from surprise import dump
from Evaluator import Evaluator

import random
import numpy as np

def LoadData(every_nth = 0):
    dh = DataHandler()
    print("Loading book ratings...")
    data = dh.loadData(every_nth)
    print("\nComputing book popularity ranks so we can measure novelty later...")
    rankings = dh.getPopularityRanks()
    return (data, rankings, dh)

np.random.seed(0)
random.seed(0)

# Load up common data set for the recommender algorithms
(evaluationData, rankings, dh) = LoadData()

# Construct an Evaluator to, you know, evaluate them
evaluator = Evaluator(evaluationData, rankings)

# Just make random recommendations
Random = NormalPredictor()
evaluator.AddAlgorithm(Random, "Random")

# Throw in an SVD recommender
SVDAlgorithm = SVD(random_state = 10)
evaluator.AddAlgorithm(SVDAlgorithm, "SVD")

# KNN algorithm based on cosine and users
UserKNN = KNNBasic(sim_options = {'name' : 'cosine', 'user_based' : True})
evaluator.AddAlgorithm(UserKNN, "User KNN")

# KNN algorithm based on cosine and items
ItemKNN = KNNBasic(sim_options = {'name' : 'cosine', 'user_based' : False})
evaluator.AddAlgorithm(ItemKNN, "Item KNN")

# Fight!
evaluator.Evaluate()
