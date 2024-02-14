import os
import sys
import numpy as np
import time
import logging
from typing import List, Dict

logger = logging.getLogger("MultiProcessTools")
logger.setLevel(logging.DEBUG)


def create_log_StreamHandler(logger: logging.Logger, handler_name: str) -> None:
    logger.setLevel(logging.DEBUG)
    ## create a file handler ##
    stream_handler = logging.StreamHandler()
    ## create a logging format ##
    formatter = logging.Formatter(
        "%(asctime)s:%(filename)s:%(funcName)s:%(name)s:%(levelname)s:%(message)s"
    )
    stream_handler.set_name(handler_name)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    handler_names = [handler.get_name() for handler in logger.handlers]
    if handler_name not in handler_names:
        logger.warning(f"{handler_name} already exists in logger {logger.name}")
        logger.removeHandler(handler_name)
    logger.addHandler(stream_handler)


def create_log_FileHandler(logger: logging.Logger, handler_name: str, log_file: str) -> None:
    logger.setLevel(logging.DEBUG)
    ## create a file handler ##
    file_handler = logging.FileHandler(log_file)
    ## create a logging format ##
    formatter = logging.Formatter(
        "%(asctime)s:%(filename)s:%(funcName)s:%(name)s:%(levelname)s:%(message)s"
    )
    file_handler.set_name(handler_name)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    handler_names = [handler.get_name() for handler in logger.handlers]
    if handler_name in handler_names:
        logger.warning(
            f"{handler_name} already exists in logger {logger.name}, replacing..."
        )
        logger.removeHandler(handler_name)
    logger.addHandler(file_handler)




class MultiProcessHelper:
    
    PROCESS_FILE_EXTENTIONS = [
        ".tmp", ".err", ".fin"
    ]
    LOG_FILE_EXTENTIONS = [
        ".log"
    ]
    INSTANCE_FILE_EXTENTIONS = [
        ".running", ".failed", ".finished"
    ]
    STATUS_STATES = ["running", "failed", "finished"]
    
    def __init__(
        self,
        name: str,
        output_root: str,
        logger_names: List[str],
    ):
        time.sleep(np.random.random())
        # Initialize variables, type checks, and create output directories
        self.name = name
        self.processes = {}
        self.directories = {}
        self.files: Dict[str, list] = {}
        self.loggers: Dict[str, logging.Logger] = {}
        self.logger = logging.getLogger("MultiProcessTools")
        try:
            working_directory = os.path.join(os.path.abspath(output_root), "multiprocesstools")
            os.makedirs(working_directory, exist_ok=True)
            self.directories["working_directory"] = working_directory
        except:
            raise ValueError(f"{working_directory} is not a valid path")
        self._initialize_instance()
        self._initialize_loggers(logger_names=logger_names)
        self.logger.info(f"Instance number: {self.instance_number}")
        for directory in self.directories.keys():
            self.logger.info(f"{directory}: {self.directories[directory]}")
                
    @property
    def status(self) -> Dict[str, List[str]]:
        pass
    
    def _initialize_instance(self) -> None:
        """Initialize the instance_number number"""
        self.create_directory("instances")
        instance_number = 0
        valid_instance = False
        while valid_instance == False:
            instance_number += 1
            valid_instance = self.create_file(
                file_name=f"{self.name}_{instance_number}",
                dir="instances",
                extentions=self.INSTANCE_FILE_EXTENTIONS,
            )
        self.instance_number = instance_number

    def _initialize_loggers(
        self,
        logger_names: List[str],
    ) -> None:
        """Initialize the object loggers"""
        self.create_directory("logs")
        log_path = self.get_directory("logs")
        success = self.create_file(
            file_name=log_file,
            dir="logs",
            extentions=self.LOG_FILE_EXTENTIONS,
        )
        if not success:
            raise ValueError(f"Log file {log_file} already exists")

        log_file = os.path.join(log_path, f"{self.name}_{self.instance_number}")

        create_log_FileHandler(self.logger, f"file_handler{self.instance_number}", log_file)
        create_log_StreamHandler(self.logger, f"stream_handler{self.instance_number}")
        self.logger.info(f"Created log file: {log_file}")

        for logger_name in logger_names:
            logger = logging.getLogger(logger_name)
            create_log_FileHandler(logger, f"file_handler{self.instance_number}", log_file)
            create_log_StreamHandler(logger, f"stream_handler{self.instance_number}")
            self.loggers[logger_name] = logger
            logger.info(f"Created log file: {log_file}")

    def create_directory(self, dir_name):
        path = os.path.join(self.directories["working_directory"], dir_name)
        if os.path.exists(path):
            self.logger.info(f"Path already exists:\n\n{path} ")
            if dir_name not in self.directories:
                self.directories[dir_name] = path
            if dir_name not in self.files:
                self.files[dir_name] = []
            elif dir_name in self.directories:
                if self.directories[dir_name] != path:
                    raise ValueError(
                        f"Directory {dir_name} already exists, but the path is different: {self.directories[dir_name]} != {path}"
                    )
        else:
            self.logger.info(f"Creating path:\n\n{path}")
            assert dir_name not in self.directories.keys()
            os.makedirs(path, exist_ok=True)
            self.directories[dir_name] = path

    def get_directory(self, dir_name):
        if any(dir_name in i for i in self.directories.items()):
            if dir_name in self.directories.keys():
                return self.directories[dir_name]
            else:
                return dir_name
        else:
            raise ValueError(f"{dir_name} is not in self.directories")

    def create_file(
        self, file_name: str, dir: str, extentions: List[str]
    ) -> bool:
        """
        Creates a temporary file with the given name.
        returns true if the file was created successfully, false if the file exists.
        """
        path = self.get_directory(dir)
        for extention in extentions:
            if os.path.exists(os.path.join(path, file_name + extention)):
                return False
        file = os.path.join(path, file_name + extentions[0])
        try:
            f = open(file, "x")
            f.close()
            self.files[dir].append(file)
            logger.info(f"Created file: {file}")
            return True
        except FileExistsError:
            logger.warning(f"File {file} already exists")
            return False
        except:
            time.sleep(np.random.uniform(0.01, 0.5))
            try:
                f = open(file, "x")
                f.close()
                self.files[dir].append(file)
                logger.info(f"Created file: {file}")
                return True
            except FileExistsError:
                logger.warning(f"File {file} already exists")
                return False
            except Exception as e:
                self.logger.error("Unexpected error:", e.with_traceback())
                raise e.with_traceback()
            
    def update_file(self, file_name, dir, new_suffix) -> None:
        try:
            idx = self.files[dir].index(file_name)
        except KeyError as e:
            logger.error(f"{dir} not in self.files")
            logger.error(e.with_traceback())
            raise ValueError(f"{dir} not in self.files\n\n{e.with_traceback()}")
        except ValueError as e:
            logger.error(f"{file_name} not in {dir}")
            logger.error(e.with_traceback())
            raise ValueError(f"{file_name} not in {dir}\n\n{e.with_traceback()}")
        file = os.path.join(self.get_directory(dir), file_name)
        current_suffix = self.files[dir][idx].split(".")[-1]
        assert file.endswith(f".{current_suffix}")
        if os.path.exists(file):
            self.logger.info(f"Updating file: {file}")
            new_file = file.replace(f".{current_suffix}", f".{new_suffix}")
            os.rename(file, new_file)
            new_filename = self.files[dir][idx].replace(f".{current_suffix}", f".{new_suffix}")
            self.files[dir][idx] = new_filename
        else:
            self.logger.error(f"{file} does not exist...")

    def delete_file(self, file_name, dir) -> None:
        path = self.get_directory(dir)
        try:
            idx = self.files[dir].index(file_name)
            file_name = self.files[dir].pop(idx)
            file = os.path.join(path, file_name)
        except ValueError as e:
            self.logger.error(f"{file_name} not in {dir}")
            self.logger.error(e.with_traceback())
            raise ValueError(f"{file_name} not in {dir}\n\n{e.with_traceback()}")
        if os.path.exists(file):
            self.logger.info(f"Deleting file: {file}")
            os.remove(file)
        else:
            self.logger.info(f"{file} was already deleted or does not exist...")
            

    def track_process(self, process_name: str) -> bool:
        if process_name in self.processes.keys():
            raise ValueError(f"{process_name} already in self.processes")
        process_idx = len(self.processes)
        process_dir = f"p{process_idx}_{process_name}"
        self.create_directory(process_dir)
        self.processes[process_name] = {
            "status": self.STATUS_STATES[0],
            "dir": process_dir,
        }
        return True

    def update_process_status(self, process_name: str, status: str) -> None:
        if process_name not in self.processes.keys():
            raise ValueError(f"{process_name} not in self.processes")
        if status not in self.STATUS_STATES:
            raise ValueError(f"{status} is not a valid status")
        if self.processes[process_name]["status"] == status:
            self.logger.info(f"{process_name} is already {status}")
            return
        self.processes[process_name]["status"] = status
        self.logger.info(f"Updated status of {process_name} to {status}")            
        
    def create_process_file(self, process_name: str, file_name: str) -> bool:
        try:
            process_dir = self.processes[process_name]["dir"]
        except KeyError as e:
            self.logger.error(f"{process_name} not in self.processes")
            self.logger.error(e.with_traceback())
            raise ValueError(f"{process_name} not in self.processes\n\n{e.with_traceback()}")
        success = self.create_file(
            file_name=file_name,
            dir=process_dir,
            extentions=self.PROCESS_FILE_EXTENTIONS,
        )
        if not success:
            return False
        return True
    
    def update_process_file(self, process_name: str, file_name: str, status: str) -> None:
        try:
            process_dir = self.processes[process_name]["dir"]
        except KeyError as e:
            self.logger.error(f"{process_name} not in self.processes")
            self.logger.error(e.with_traceback())
            raise ValueError(f"{process_name} not in self.processes\n\n{e.with_traceback()}")
        try:
            status_idx = self.STATUS_STATES.index(status)
        except ValueError as e:
            self.logger.error(f"{status} not in self.STATUS_STATES")
            self.logger.error(e.with_traceback())
            raise ValueError(f"{status} not in self.STATUS_STATES\n\n{e.with_traceback()}")

        self.update_file(
            file_name=file_name,
            dir=process_dir,
            new_suffix=self.PROCESS_FILE_EXTENTIONS[status_idx],
        )
        

    def delete_all_files_with_extention(self, extention) -> None:
        """Delete all files with a certain extention"""
        for directory in self.files:
            for file in self.files[directory]:
                if file.endswith(extention):
                    self.delete_file(file, directory)
    
    def close_all_loggers(self) -> None:
        for logger_name in self.loggers.keys():
            logger = self.loggers.pop(logger_name)
            logger.info("Closing all handlers...")
            for handler in logger.handlers:
                logger.info(f"Closing handler: {handler.get_name()}")
                handler.close()
                logger.removeHandler(handler)
            logger.info("All handlers closed")
    
    def cleanup(self):
        self.logger.info("Cleaning up!")
        self.delete_all_files_with_extention(".tmp")
        self.delete_all_files_with_extention(".running")
        self.close_all_loggers()
