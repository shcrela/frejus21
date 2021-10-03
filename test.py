#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 10:34:02 2021

@author: dejan
"""
import os
import numpy as np
from scipy import linalg, spatial
from sklearn import metrics, decomposition
import matplotlib.pyplot as plt
# from read_WDF import read_WDF
from read_WDF_class import WDF
import visualize as vis
import CR_search as cr
import preprocessing as pp
import calculate as cc

# folder = "../../Raman/Data/Chloe/prob/"
# file = "sableindien-x5-532streamline-map1.wdf"

folder = "../../../RamanData/Maxime/"
files = os.listdir(folder)
valid_files = [f for f in files if f[-3:].lower()=="wdf"]
file = valid_files[4]
print(file)
folder = "../../../RamanData/Chloe/prob/"
file = "sableindien-x5-532streamline-map1.wdf"
filename = folder + file

fff = WDF(filename)

# vis.ShowSelected(fff)

fff.spectra = pp.correct_saturated(fff)
#%%
from read_WDF import read_WDF

spectra, sigma, params, map_params, origins = read_WDF(filename, verbose=True)
#%%
# Order:
# rawspectra, x_values = pp.order(rawspectra, x_values)
# fff.spectra = pp.remove_CRs(fff.spectra, fff.x_values)
b_line = cc.baseline_als(fff.spectra)
fff.spectra -= b_line
vis.AllMaps(b_line.reshape(fff.n_y, fff.n_x, -1))

vis.AllMaps((fff.spectra[:,635]/fff.spectra[:,400]).reshape(fff.n_y, fff.n_x, -1))

#%% Correct saturated spectra
fff.spectra = pp.correct_saturated(fff.spectra, (fff.n_y, fff.n_x))

# Normalize
norma = linalg.norm(rawspectra, axis=-1, keepdims=True)
norma[norma==0] = 1

n_spectra = rawspectra/norma
n_pectra = pp.scale(n_spectra)
#%%
# BAseline:
b_line = cc.baseline_als(n_spectra)#, lam=1e7, p=0.5)
spectra = n_spectra - b_line
vis.ShowSpectra(spectra, x_values)
#%%
# Sparse PCA
pca = decomposition.SparsePCA(n_components=4)
n_spectra = pp.scale(rawspectra)
reduced = pca.fit(n_spectra)

#%%
# calculate the distances between all pairs of spectra:
distances = spatial.distance.pdist(spectra, 'hamming')
dd = spatial.distance.squareform(distances)

dd = metrics.pairwise.nan_euclidean_distances(spectra, missing_values=0)
def closest(indice):
    global spectra, distances, dd, zero_saturated_idx

    a = dd[indice]
    valid_idx = np.setdiff1d(np.where(a > 0)[0], zero_saturated_idx)
    closest_idx = valid_idx[a[valid_idx].argmin()]
    plt.figure()
    plt.plot(spectra[indice], alpha=0.5, label=indice)
    plt.plot(spectra[closest_idx], alpha=0.5, label=closest_idx)
    plt.legend()


closest(834)
#%%
crs = cr.AdjustCR_SearchSensitivity(spectra, x_values)
ccc = cr.remove_CRs(mock_sp3, sigma_kept, initialization)
#cr.remove_cosmic_rays(spectra, x_values)
#%%
# We identify where are the sharp peaks:
surplus = np.diff(spectra, n=3, axis=-1, append=spectra[:,-3:])
condition = surplus / (spectra+1)
kandidati = np.where(surplus  > 5000)
# mean_values = np.mean(spectra, axis=-1, keepdims=True)
# kandidati = np.where(surplus / mean_values > 1)


# Now, we need to check if among `kandidati` we observe some repeating values,
# in which case they are more likely to represent cristalisations then CRs
cumuls = np.histogram(kandidati[1], bins=x_values[::10])
kristali = np.where(cumuls[0] > np.std(cumuls[0]))[0]

# Eliminate the repeating values from `kandidati`
left_bin_border = cumuls[1][kristali]
right_bin_border = cumuls[1][kristali+1]
to_keep = np.ones_like(kandidati[0], dtype=bool)
for i, (l, r) in enumerate(zip(left_bin_border, right_bin_border)):
    to_keep[np.where((l < kandidati[1]) & (kandidati[1] < r))[0]] = 0

CRs = (kandidati[0][to_keep], x_values[kandidati[1][to_keep]])
