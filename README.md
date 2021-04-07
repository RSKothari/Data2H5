
# Data2H5

This tool rapidly converts loose files scattered within any folder into a consolidated H5 file. This allows for faster read operations with lower memory requirement.
**Reasoning**: H5 files consolidate data in contiguous memory sectors. 

To learn more about how H5 files work, I refer the reader to this [fantastic article](https://www.oreilly.com/library/view/python-and-hdf5/9781491944981/ch04.html).

Features:
* H5 files speed up training
* Point and go - just give the paths!
* Utilizes all your cores to read data into H5
* Easy steps to incorporate H5 file into data loader
* Allows reading custom data formats by providing your own file reading function
* Allows complex file pruning by supplying your own extension matching routine

## Requirements

`conda install -c anaconda h5py`

`conda install -c conda-forge imageio`

## Commands

Suppose your loose files are spread across a folder. You can use this utility as such:

`python converter --path_images=<PATH_TO_FOLDER> --path_output=<PATH_ENDING_WITH_H5_FILE> --ext=jpg`

For example:

`python converter --path_images=/media/HDD/Gaze360 --path_output=/media/HDD/H5/Gaze360.h5`

## Operation

This script finds all files (images or otherwise) using the `os.walk` utility within a folder which matches the user specified extension. These data files are then consolidated into a single H5 file. Each file can be then be read directly from the H5 file using their **relative path** .
For example:

```
path_image_file = '<PATH_TO_FOLDER>/foo/boo/goo/image_0001.jpg'
data = cv2.imread(path_image_file)
```

can be replaced with:

```
path_h5 = '<PATH_ENDING_WITH_H5_FILE>'
h5_obj = h5py.File(path_h5, mode='r')
data = h5_obj['foo/boo/goo/image_0001.jpg'][:]
```

## Advantages
* Easy to manage
* H5 files improve speed of reading operation
* Lowers memory consumption by leveraging lossless compression
* Partially loads data instead of hosting on RAM - convenient for large datasets
* Utilizes caching to further improve reading speeds when reading same samples again and again

## Custom data types

You can specify a custom file extension by specifying `--ext=fancy_ext`. For example:

`python converter --path_images=<PATH_TO_FOLDER> --path_output=<PATH_ENDING_WITH_H5_FILE> --ext=json --custom_read_func`

You may then add your own custom reading logic in `my_functions.py` in the function `my_read`. To ensure the program reads your custom read function, please add the flag `--custom_read_func` which tells the script to ignore the default reader.

## Custom extension pruning!

You can provide your own file extension matching function in `my_prune` with the template provided by `--ext` flag. For example, if you want to match complex file extensions such as `.FoO0345` with a template extension string `foo`, then you can supply the following code as your own custom prune function.

```
def my_prune(filename_str, ext_str):
    # Logic to verify if the extension type is present
    # within the filename
    return True if ext_str in filename_str.lower() else False
```

## Data loader setup

To leverage H5 files into your training data loader, please refer to `benchmark.py`. There are three easy steps to follow:

* Step 1. Generate a list of all files used during training in the `init` function.
```
with h5py.File(path_h5, 'r') as h5_obj:
    self.file_list = list(h5_obj.keys())  # Each key is the relative path to file
```
* Step 2. Open the `H5` reader object **within** the `__getitem__` call. This creates a separate reader object for each individual worker.
```
if  not  hasattr(self, 'h5_obj'):
   self.h5_obj = h5py.File(self.path_h5, mode='r', swmr=True)
```
* Step 3. Add a safe closing operation for the H5 file.
```
def  __del__(self, ):
    self.h5_obj.close()
```
## Benchmarks

Coming soon!

## Contact

For more information, please feel free to reach out to me at rsk3900@rit.edu