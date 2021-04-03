# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 08:36:27 2021

@author: Rudra
"""

import os
import h5py
import argparse
from pprint import pprint


def make_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--single_process', action='store_true',
                        help='run on a single core for some reason')
    parser.add_argument('--no_compress', action='store_true',
                        help='deactivate lossless compression for some reason')
    parser.add_argument('--ext', default='jpg',
                        help='specify png or jpg to select ext. default: jpg')
    parser.add_argument('--custom_read_func', action='store_true',
                        help='use custom read function? ')

    required_args = parser.add_argument_group('required named arguments')
    required_args.add_argument('--path_images', required=True,
                               help='abs path to image directory',
                               default='D:/Datasets/Gaze360/imgs')
    required_args.add_argument('--path_output', required=True,
                               help='abs path to output H5 file',
                               default='D:/exp.h5')
    args = parser.parse_args()
    pprint(vars(args))

    # Fix path and make them OS dependent
    args.path_images = os.path.abspath(args.path_images)
    args.path_output = os.path.abspath(args.path_output)

    # Delete and create a new H5 file
    h5_obj = h5py.File(args.path_output, 'w')
    h5_obj.close()

    return args
