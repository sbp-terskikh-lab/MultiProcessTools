# MultiProcessTools -- A Lazy Way to Handle Parallel Processing via a Shared Filesystem in Python

MultiProcessTools is a very lightweight toolkit for lazily handling shared filesystem parallel computations through tempfile creation and collection. In particular, MultiProcessTools introduces a MultiProcessHelper class which can create empty tempfiles as placeholder for a computation as it is running. MultiProcessHelper also keeps track of the tempfiles that have been created and deleted, and allows you to easily perform garbage collection via a cleanup method.

This project is in its infancy and much of the code is actively being developed (and deleted), so expect major refactoring until future versions specify otherwise. 

MultiProcessTools was developed to assist in the computational biology work done in the Terskih Lab at SBP Medical Discovery Institute.