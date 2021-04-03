# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 16:48:31 2021

@author: Rudra
"""
import os
import cv2
import tqdm
import time
import h5py
import torch
import numpy as np

from args_maker import make_args


def join_path(path_left, path_right):
    return os.path.join(path_left, path_right)


class benchmark(torch.utils.data.Dataset):
    def __init__(self, path_h5, path_folder, mode='H5'):

        self.path_h5 = path_h5
        self.path_folder = path_folder
        self.read_from_H5 = True if mode == 'H5' else False

        with h5py.File(path_h5, 'r') as h5_obj:
            self.file_list = list(h5_obj.keys())
            
    def __del__(self, ):
        self.h5_obj.close()

    def __len__(self, ):
        return len(self.file_list)

    def __getitem__(self, idx):

        entry_str = self.file_list[idx]

        if self.read_from_H5:
            if not hasattr(self, 'h5_obj'):
                self.h5_obj = h5py.File(self.path_h5, mode='r', swmr=True)
            datum = self.h5_obj[entry_str][:]
        else:
            path_file = join_path(self.path_folder, entry_str)
            datum = cv2.imread(os.path.abspath(path_file))
        datum = cv2.resize(datum,
                           (224, 244),
                           interpolation=cv2.INTER_LANCZOS4)
        return datum


if __name__ == '__main__':

    args = vars(make_args())

    bench_obj = benchmark(args['path_output'], args['path_images'])
    loader = torch.utils.data.DataLoader(bench_obj,
                                         batch_size=48,
                                         num_workers=4)

    for epoch in range(3):
        time_elapsed = []
        start_time = time.time()
        for bt, data in enumerate(tqdm.tqdm(loader)):
            end_time = time.time()
            time_elapsed.append(end_time - start_time)
            start_time = time.time()

        time_elapsed = np.array(time_elapsed)
        t_mean = 1/np.mean(time_elapsed)
        t_std = np.std(1/time_elapsed)
        print('Ep: {}. Bts/Sec. Mean: {}. STD: {}'.format(epoch,
                                                          np.round(t_mean, 2),
                                                          np.round(t_std, 2)))
