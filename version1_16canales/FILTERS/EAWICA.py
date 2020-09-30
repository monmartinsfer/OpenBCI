# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

# entropy
from ENTROPY import entropy
# filters
from FILTERS.filter_bank_manager import filter_bank_class
# infomax based ICA method
from ica import ica1
# external common libraries
from scipy.stats import kurtosis
from sklearn import preprocessing
from scipy.stats import zscore
import numpy as np

# Filtro EAWICA
def eawica(sample, constants, wavelet='db4', low_k=5, up_k=95, low_r=5, up_r=95, alpha=6):  #Recibe la muestra y las constantes
                                                                                            #DESDE Data_Manager. También se fijan
                                                                                            #los valores de los umbrales
    n_channels = sample.shape[0]            #Primer elemento del vector SHAPE = Filas = Canales = Sensores
    n_epochs = constants.SECONDS
    n_samples = constants.WINDOW
    fb = filter_bank_class(constants)       #Envía las constantes a Filter_Bank
    
    # Descomposición de la onda en rangos de frecuencias usando filtro EAWICA en tres listas diferentes
    wcs, wcs_beta, wcs_gamma = [], [], []
    # Para cada canal se descompone la señal en los rangos de frecuencia y se agregan GAMMA, BETA y ALPHA
    for i in range(n_channels):
        GAMMA, BETA, ALPHA, THETA, DELTA = fb.eawica_wavelet_band_pass(sample[i, :], wavelet)   #Aplica el filtro EAWICA paso banda definido en Filter_Bank
        # La lista WCS tendrá la forma [[GAMMA1,0], [BETA1,1], [ALPHA1,2], [GAMMA2,3], [BETA2,4], [ALPHA2,5], ...]
        #                              [[GAMMA1,0], [BETA1,1], [ALPHA1,2], [GAMMA2,3], [BETA2,4], [ALPHA2,5], ...]
        #                              [[GAMMA1,0], [BETA1,1], [ALPHA1,2], [GAMMA2,3], [BETA2,4], [ALPHA2,5], ...]
        pos = i*3
        wcs.append([GAMMA, pos])
        wcs.append([BETA, pos+1])
        wcs.append([ALPHA, pos+2])
        # Las listas WCS_Beta y WCS_Gamma tendrán la forma [BETA1, BETA2...] y [GAMMA1, GAMMA2...]
        wcs_beta.append(BETA)
        wcs_gamma.append(GAMMA)
  
    # CHECKING FIRST CONDITION OVER ALL wcs_delta
    kurt_list = []
    renyi_list = []

    for i in range(len(wcs)):
        # Calcular la kurtosis: E(desviación/variaza)^4
        k = kurtosis(wcs[i][0])     #Aplica la kurtosis al primer elemento de cada pareja de la lista WCS
        kurt_list.append(k)
        # Calcular la entropía Renyi
        pdf = np.histogram(wcs[i][0], bins=10)[0]/wcs[i][0].shape[0]        #Calcula el histograma (diagrama de 10 barras),
                                                                            #coge el primer elemento (número de repeticiones)
                                                                            #y la divide entre el número de filas de esa componente de WCS
        r = entropy.renyientropy(pdf,alpha=alpha,logbase=2,measure='R')
        renyi_list.append(r)
     
    # Escalado: transformar los valores en una distribución normal
    kurt_list_scaled = zscore(kurt_list)
    renyi_list_scaled = zscore(renyi_list)
      
    # Umbrales superior e inferior: calcula los percentiles = valor por debajo del cual se encuentra el porcentaje de los datos especificado
    low_kurt_threshold, up_kurt_threshold = np.percentile(kurt_list_scaled, low_k), np.percentile(kurt_list_scaled, up_k)
    low_renyi_threshold, up_renyi_threshold = np.percentile(renyi_list_scaled, low_r), np.percentile(kurt_list_scaled, up_r)

    # Aplica un OR entre las matrices elemento a elemento para hallar los datos extremos = fuera de los percentiles
    cond_11 = np.logical_or(kurt_list_scaled > up_kurt_threshold, kurt_list_scaled < low_kurt_threshold)
    cond_12 = np.logical_or(renyi_list_scaled > up_renyi_threshold, renyi_list_scaled < low_renyi_threshold)   
    cond_1 = cond_11 + cond_12      #Vector con el valor TRUE/FALSE para cada elemento y para las dos condiciones
    
    # SELECT wcs_delta MARKED AS CONTAINING ARTIFACTUAL INFORMATION
    signals2check = np.zeros((np.sum(cond_1), n_samples+1))     #Crear una matriz de ceros: FILAS = número de TRUE en las condiciones, COLUMNAS = número de muestras
    
    indices = np.where(cond_1 == True)[0]           #Extraer los índices de los elementos cuya condición sea TRUE
    for indx in range(len(indices)):
        if cond_1[indices[indx]]:
            signals2check[indx, :-1] = wcs[indices[indx]][0]
            signals2check[indx, -1] = wcs[indices[indx]][1]
            
    # ICA INFOMAX DECOMPOSITION OF MARKED signals TO OBTAIN ICs
    n_components = signals2check.shape[0]
    A,S,W = ica1(signals2check[:,:-1], n_components)

    # CHECK SECOND CONDITION OVER EACH EPOCH ON WICs
    control_k = np.zeros((S.shape[0], (n_epochs)))
    control_r = np.zeros((S.shape[0], (n_epochs)))
    
    for indx1 in range(S.shape[0]):        
        for indx2 in range((n_epochs)):
            ini = int((indx2*S.shape[1]/n_epochs))
            end = int(ini + S.shape[1]/n_epochs)
            if end+1==S.shape[1]:
                end+=1
            epoch = S[indx1,ini:end] 
            control_k[indx1,indx2] = kurtosis(epoch)
            pdf = np.histogram(epoch, bins=10)[0]/epoch.shape[0]
            r = entropy.renyientropy(pdf,alpha=alpha,logbase=2,measure='R')
            control_r[indx1,indx2] = r        
    
    table = np.zeros((S.shape[0], n_epochs))
    for indx1 in range(n_epochs):
        control_k[:,indx1] = preprocessing.scale(control_k[:,indx1])
        control_r[:,indx1] = preprocessing.scale(control_r[:,indx1])     
        
    table = np.logical_or(control_k > up_kurt_threshold, control_k < low_kurt_threshold) + np.logical_or(control_r > up_renyi_threshold, control_r < low_renyi_threshold)
    
    # ZEROING THOSE EPOCHS IN WICs MARKED AS ARTIFACTUAL EPOCHS
    for indx1 in range(S.shape[0]):        
        for indx2 in range(n_epochs):
            if table[indx1,indx2]:
                ini = indx2*int(n_samples/n_epochs)
                end = ini + int(n_samples/n_epochs)
                # epochs zeroing
                S[indx1,ini:end] = 0             
    
    # wcs_delta RECONSTRUCTION FROM WICs
    reconstructed = A.dot(S) 
    for i in range(reconstructed.shape[0]):   
        wcs[int(signals2check[i,-1])][0] = reconstructed[i,:]

    
    data_cleaned = np.zeros(sample.shape)   
    for i in range(n_channels):
        pos = i*3
        data_cleaned[i,:] = wcs[pos][0]+wcs[pos+1][0]+wcs[pos+2][0]+wcs_beta[i]+wcs_gamma[i]  
            
            
    return data_cleaned

