import os
import sys
import numpy as np
import time
import logging
from typing import List

# from .tools import create_logger_handlers
from ..functions.create_logger_handlers import create_logger_handlers
from ..functions.close_logger import close_logger

logger = logging.getLogger("MultiProcessTools")


class MultiProcessHelper:
    def __init__(
        self,
        pipe_name: str,
        working_directory: str,
        sub_directories: dict,
        loggers: List[str],
    ):
        time.sleep(np.random.random())
        # Initialize variables, type checks, and create output directories
        self.tempfiles = []
        self.directories = {}
        self.loggers = []
        if not os.path.exists(working_directory):
            raise ValueError(f"working_directory does not exist: {working_directory}")

        self._initialize_instance_number(file_name=pipe_name, path=working_directory)
        self._initialize_directories(
            working_directory=working_directory,
            sub_directories=sub_directories,
        )
        self._initialize_loggers(
            log_name=pipe_name,
            job_names=loggers,
            log_path=working_directory,
            instance_number=self.instance_number,
        )
        logger = logging.getLogger(loggers[0])
        logger.info(f"Instance number: {self.instance_number}")
        for directory in self.directories.keys():
            logger.info(f"{directory}: {self.directories[directory]}")

    def _initialize_instance_number(self, file_name: str, path: str) -> None:
        """Initialize the instance_number number"""
        instance_number = 0
        valid_instance = False
        while valid_instance == False:
            instance_number += 1
            valid_instance = self.create_temp_file(
                final_file_name=f"{file_name}{instance_number}.tmp",
                temp_file_name=f"{file_name}{instance_number}.tmp",
                path=path,
            )
        self.instance_number = instance_number

    def _initialize_directories(
        self,
        working_directory: str,
        sub_directories: dict,
    ) -> None:
        if os.path.isdir(working_directory):
            self.directories["working_directory"] = working_directory
        else:
            try:
                os.makedirs(working_directory)
                self.directories["working_directory"] = working_directory
            except:
                raise ValueError(f"{working_directory} is not a valid path")
        if not isinstance(sub_directories, list):
            raise ValueError(
                f"sub_directories be a list, but {type(sub_directories)} was given"
            )
        for dir_name in sub_directories:
            self.create_directory(dir_name=dir_name)

    def _initialize_loggers(
        self,
        log_name: str,
        job_names: List[str],
        log_path: str,
        instance_number: int,
    ) -> None:
        """Initialize the object loggers"""
        for job_name in job_names:
            create_logger_handlers(
                job_name=job_name,
                log_name=f"{log_name}{instance_number}.log",
                log_path=log_path,
                instance_number=instance_number,
            )
            self.loggers.append(job_name)

    def create_directory(self, dir_name):
        path = os.path.join(self.directories["working_directory"], dir_name)
        os.makedirs(path, exist_ok=True)
        self.directories[dir_name] = path

    def get_directory(self, dir_name):
        if dir_name in self.directories.keys():
            return self.directories[dir_name]
        elif os.path.isdir(dir_name):
            return dir_name
        else:
            raise ValueError(
                f"{dir_name} is not in self.directories and is not a valid path"
            )

    def close_all_loggers(self) -> None:
        for logger_name in self.loggers:
            close_logger(logger_name)
            self.loggers.remove(logger_name)

    def create_temp_file(
        self, final_file_name: str, temp_file_name: str, path: str
    ) -> bool:
        """
        Creates a temporary file with the given name.
        returns true if the file was created successfully, false if the file exists.
        """
        path = self.get_directory(path)
        temp_file = os.path.join(path, temp_file_name)
        if os.path.exists(temp_file):
            return False
        final_file = os.path.join(path, final_file_name)
        if os.path.exists(final_file):
            return False
        # time.sleep(np.random.uniform(0.01,0.5))
        try:
            f = open(temp_file, "x")
            f.close()
            self.tempfiles.append(temp_file)
            return True
        except:
            time.sleep(np.random.uniform(0.01, 0.5))
            try:
                f = open(temp_file, "x")
                f.close()
                self.tempfiles.append(temp_file)
                return True
            except FileExistsError:
                return False
            except:
                logger.error("Unexpected error:", sys.exc_info()[0])
                raise RuntimeError("Unexpected error")

    def delete_all_tempfiles(self) -> None:
        """Delete all temporary files"""
        all_tempfiles = list(self.tempfiles)
        for tempfile in all_tempfiles:
            self.delete_tempfile(tempfile)

    def delete_tempfile(self, tempfile) -> None:
        if os.path.exists(tempfile):
            logger.info(f"Deleting tempfile: {tempfile}")
            os.remove(tempfile)
        else:
            logger.info(f"{tempfile} was already deleted or does not exist...")
        if tempfile in self.tempfiles:
            self.tempfiles.remove(tempfile)
        else:
            logger.warning(f"{tempfile} not in self.tempfiles")

    def cleanup(self):
        logger.info("Cleaning up!")
        self.delete_all_tempfiles()
        self.close_all_loggers()
