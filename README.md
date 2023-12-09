# MultiProcessTools -- A Quick Way to Handle Parallel Processing via a Shared Filesystem in Python

MultiProcessTools is a very lightweight toolkit for quickly handling shared filesystem parallel analysis through tempfile creation and collection.

In scientific research we are often running the exact same computation on many different files. For instance, you may be performing segmentation and feature extraction on thousands of images. Is there any way to speed this up? Yes! Parallel computing.

Isn't this problem already solved you may ask; there are packages like [Joblib](https://joblib.readthedocs.io/en/stable/) and even python itself has [native multiprocessing](https://docs.python.org/3/library/concurrent.futures.html). Indeed, but these only work on a single machine: they do not easily lend themselves to cross-machine computing (cluster computing).

You may say yet again this problem has already been rigorously solved via networking (e.g. [Dask](https://www.dask.org)). True, but this requires effort, time, and planning ahead in your code: you're a scientist not a software dev... What if want a quick and dirty way to parrallelize a shared computation performed on many files across your node cluster without all of that setup and coding? What if your collaborators just gave you access to run a few things on their larger server and you don't have a lot of time to network?

In comes MultiProcessTools! We solve this problem by simply coordinating all jobs through the shared file system. In particular, MultiProcessTools introduces a MultiProcessHelper class which can create empty tempfiles as a placeholder for a computation as it is running. MultiProcessHelper also keeps track of the tempfiles that have been created and deleted, and allows you to easily perform garbage collection via a cleanup method. All you need to do is add in a few lines to your script and then you can execute it on any number of machines without conflicts, so long as they share a filesystem.

This project is in its infancy and much of the code is actively being developed (and deleted), so expect major refactoring until future versions specify otherwise. 

MultiProcessTools was developed to assist in the computational biology work done in the Terskih Lab at SBP Medical Discovery Institute.

Please feel free to reach out to Martin with any questions regarding EpiLands @ malvarezkuglen@sbpdiscovery.org

## Basic Usage

Import multiprocesshelper, initialize the helper

```python
from multiprocesstools import multiprocesshelper

mph = multiprocesshelper(
        name = "my_analysis",
        working_directory = "path/to/my/output/location",
        loggers = [
            "my_analysis_logger1", 
            "my_analysis_logger2", 
            "my_analysis_logger3", 
            "my_analysis_logger4", 
            ],
)
```

Basic usage of a multiprocesshelper in a script. Generally you will do the following 
1) Create a directory where you are saving your results
2) Iterate over the files needed to be analyzed in parallel
3) Create a tempfile & check if it is available
   1) Note that path may be the string name provided to "create_directory" or it may be the entire path, so long as it exists as either a key or value in mph.directories.
4) Perform the analysis with error handling
5) Save the results as final_file_name
   1) It is crucial that you save this file under the exact name you specify as "final_file_name", and in the same directory as specified in path. This is how multiprocesshelper knows which files are finished, in progress, or not even started.
6) Delete the tempfile
7) Cleanup if needed

```python
if name == "__main__":
    mph.create_directory("my_analysis_results")
    for f in files_to_analyze:
        file_name = f.split(".")[0]
        final_file_name = file_name + "_analyzed.csv"
        temp_file_name = file_name + ".tmp"

        file_is_available = mph.create_temp_file(
            final_file_name = final_file_name,
            temp_file_name = temp_file_name,
            path = "my_analysis_results"

        )
        if file_is_available == False:
            continue
        try:

            .... Perform analysis ....


            ... Save the results with name assigned to final_file_name ...

            mph.delete_tempfile(
                temp_file_name = temp_file_name,
                path = "my_analysis_results"
            )
        
        except:

            ... Log exception ...
        
            mph.delete_tempfile(
                temp_file_name = temp_file_name,
                path = "my_analysis_results"
            )
```

In the case of catastrophic failures and the program needs to end, simply use the cleanup method to delete all tempfiles & close all loggers created by & associated with your multiprocesshelper

```python
... Program catastrophically fails ...
except:
    ... Handle error ...
    mph.cleanup()
```
