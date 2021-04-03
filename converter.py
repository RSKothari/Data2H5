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
    def __init__(self, args):
        self.args_dict = vars(args)
        root_dir_file_list = self.create_tree()
        list_of_valid_datum = self.prune_tree(root_dir_file_list)
        self.list_of_valid_datum = self.generate_full_path(list_of_valid_datum)

    def generate_full_path(self, paths):
        full_paths = []
        for path in paths:
            vals = [join_path(path[0], ele) for ele in path[1]]
            full_paths.append(vals)
        return list(itertools.chain(*full_paths))

    def create_tree(self):
        return list(os.walk(self.args_dict['path_images']))

    def prune_tree(self, tree):
        list_of_valid_datum = []
        for (dir_, dirs, files) in tree:
            valid_files = self.prune_files(files)
            if any(valid_files):
                rel_root = os.path.relpath(dir_, self.args_dict['path_images'])
                list_of_valid_datum.append((rel_root, valid_files))
        return list_of_valid_datum

    def prune_files(self, files):
        if any(files):
            return [fi for fi in files if fi.endswith(self.args_dict['ext'])]
        else:
            return []

    def log_sample(self, h5_obj, datum):
        key, data = datum
        h5_obj.create_dataset(key,
                              data.shape,
                              data=data,
                              dtype=str(data.dtype),
                              chunks=True,
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
            from my_functions import my_read
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
        path_image = join_path(self.args_dict['path_images'], path_sample)
        image = imageio.imread(path_image)
        return path_sample, image


if __name__ == '__main__':
    args = make_args()
    obj = capture_within_H5(args)

    # %% Begin reading and writing to H5
    obj.read_write()
