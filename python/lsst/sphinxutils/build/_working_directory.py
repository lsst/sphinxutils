import os
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def working_directory(path: str | os.PathLike) -> Iterator[None]:
    """Context manager to temporarily change the working directory."""
    prev_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(prev_cwd)
