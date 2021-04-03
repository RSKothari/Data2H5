# Data2H5

This tool rapidly converts loose files scattered within any folder into a consolidated H5 file. This allows for faster read operations with lower memory requirement.
**Reasoning**: H5 files consolidate data in contiguous memory sectors. 
To learn more about how H5 files work, I refer the reader to this [fantastic article](https://www.oreilly.com/library/view/python-and-hdf5/9781491944981/ch04.html).

## Requirements

`conda install -c anaconda h5py`

`conda install -c conda-forge imageio`

## Commands
Suppose your loose files are spread across a folder. You can use this utility as such:

`python converter --path_images=<PATH_TO_FOLDER> --path_output=<PATH_ENDING_WITH_H5_FILE> --ext=jpg`

For example:

`python converter --path_images=/media/HDD/Gaze360 --path_output=/media/HDD/H5/Gaze360.h5`

## Operation

This script finds all files with the user specified extension within a folder. It uses the `os.walk` utility to find and read all valid data files. These data files can be extracted using their **relative path** from the folder they were extracted.
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

Note that `[:]` in the end reads `data` by value. The command preceding `[:]`  is a reference to `data`.

## Advantages

Reading speed increases, lower memory consumption

## Custom data types

You can specify a custom data format by specifying `--ext=fancy_ext`. For example:

`python converter --path_images=<PATH_TO_FOLDER> --path_output=<PATH_ENDING_WITH_H5_FILE> --ext=json --custom_read_func`

You may then add your own custom reading logic in `my_functions.py` in the function `my_read`. To ensure the program reads your custom logic function, please be sure to add a flag `--custom_read_func` which indicates the same.

## Data loader tricks

Coming soon!

## Benchmarks

Coming soon!

## Contact

For more information, please feel free to reach out to me at rsk3900@rit.edu