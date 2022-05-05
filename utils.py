from config import *
import matplotlib as mpl
import numpy as np


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




def blueToRedFade(mix: float, max: float):
    c1 = '#1f77b4'  # blue
    c2 = 'red'  # green
    return colorFader(c1, c2, mix / max)


def colorFader(c1, c2, mix=0):  # fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1 = np.array(mpl.colors.to_rgb(c1))
    c2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1 - mix) * c1 + mix * c2)
