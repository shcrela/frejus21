#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 18:53:55 2021

@author: dejan
"""
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, transform
from scipy.ndimage import median_filter
from sklearn.experimental import enable_iterative_imputer
from sklearn import preprocessing, impute
import calculate as cc
from read_WDF_class import WDF
# from sklearnex import patch_sklearn
# patch_sklearn()


def select_zone(spectra, **kwargs):
    if isinstance(spectra, WDF):
        left = kwargs.get('left', spectra.x_values.min())
        right = kwargs.get('right', spectra.x_values.max())
        condition = (spectra.x_values >= left) & (spectra.x_values <= right)
        spectra.x_values = spectra.x_values[condition]
        spectra.spectra = spectra.spectra[:, condition]
        spectra.npoints = len(spectra.x_values)
        return spectra

def scale(spectra, **kwargs):
    """
    scale the spectra

    Parameters
    ----------
    spectra : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    return preprocessing.robust_scale(spectra, axis=-1,
                                      with_centering=False,
                                      quantile_range=(5,95))


def order(spectra, x_values):
    """
    Order values so that x_values grow.

    Parameters:
    -----------
    spectra: numpy array
        Your input spectra
    x_values: 1D numpy array
        Raman shifts

    Returns:
    --------
    ordered input values
    """

    if np.all(np.diff(x_values) <= 0):
        x_values = x_values[::-1]
        spectra = spectra[:,::-1]
    return spectra, x_values


def find_zeros(spectra):
    """
    Find the indices of zero spectra.

    Parameters
    ----------
    spectra : 2D numpy array
        your raw spectra.

    Returns
    -------
    1D numpy array of ints
        indices of zero spectra.

    """
    zero_idx = np.where((np.max(spectra, axis=-1) == 0) &
                        (np.sum(spectra, axis=-1) == 0))[0]
    if len(zero_idx) > 0:
        return zero_idx


def find_saturated(spectra, saturation_limit=90000):
    """
    Identify the saturated instances in the spectra.
    IMPORTANT: It will work only before any scaling is done!

    Parameters
    ----------
    spectra : 2D numpy array of floats
        Your input spectra.

    Returns
    -------
    Indices of saturated spectra.
    """

    razlika = np.abs(
                np.diff(spectra, n=1, axis=-1,
                        append=spectra[:,-2][:,None]))

    saturated_indices = np.unique(
                        np.where(razlika > saturation_limit)[0])

    if len(saturated_indices)==0 and np.any(spectra==0):
        print("No saturated spectra is found;\n"
              "Please make sure to apply this function before any scaling is done!")
    else:
        return saturated_indices


def get_neighbourhood(indices, map_shape):
    """
    Recover the indices of the neighbourhood (the `O`s in the schema below)
                                  O
                                 OOO
                                OOXOO
                                 OOO
                                  O
    for each element `X` listed in `indices`,
    given the shape of the containing matrix `map_shape`.
    """
    if isinstance(map_shape, int):
        nx = 1
        size = map_shape
    elif len(map_shape) == 2:
        nx = map_shape[1]
        size = map_shape[0] * map_shape[1]
    else:
        print("Check your `map_shape` value.")
        return
    extended = list(indices)
    for s in extended:
        susjedi = np.unique(
                    np.array([s-2*nx,
                              s-nx-1, s-nx, s-nx+1,
                              s-2, s-1, s, s+1, s+2,
                              s+nx-1, s+nx, s+nx+1,
                              s+2*nx]))
        susjedi_cor = susjedi[(susjedi >= 0) & (susjedi < size)]
        extended = extended + list(susjedi_cor)
    return np.sort(np.unique(extended))


def correct_zeros(rawspectra, copy=False):
    if copy:
        spectra = np.copy(rawspectra)
    else:
        spectra = rawspectra
    zero_idx = find_zeros(spectra)
    if zero_idx is not None:
        spectra[zero_idx] = np.median(spectra, axis=0)
    return spectra


def correct_saturated(inputspectra, map_shape=None, copy=False,
                     n_nearest_features=8, max_iter=44,
                     smoothen=True, lam=None):
    """
    Correct saturated spectra.

    Parameters:
    -----------
    rawspectra: 2D numpy array
        Your raw (!) input spectra that you want to correct
        Note that you
    map_shape: int or a tuple ints
        since this method """
    if isinstance(inputspectra, WDF):
        rawspectra = inputspectra.spectra
        map_shape = (inputspectra.n_y, inputspectra.n_x)
    else:
        rawspectra = inputspectra
    if lam == None:
        lam = rawspectra.shape[-1]//5
    spectra = correct_zeros(rawspectra, copy=copy)
    sat = find_saturated(spectra)
    saturated_idx = np.where(spectra==0)
    assert(sat == np.unique(saturated_idx[0])).all(), "Strange saturations.\n"+\
                "Check if you haven't done some normalization on the spectra beforehand."
    if len(sat) > 0:
        spectra[saturated_idx] = np.nan
        trt = get_neighbourhood(sat, map_shape)
        # The most important part:
        min_value = 0.75 * np.max(rawspectra[trt], axis=-1)
        imp = impute.IterativeImputer(n_nearest_features=n_nearest_features,
                                      max_iter=max_iter, skip_complete=True,
                                      min_value=min_value)
        # create an array so that trt[vrackalica] = sat
        vrackalica = np.array([np.argwhere(trt==i)[0][0] for i in sat])
        popravljeni = imp.fit_transform(spectra[trt].T).T[vrackalica]
        spectra[sat] = popravljeni
        if smoothen:
            upeglani = cc.baseline_als(popravljeni, lam=lam, p=0.6)
            is_changed = np.diff(saturated_idx[0], prepend=sat[0])!=0
            renormalizovani = []
            i = 0
            for cond in is_changed:
                if cond:
                    i+=1
                renormalizovani.append(i)
            novi = np.copy(saturated_idx)
            novi[0] = np.array(renormalizovani)
            novi = tuple(novi)
            spectra[saturated_idx] = upeglani[novi]
    return spectra


def remove_CRs(inputspectra, **initialization):
    
    mock_sp3 = inputspectra.spectra
    sigma_kept = inputspectra.x_values
    _n_x = inputspectra.n_x
    _n_y = inputspectra.n_y
    # a bit higher then median, or the area:
    scaling_koeff = np.trapz(mock_sp3, x=sigma_kept, axis=-1)[:, np.newaxis]
    mock_sp3 /= np.abs(scaling_koeff)
    normalized_spectra = np.copy(mock_sp3)
    # construct the footprint pointing to the pixels surrounding any given pixel:
    kkk = np.zeros((2*(_n_x+1) + 1, 1))
    # does this value change anything?
    kkk[[0, 1, 2, _n_x-1, _n_x+1, -3, -2, -1]] = 1

    # each pixel has the median value of its surrounding neighbours:
    median_spectra3 = median_filter(mock_sp3, footprint=kkk)

    # I will only take into account the positive values (CR):
    coarsing_diff = (mock_sp3 - median_spectra3)

    # find the highest differences between the spectra and its neighbours:
    bad_neighbour = np.quantile(coarsing_diff, 0.99, axis=-1)
    # The find the spectra where the bad neighbour is very bad:
    # The "very bad" limit is set here at 30*standard deviation (why not?):
    basic_candidates = np.nonzero(coarsing_diff > 40*np.std(bad_neighbour))
    sind = basic_candidates[0]  # the spectra containing very bad neighbours
    rind = basic_candidates[1]  # each element from the "very bad neighbour"
    if len(sind) > 0:
        # =====================================================================
        #               We want to extend the "very bad neighbour" label
        #           to ext_size adjecent family members in each such spectra:
        # =====================================================================
        npix = len(sigma_kept)
        ext_size = int(npix/50)
        if ext_size % 2 != 1:
            ext_size += 1
        extended_sind = np.stack((sind, )*ext_size, axis=-1).reshape(
            len(sind)*ext_size,)
        rind_stack = tuple()
        for ii in np.arange(-(ext_size//2), ext_size//2+1):
            rind_stack += (rind + ii, )
        extended_rind = np.stack(rind_stack, axis=-1).reshape(
            len(rind)*ext_size,)
        # The mirror approach for family members close to the border:
        extended_rind[np.nonzero(extended_rind < 0)] =\
            -extended_rind[np.nonzero(extended_rind < 0)]
        extended_rind[np.nonzero(extended_rind > len(sigma_kept)-1)] =\
            (len(sigma_kept)-1)*2 -\
            extended_rind[np.nonzero(extended_rind > len(sigma_kept)-1)]
        # remove duplicates (https://stackoverflow.com/a/36237337/9368839):
        _base = extended_sind.max()+1
        _combi = extended_rind + _base * extended_sind
        _vall, _indd = np.unique(_combi, return_index=True)
        _indd.sort()
        extended_sind = extended_sind[_indd]
        extended_rind = extended_rind[_indd]
        other_candidates = (extended_sind, extended_rind)
        mock_sp3[other_candidates] = median_spectra3[other_candidates]

        CR_cand_ind = np.unique(sind)
# =============================================================================
#         #CR_cand_ind = np.arange(len(spectra_kept))
#         _ss = np.stack((normalized_spectra[CR_cand_ind],
#                         mock_sp3[CR_cand_ind]), axis=-1)
#         check_CR_candidates = NavigationButtons(sigma_kept, _ss,
#                                                 autoscale_y=True,
#                                                 title=[
#                                                     f"indice={i}" for i in CR_cand_ind],
#                                                 label=['normalized spectra',
#                                                        'median correction'])
#         if len(CR_cand_ind) > 10:
#             plt.figure()
#             sns.violinplot(y=rind)
#             plt.title("Distribution of Cosmic Rays")
#             plt.ylabel("CCD pixel struck")
# =============================================================================
    else:
        print("No Cosmic Rays found!")
    inputspectra.spectra = mock_sp3
    return inputspectra
