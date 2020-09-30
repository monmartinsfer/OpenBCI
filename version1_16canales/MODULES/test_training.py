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
from FEATURES.feature_selection import rfe_selection
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



numBasicFeatures = 5
numBands = 5
numFeatures = numBasicFeatures*numBands*constants.CHANNELS
numTrials = 15
numTestTrials = 12
print('training pipeline is initialized')

user = 'mikel'
path_training = './data/MIKEL/' + user +'.csv'
path_labels = './data/MIKEL/labels_' + user + '.csv'
path_best_model = './RESULTS/MIKEL/best_model.npy'
path_best_model_furnitures = './RESULTS/MIKEL/best_model_furnitures.npy'
path_allFeatures = './RESULTS/MIKEL/allFeatures.npy'
path_allLabels = './RESULTS/MIKEL/allLabels.npy'


############  LOAD TRAINING DATA #############################
dataframe = io.open_csvFile(path_training)
labels_byTrial = io.open_csvFile(path_labels)
dataframe = dataframe.iloc[8:,:]
############## COMPUTE FEATURES ###################################
numSamples = int(dataframe.shape[0]/constants.CHANNELS)
# -- init training data
features = np.zeros((numSamples, numFeatures))
labels = np.zeros((numSamples,))
for i in range(numSamples):
    # -- indexing training data
    ini = i*constants.CHANNELS
    end = ini+constants.CHANNELS
    sample = dataframe.iloc[ini:end,3:]
    # -- get features by sample
    features[i,:] = compute_online_features(sample,constants,numFeatures)
    # -- get label depending on the trial --
    labels[i] = labels_byTrial['label'].iloc[ dataframe['trial'].iloc[i*constants.CHANNELS] ]     
    
        
np.save(path_allFeatures, features)
np.save(path_allLabels, labels)      

features = np.load(path_allFeatures)

####### DATASET PREPROCESSING #######################
from sklearn.preprocessing import QuantileTransformer
Quantile_scaler = QuantileTransformer(output_distribution='normal')
features = Quantile_scaler.fit_transform(features)



########## DATASET SMOOTHING #######################
from FEATURES.feature_smoothing import smoothing
for i in range(features.shape[1]):
    try:
        features[:,i] = smoothing(features[:,i])
    except:
        print(i)

import matplotlib.pyplot as plt
plt.imshow(features.T)
######## TRAIN AND TEST SETS SPLIT ##############
from FEATURES.features_train_test_split import ByTrials_train_test_split
X_train, y_train, X_test, y_test = ByTrials_train_test_split(features, labels, numTrials, numTestTrials)

########## FEATURE SELECTION AND MODEL TRAINING ##############
label_names = ['POS','NEU','NEG']
best_model = {'model':[],'name':[],'predictions':[],'score':0,'selected_features':[],'report':[]}
for i in range(1,numFeatures):
    # -- feature selection -- #
    select_features = i
    _, selected_features_indx = rfe_selection(X_train, y_train, select_features)  
    # -- model training -- #
    classifiers, names, predictions, scores_list = models_trainer.classify(X_train[:,selected_features_indx], y_train, X_test[:,selected_features_indx], y_test)
    winner = np.asarray(scores_list).argmax()
    if scores_list[winner] > best_model['score']:
        best_model['model'] = classifiers[winner]
        best_model['name'] = names[winner]
        best_model['predictions'] = predictions[winner]
        best_model['score'] = scores_list[winner]
        best_model['selected_features'] = selected_features_indx
        best_model['report'] = models_trainer.get_report(classifiers[winner], X_test[:,selected_features_indx], y_test, label_names)
#        log.update_text('Report: ' + best_model['report'])
        print(best_model['report'] )
        
        # save the model to disk
        pickle.dump(best_model['model'], open(path_best_model, 'wb'))
        # -- save furnitures to disk --
        np.save(path_best_model_furnitures, best_model)
