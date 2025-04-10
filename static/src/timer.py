import time

def timeit(func):
    """
    Decorator to measure the execution time of a function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"executed in {execution_time:.4f} sec")
        return result, execution_time  # Return both the result and the execution time
    return wrapper