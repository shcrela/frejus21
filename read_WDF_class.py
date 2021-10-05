# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import os
import io
import time
import pandas as pd
from scipy.signal import oaconvolve
import matplotlib.pyplot as plt
from PIL import Image, ImageFile
import constants_WDF_class as const
# import visualize as vis

ImageFile.LOAD_TRUNCATED_IMAGES = True


def convert_time(t):
    """Convert the Windows 64bit timestamp to human readable format.

    Input:
    -------
        t: timestamp in W64 format (default for .wdf files)
    Output:
    -------
        string formatted to suit local settings

    Example:
    -------
        >>> time_of_spectrum_recording =
          [convert_time(x) for x in origins.iloc[:,4]]

        should give you the list with the times on which
        each specific spectrum was recorded
    """
    return time.strftime('%c', time.gmtime((t/1e7-11644473600)))


def reorder(ar, n_columns, n_rows, method):
    nx = n_columns
    ny = n_rows
    vertical = ["Alternating", "StreamLine", "Alternating2"]
    if method in ["StreamLine", "Alternating2"]: # need to inverse
        nx = n_rows
        ny = n_columns
    try:
        if ar.ndim == 1:
            arr = ar.reshape(ny, nx)
        elif ar.ndim == 2:
            arr = ar.reshape((ny, nx, ar.shape[-1]))
        else:
            print("WTF?!")
    except ValueError:
        raise ValueError("Can't deal with incompleted scans yet.\n"
        f"You have recorded only {int(ar.size/ar.shape[-1])} "
        f"out of {nx*ny} spectra.\n"
        "You can try reading your data with read_WDF function.")
    if method == "InvertedRows":
        reordered = np.array([arr[i][::-1] if i&1 else arr[i] for i in range(ny)])
    elif method in vertical:
        reordered = np.rot90(arr, axes=(0, 1))
    else:
        reordered = arr
    return reordered.reshape(ar.shape)

def _read(f, dtype=np.uint32, count=1):
    """Reads bytes from binary file,
    with the most common values given as default.
    Returns the value itself if one value, or list if count > 1
    Note that you should do ".decode()"
    on strings to avoid getting strings like "b'string'"
    For further information, refer to numpy.fromfile() function
    """
    if count == 1:
        return np.fromfile(f, dtype=dtype, count=count)[0]
    else:
        return np.fromfile(f, dtype=dtype, count=count)[0:count]


class WDF(object):
    """
    Read data from the binary .wdf file.

    Parameters:
    -----------
    file: string
        full (absolute or relative) path to the .wdf file
    verbose: bool
        Weather you want to print the informations about the file.
    Attributes:
    -----------
    spectra: numpy array
        that's why we're here :)
    x_values: numpy array
        the x-axis of your spectra
    origins: pandas dataframe
        contains information about each individual point of measurement
    params: dict
        contains general informations about the measurement
    map_params: dict : (returned if the measurement is of type map)
        dictionary containing informations about the map
    n_x, n_y, n_z : ints
        number of steps in each direction (same as in map_params["NbSteps"])
    ncollected, nspectra: ints
        number of spectra collected, number of spectra expected
        same as: params["Count"], params["Capacity"]
    npoints: int
        number of points in each spectrum
        same as params["PointsPerSpectrum"]
        should be equal to len(x_values) = spectra.shape[-1]
    filename: string
        the name of the file (without the path)
    folder: string
        the folder containing the file
    b_off: list of ints
        offsets in bytes for each of the blocks found in the file
    block_names: list of strings
        names of each block found in the file
    block_sizes: list of ints
        sizes of each block in bytes




    """
    def __init__(self, file, verbose=False):

        self.folder, self.filename = os.path.split(file)
        self.verbose = verbose
        try:
            f = open(file, "rb")
            if self.verbose:
                print(f'Reading the file: \"{self.filename}\"\n')
        except IOError:
            raise IOError(f"File {file} does not exist!")
        self.filesize = os.path.getsize(file)
        self.block_names = []
        self.block_sizes = []
        self.b_off = []
        self.params = {}
        self.map_params = {}

        # Reading all of the block names, offsets and sizes
        offset = 0
        while offset < self.filesize - 1:
            f.seek(offset)
            self.b_off.append(offset)
            block_header = np.fromfile(f, dtype=const.HEADER_DT, count=1)
            offset += block_header['block_size'][0]
            self.block_names.append(block_header['block_name'][0].decode())
            self.block_sizes.append(block_header['block_size'][0])

        name = 'WDF1'
        gen = [i for i, x in enumerate(self.block_names) if x == name]
        for i in gen:
            self.print_block_header(name, i)
            f.seek(self.b_off[i]+16)
    #        TEST_WDF_FLAG = _read(f,np.uint64)
            self.params['WdfFlag'] = const.WDF_FLAGS[_read(f, np.uint64)]
            f.seek(60)
            self.params['PointsPerSpectrum'] = self.npoints = _read(f)
            # Number of spectra expected (nspectra):
            self.params['Capacity'] = self.nspectra = _read(f, np.uint64)
            # Number of spectra written into the file (ncollected):
            self.params['Count'] = self.ncollected = _read(f, np.uint64)
            # Number of accumulations per spectrum:
            self.params['AccumulationCount'] = _read(f)
            # Number of elements in the y-list (>1 for image):
            self.params['YlistLength'] = _read(f)
            self.params['XlistLength'] = _read(f)  # number of elements in the x-list
            self.params['DataOriginCount'] = _read(f)  # number of data origin lists
            self.params['ApplicationName'] = _read(f, '|S24').decode()
            version = _read(f, np.uint16, count=4)
            self.params['ApplicationVersion'] = '.'.join(
                [str(x) for x in version[0:-1]]) +\
                ' build ' + str(version[-1])
            m_flag = _read(f)
            self.params['ScanType'] = const.SCAN_TYPES.get(m_flag, m_flag)
            m_flag = _read(f)
            self.params['MeasurementType'] = const.MEASUREMENT_TYPES.get(m_flag, m_flag)
            self.params['StartTime'] = convert_time(_read(f, np.uint64))
            self.params['EndTime'] = convert_time(_read(f, np.uint64))
            m_flag = _read(f)
            self.params['SpectralUnits'] = const.DATA_UNITS.get(m_flag, m_flag)
            self.params['LaserWaveLength'] = np.round(10e6/_read(f, '<f'), 2)
            f.seek(240)
            self.params['Title'] = _read(f, '|S160').decode()
        if self.verbose:
            for key, val in self.params.items():
                print(f'{key:-<40s} : \t{val}')
            if self.nspectra != self.ncollected:
                print(f'\nATTENTION:\nNot all spectra were recorded\n'
                      f'Expected nspectra={self.nspectra},'
                      f'while ncollected={self.ncollected}'
                      f'\nThe {self.nspectra-self.ncollected} missing values'
                      f'will be shown as blanks\n')

        name = 'WMAP'
        gen = [i for i, x in enumerate(self.block_names) if x == name]
        for i in gen:
            self.print_block_header(name, i)
            f.seek(self.b_off[i] + 16)
            m_flag = _read(f)
            self.map_params['MapAreaType'] = const.MAP_TYPES.get(m_flag, m_flag)
            _read(f)
            self.map_params['InitialCoordinates'] = np.round(_read(f, '<f', count=3), 2)
            self.map_params['StepSizes'] = np.round(_read(f, '<f', count=3), 2)
            self.map_params['NbSteps'] = _read(f, np.uint32, count=3)
            self.n_x, self.n_y = self.map_params["NbSteps"][self.map_params["NbSteps"]>1]
            self.map_params['LineFocusSize'] = _read(f)
        if self.verbose:
            for key, val in self.map_params.items():
                print(f'{key:-<40s} : \t{val}')

        name = 'DATA'
        gen = [i for i, x in enumerate(self.block_names) if x == name]
        for i in gen:
            data_points_count = self.npoints * self.ncollected
            self.print_block_header(name, i)
            f.seek(self.b_off[i] + 16)
            self.spectra = _read(f, '<f', count=data_points_count)\
                .reshape(self.ncollected, self.npoints)
            if verbose:
                print(f'{"The number of spectra":-<40s} : \t{self.spectra.shape[0]}')
                print(f'{"The number of points in each spectra":-<40s} : \t'
                      f'{self.spectra.shape[1]}')
            if self.params['MeasurementType'] == 'Map':
                self.spectra = reorder(self.spectra, self.n_x, self.n_y,
                                       self.map_params["MapAreaType"])


        name = 'XLST'
        gen = [i for i, x in enumerate(self.block_names) if x == name]
        for i in gen:
            self.print_block_header(name, i)
            f.seek(self.b_off[i] + 16)
            m_flag = _read(f)
            self.params['XlistDataType'] = const.DATA_TYPES.get(m_flag, m_flag)
            m_flag = _read(f)
            self.params['XlistDataUnits'] = const.DATA_UNITS.get(m_flag, m_flag)
            self.x_values = _read(f, '<f', count=self.npoints)
        if self.verbose:
            print(f"{'The shape of the x_values is':-<40s} : \t{self.x_values.shape}")
            print(f"*These are the \"{self.params['XlistDataType']}"
                  f"\" recordings in \"{self.params['XlistDataUnits']}\" units")

    # It is not clear what the next block is for:
        name = 'YLST'
        gen = [i for i, x in enumerate(self.block_names) if x == name]
        for i in gen:
            self.print_block_header(name, i)
            f.seek(self.b_off[i] + 16)
            m_flag = _read(f)
            self.params['YlistDataType'] = const.DATA_TYPES.get(m_flag, m_flag)
            m_flag = _read(f)
            self.params['YlistDataUnits'] = const.DATA_UNITS.get(m_flag, m_flag)
            self.test_ylist = _read(f)
            if self.block_sizes[i] > 28:
                self.y_values = _read(f, '<f', count=int((self.block_sizes[i]-16)/4))
                if self.verbose:
                    print("There's something here!")
                    print(f"{'Its size is':-<40s} : \t{self.y_values.shape}")
            else:
                if self.verbose:
                    print("*Nothing here.")

        name = 'WHTL'
        gen = [i for i, x in enumerate(self.block_names) if x == name]
        for i in gen:
            self.print_block_header(name,i)
            f.seek(self.b_off[i] + 16)
            img_bytes = _read(f, count=int((self.block_sizes[i]-16)/4))
            img = Image.open(io.BytesIO(img_bytes))
            self.img_arr = np.array(img.getdata()).reshape(
                                        img.size[1], img.size[0], -1)
            self.img_exif = dict()
            for tag, value in img._getexif().items():
                decodedTag = const.EXIF_TAGS.get(tag, tag)
                self.img_exif[decodedTag] = value
            try:
                dunit = self.img_exif["FocalPlaneResolutionUnit"]
                self.img_exif["FocalPlaneResolutionUnit"] = \
                const.DATA_UNITS.get(dunit, dunit)
            except:
                pass

        name = 'WXDB'
        gen = [i for i, x in enumerate(self.block_names) if x == name]
        if len(gen) > 0:
            self.imgs = []
            self.img_sizes = []
            self.img_psets = dict()
            for i in gen:
                self.print_block_header(name,i)
                f.seek(self.b_off[i] + 16)
                self.img_offsets = _read(f, dtype='u8', count=self.nspectra)
                for nn, j in enumerate(self.img_offsets):
                    f.seek(int(j+self.b_off[i]))
                    size = _read(f)
                    self.img_sizes.append(size)
                    img_type = _read(f, dtype=np.uint8)
                    img_flag = _read(f, dtype=np.uint8)
                    img_key = _read(f, dtype=np.uint16)
                    img_size = _read(f)
                    img_length = _read(f)
                    self.img_psets[nn] = {"img_type": img_type,
                                     "img_flag": img_flag,
                                     "img_key": img_key,
                                     "img_size": img_size,
                                     "img_length": img_length}

    #                 img_bytes = _read(f, count=int(size/4 -1))
    #                 self.imgs.append(io.BytesIO(img_bytes))


        name = 'ORGN'
        origin_labels = []
        origin_set_dtypes = []
        origin_set_units = []
        origin_values = np.empty((self.params['DataOriginCount'],
                                  self.nspectra), dtype='<d')
        gen = [i for i, x in enumerate(self.block_names) if x == name]
        for i in gen:
            self.print_block_header(name, i)
            f.seek(self.b_off[i] + 16)
            nb_origin_sets = _read(f)
            # The above is the same as params['DataOriginCount']
            for set_n in range(nb_origin_sets):
                data_type_flag = _read(f).astype(np.uint16)
                # not sure why I had to add the astype part,
                # but if I just read it as uint32, I got rubbish sometimes
                origin_set_dtypes.append(const.DATA_TYPES.get(data_type_flag,
                                                              data_type_flag))
                m_flag = _read(f)
                origin_set_units.append(const.DATA_UNITS.get(m_flag, m_flag))
                origin_labels.append(_read(f, '|S16').decode())
                if data_type_flag == 11:
                    origin_values[set_n] = _read(f, np.uint64, count=self.nspectra)
                    # special case for reading timestamps
                else:
                    origin_values[set_n] = np.round(
                        _read(f, '<d', count=self.nspectra), 2)

                if self.params['MeasurementType'] == 'Map':
                    origin_values[set_n] = reorder(origin_values[set_n],
                                                   self.n_x, self.n_y,
                                                   self.map_params['MapAreaType'])
        if self.verbose:
            print('\n\n\n')
        self.origins = pd.DataFrame(origin_values.T,
                               columns=[f"{x} ({d})" for (x, d) in \
                                        zip(origin_labels, origin_set_units)])
        try:
            self.xres = float(self.img_exif["FocalPlaneXResolution"]) /\
                    self.img_arr.shape[1]  # in µ/px
            self.yres = float(self.img_exif["FocalPlaneYResolution"]) /\
                    self.img_arr.shape[0]  # in µ/px

            self.xminpx, self.yminpx = (round(
                                        (self.map_params["InitialCoordinates"][0] -
                                         self.img_exif["FocalPlaneXYOrigins"][0])
                                           /self.xres),
                                        round(
                                        (self.map_params["InitialCoordinates"][1] -
                                         self.img_exif["FocalPlaneXYOrigins"][1])
                                           /self.yres))

            self.xmaxpx = self.xminpx + round(self.map_params["StepSizes"][0] *
                                              self.map_params["NbSteps"][0] / self.xres)
            self.ymaxpx = self.yminpx + round(self.map_params["StepSizes"][1] *
                                              self.map_params["NbSteps"][1] / self.yres)

            self.xminpx, self.xmaxpx = np.sort([self.xminpx, self.xmaxpx])
            self.yminpx, self.ymaxpx = np.sort([self.yminpx, self.ymaxpx])

            self.xsizepx = self.xmaxpx - self.xminpx
            self.ysizepx = self.ymaxpx - self.yminpx
            grid_in_image = (self.xsizepx <= np.size(self.img_arr, 1)) &\
                            (self.ysizepx <= np.size(self.img_arr, 0))
            reducing_makes_sense = (self.xres < self.map_params["StepSizes"][0]) &\
                                   (self.xres < self.map_params["StepSizes"][0])
            if grid_in_image :
                kernel_shape = np.abs(np.array((
                                round(self.map_params['StepSizes'][0]/self.xres),
                                round(self.map_params['StepSizes'][1]/self.yres))))
                kernel = np.zeros(kernel_shape, dtype=bool)

                xpx_off = int((self.n_x * kernel_shape[1] - self.xsizepx)/2) # + 1
                ypx_off = int((self.n_y * kernel_shape[0] - self.ysizepx)/2) # + 1

                cropped_img = self.img_arr[self.yminpx-ypx_off : self.ymaxpx+ypx_off,\
                                           self.xminpx-xpx_off : self.xmaxpx+xpx_off,:]

                # ydim = np.size(cropped_img, 0)//kernel_shape[0]
                # xdim = np.size(cropped_img, 1)//kernel_shape[1]
                if reducing_makes_sense:
                    if self.params["ScanType"] in ["StreamLine", "StreamLineHR"]:
                        kernel[:, round(kernel_shape[1]/2)] = 1
                    elif self.params["ScanType"] in ["Point", "Static"]:
                        kernel[round(kernel_shape[1]/2), round(kernel_shape[1]/2)] = 1
                    else:
                        kernel = 1
                    self.img_reduced = oaconvolve(cropped_img,
                                        kernel[:,:,None],
                                        'valid')[::kernel_shape[0],::kernel_shape[1],:]
                    self.img_reduced = (255 * self.img_reduced /\
                                        self.img_reduced.max()).astype(int)
                else:
                    self.img_reduced = self.img_arr[self.yminpx : self.ymaxpx,\
                                                    self.xminpx : self.xmaxpx]
        except:
            print("Problem loading image")

    def show_grid(self, alpha=0.1):
        self.fig, self.ax = plt.subplots()
        self.ax.imshow(self.img_arr)
        # map_zone = Rectangle((self.xminpx, self.yminpx), self.xsizepx, self.ysizepx)
        # ax.add_patch(map_zone)
        x_pxvals = np.linspace(self.xminpx, self.xmaxpx, self.map_params["NbSteps"][0])
        y_pxvals = np.linspace(self.yminpx, self.ymaxpx, self.map_params["NbSteps"][1])
        for xxx in x_pxvals:
            self.ax.vlines(xxx, ymin=self.yminpx, ymax=self.ymaxpx, lw=1, alpha=alpha)
        for yyy in y_pxvals:
            self.ax.hlines(yyy, xmin=self.xminpx, xmax=self.xmaxpx, lw=1, alpha=alpha)
        # ax.scatter(self.xminpx, self.yminpx, marker="X", s=50, c='r')
        # self.fig.show()

    def print_block_header(self, name, i):
        if self.verbose:
            print(f"\n{' Block : '+ name + ' ':=^80s}\n"
                  f"size: {self.block_sizes[i]}, offset: {self.b_off[i]}")
