import time
import logging
from types import FunctionType
import numpy as np
import os

logger = logging.getLogger("MultiProcessTools")
logger.setLevel(logging.DEBUG)


class RunTimeCounter:
    """
    Creates a runtime counter, which has the ability to check if the runtime has exceeded the timeout.
    """

    def __init__(self, timeout: float) -> None:
        self.start_queue = time.perf_counter()
        self.timeout = timeout

    def get_time_left(self) -> float:
        return time.perf_counter() - self.start_queue > self.timeout

    def check_runtime(self) -> None:
        if time.perf_counter() - self.start_queue > self.timeout:
            logger.error(f"Timeout reached. Illumination correction model not found")
            raise RuntimeError(
                f"Timeout exceeded while waiting for illumination correction model to be created"
            )
        else:
            return self.get_time_left()

    def __str__(self) -> str:
        return f"RunTimeCounter created at {self.start_queue} with timeout {self.timeout} and {self.get_time_left()} seconds left"



## We should turn this into a decorator
def run_func_IO_loop(func: FunctionType, func_args: dict, timeout: float):
    """
    Runs a function in a loop until it returns with no IO error.
    """
    busy = True
    timecounter = RunTimeCounter(timeout)
    while busy == True:
        try:
            return_value = func(**func_args)
            busy = False
        except Exception as e:
            logger.error(f"Couldn't run {func.__name__}: " + str(e))
        time.sleep(np.random.uniform(0.01, 0.5))
        timecounter.check_runtime()
    return return_value


def wait_until_file_exists(path: os.PathLike, timeout: int) -> bool:
    """
    waits until the file exists.
    """
    if not os.path.exists(path):
        timecounter = RunTimeCounter(timeout)
        while not os.path.exists(path):
            timecounter.check_runtime()
            logger.info(f"Waiting for {path} to be created...")
            time.sleep(5)
    return True
