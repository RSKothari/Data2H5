# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 08:33:52 2021

@author: Rudra
"""
import os
import h5py
import tqdm
import imageio
import itertools
import multiprocessing as mp

from args_maker import make_args


def join_path(path_left, path_right):
    return os.path.join(path_left, path_right)


class capture_within_H5():
    '''
    A class to find all files with the given extension and store them
    into a H5 file.
    '''
    def __init__(self, args):
        # Initialize the converter and generate a list of valid files
        self.args_dict = args
        root_dir_file_list = self.create_tree()
        list_of_valid_datum = self.prune_tree(root_dir_file_list)
        self.list_of_valid_datum = self.generate_full_path(list_of_valid_datum)

    def generate_full_path(self, paths):
        # Given a list of os.walk tuples, append the root path
        # to all individual relative paths
        full_paths = []
        for path in paths:
            vals = [join_path(path[0], ele) for ele in path[1]]
            full_paths.append(vals)
        return list(itertools.chain(*full_paths))

    def create_tree(self):
        # Generate a tree of a files in a given directory
        return list(os.walk(self.args_dict['path_images']))

    def prune_tree(self, tree):
        # Prune a tree by only accepting files which match the
        # provided file extension
        list_of_valid_datum = []
        for (dir_, _, files) in tree:
            valid_files = self.prune_files(files)
            if any(valid_files):
                rel_root = os.path.relpath(dir_, self.args_dict['path_images'])
                list_of_valid_datum.append((rel_root, valid_files))
        return list_of_valid_datum

    def prune_files(self, files):
        if any(files):
            if self.args_dict['custom_prune_func']:
                return [fi for fi in files
                        if my_prune(fi, self.args_dict['ext'])]
            else:
                return [fi for fi in files
                        if self.default_prune(fi, self.args_dict['ext'])]
        else:
            return []

    def log_sample(self, h5_obj, datum):
        key, data = datum
        h5_obj.create_dataset(key,
                              data.shape,
                              data=data,
                              dtype=str(data.dtype),
                              chunks=data.shape,
                              compression='lzf')

    def read_write(self, ):
        # create a pool
        if self.args_dict['single_process']:
            _ = list(map(self.read_function,
                         tqdm.tqdm(self.list_of_valid_datum)))
        else:

            h5_obj = h5py.File(self.args_dict['path_output'], 'a')

            pool = mp.Pool(processes=mp.cpu_count())
            num_entries = len(self.list_of_valid_datum)
            num_per_cyc = 4*mp.cpu_count()

            # Read data in splits so that it is easy on the RAM
            for idx in tqdm.tqdm(range(1 + num_entries // num_per_cyc)):

                start_loc = max([idx * num_per_cyc, 0])
                end_loc = min([(idx + 1) * num_per_cyc, num_entries])

                results = pool.map(self.read_function,
                                   self.list_of_valid_datum[start_loc:end_loc])

                # Write out results as a single process
                for result in results:
                    self.log_sample(h5_obj, result)

            h5_obj.close()

            pool.close()
            pool.join()

    def read_function(self, path_sample):

        if self.args_dict['custom_read_func']:
            data = my_read(path_sample)
        else:
            data = self.default_reader(path_sample)

        if self.args_dict['single_process']:

            h5_obj = h5py.File(self.args_dict['path_output'], 'a')
            self.log_sample(h5_obj, data)
            h5_obj.close()

            return True
        else:
            return data

    def default_reader(self, path_sample):
        # Read operation for jpg or png images
        path_image = join_path(self.args_dict['path_images'], path_sample)
        image = imageio.imread(path_image)
        return path_sample, image
    
    def default_prune(self, filename_str, ext_str):
        # Given an input file name, return true if they match else False
        return filename_str.endswith(ext_str)


if __name__ == '__main__':
    args = vars(make_args())
    obj = capture_within_H5(args)
    
    if args['custom_read_func']:
        from my_functions import my_read

    if args['custom_prune_func']:
        from my_functions import my_prune

    # %% Delete and create a new H5 file
    h5_obj = h5py.File(args['path_output'], 'w')
    h5_obj.close()

    # %% Begin reading and writing to H5
    obj.read_write()
