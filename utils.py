from config import *


def file_path(file_name):
    return CODE_ROOT_FOLDER + file_name


def module_name_from_file_path(full_path):
    # e.g. ../zeeguu_core/model/user.py -> zeeguu_core.model.user

    file_name = full_path[len(CODE_ROOT_FOLDER):]
    file_name = file_name.replace("\\__init__.py", "")
    file_name = file_name.replace("/", ".")
    file_name = file_name.replace("\\", ".")
    file_name = file_name.replace(".py", "")
    return file_name

# assert (file_path("core/model/user.py") == "/content/Zeeguu-Core/zeeguu_core/model/user.py")
# assert 'zeeguu_core.model.user' == module_name_from_file_path(file_path('zeeguu_core/model/user.py'))
