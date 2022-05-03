from config import *
from pathlib import Path
from utils import module_name_from_file_path


def LOC(file_path):
    return sum([1 for _ in open(file_path)])


def module_LOC(module_name):
    size = 0
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")

    for file in files:
        file_path = str(file)
        full_module_name = module_name_from_file_path(file_path)
        if full_module_name.startswith(module_name + '.'):
            size += LOC(file_path)

    return size