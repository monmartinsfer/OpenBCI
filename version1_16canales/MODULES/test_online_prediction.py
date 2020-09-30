# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""
#%%
from COM.trigger_server_2 import trigger_server
from DYNAMIC import dynamic as Dyn_import
from GENERAL.data_manager_openBCI_02 import data_manager_openBCI 
from LOGGING import logger as log
from GENERAL.ring_buffer_02 import RingBuffer as buffer
from GENERAL.constants_02 import constants
from COM.open_bci_GCPDS_02 import OpenBCIBoard as openBCI
from GUI.GUI_bci_03 import GUI 
from GENERAL import csv_fileIO as io
from GENERAL.slots_manager import SlotsManager
from FEATURES.online_features_02 import compute_online_features
from FEATURES.feature_selection import kbest_selection
from CLASSIFIERS import models_trainer 
from GENERAL import csv_fileIO as io
import numpy as np
import pickle
############# EXTERNAL LIBRARIES ######################################
from PyQt5 import QtWidgets
from multiprocessing import Queue, Value

isconnected = Value('b',1) 
streaming = Value('b',0)   
############### INIT CONSTANTS DEFINITION ###########################
constants = constants()
######### slots manager for multiple callbacks settings #############
slots = SlotsManager()
########### queue ###########
queue = Queue()
################ BUFFER  ####################     
buffer = buffer(constants)
buffer.emitter.connect(slots.trigger)
################ INIT DATA MANAGER #####################
eeg_dmg = data_manager_openBCI(constants, queue, buffer, slots)  
eeg_dmg.start()

from FEATURES.online_features_02 import compute_online_features

from multiprocessing import Process, Array
from sklearn.externals import joblib
import numpy as np
import pickle

# callbacks
isstored = True
trial = 0
# -- features settings --
numBasicFeatures = 5
numBands = 5
numFeatures = numBasicFeatures*numBands*constants.CHANNELS
# -- path settings --
user = 'MIKEL'
path_model = './RESULTS/' + user + '/best_model.npy'
path_best_model_furnitures = './RESULTS/' + user + '/best_model_furnitures.npy'
path_training_data = './RESULTS/' + user + '/allFeatures.npy'
path_predictions = './RESULTS/' + user + '/predictions'
# -- load machine-learning model --
model = pickle.load(open(path_model, 'rb'))
# -- load furnitures --
training_data = np.load(path_training_data)
best_model_furnitures = np.load(path_best_model_furnitures)
selected_features_indx = best_model_furnitures.item().get('selected_features')

print('paso')
# -- get sample --
sample = eeg_dmg.get_short_sample(constants.METHOD)   
# -- compute features --
feature = compute_online_features(sample,constants, numFeatures)
# -- feature smoothing -- 
training_data = np.vstack((training_data,feature))
from FEATURES.feature_smoothing import smoothing
training_data = smoothing(training_data)
# -- feature scaling --
from sklearn.preprocessing import QuantileTransformer, MinMaxScaler
Quantile_scaler = QuantileTransformer(output_distribution='normal')
training_data = Quantile_scaler.fit_transform(training_data)
MinMax_scaler = MinMaxScaler()
training_data = MinMax_scaler.fit_transform(training_data)
feature = training_data[-1,:]
# -- estimate emotion --
probabilities = model.predict_proba(feature[selected_features_indx].reshape(1,-1))
predictions[:] = probabilities.squeeze().tolist()
    
def append_to_store(self):
    allPredictions.append(predictions[:])

def save_predictions(self):
    print('save predictions: ', isstored)
    if not isstored:
        np.save(path_predictions + '_trial_' + str(trial), allPredictions)
        trial += 1
    isstored = not isstored
    
        
