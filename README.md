# MultiProcessTools -- A Lazy Way to Handle Parallel Processing via a Shared Filesystem in Python

MultiProcessTools is a very lightweight toolkit for lazily handling shared filesystem parallel computations through tempfile creation and collection. In particular, MultiProcessTools introduces a MultiProcessHelper class which can create empty tempfiles as placeholder for a computation as it is running. MultiProcessHelper also keeps track of the tempfiles that have been created and deleted, and allows you to easily perform garbage collection via a cleanup method.

This project is in its infancy and much of the code is actively being developed (and deleted), so expect major refactoring until future versions specify otherwise. 

MultiProcessTools was developed to assist in the computational biology work done in the Terskih Lab at SBP Medical Discovery Institute.


## Usage

Import multiprocesshelper, initialize the helper

    from multiprocesstools import multiprocesshelper

    mph = multiprocesshelper(
            name = "my_analysis",
            working_directory = "path/to/my/output/location",
            loggers = [
                "my_analysis_logger1", "my_analysis_logger2", 
                "my_analysis_logger3", "my_analysis_logger4", 
                ],
    )

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

In the case of catastrophic failures and the program needs to end, simply use the cleanup method to delete all tempfiles & close all loggers created by & associated with your multiprocesshelper

    ... Program catastrophically fails ...
    except:
        ... Handle error ...
        mph.cleanup()
