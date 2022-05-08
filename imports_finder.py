import re
from pathlib import Path
from typing import List
from config import CODE_ROOT_FOLDER
from utils import module_name_from_file_path, file_path_from_module_name


def import_from_line(line, files: List[str], cur_file: str):
    # regex patterns used
    #   ^  - beginning of line
    #   \S - anything that is not space
    #   +  - at least one occurrence of previous
    #  ( ) - capture group (read more at: https://pynative.com/python-regex-capturing-groups/)
    try:
        y = re.search("^from (\S+) import ", line)
        if y:
            module = y.group(1)
            module_path = module.replace(".", "\\")
            module_full_path = CODE_ROOT_FOLDER + module_path
            # check if the import is a relative import
            if module.startswith("."):
                if len(module) > 1: # e.g.  "from .api import"
                    module_full_path = module_name_from_file_path(cur_file)
                    module_full_path = module_full_path.split(".")
                    if not cur_file.endswith("__init__.py"):
                        module_full_path = module_full_path[:-1]
                    module_full_path = ".".join(module_full_path)
                    module_full_path = module_full_path + "." + module[1:]
                    module_full_path = file_path_from_module_name(module_full_path)
                else:
                    # e.g. "from . import"
                    module_full_path = module_name_from_file_path(cur_file)
                    module_full_path = module_full_path.split(".")[:-1]
                    module_full_path = ".".join(module_full_path)
                    module_full_path = file_path_from_module_name(module_full_path)

            module = module_name_from_file_path(module_full_path)
            module_script_path = module_full_path + ".py"
            if module_script_path in files:
                return [module]

            # check for all files in current module
            result = set()
            resolved_imports = set()
            module_files = list(Path(module_full_path).glob("*.py"))
            imports = extract_import_entities_from_import_statement(line)
            if len(imports) == 1 and imports[0] == "*":
                result = [module_name_from_file_path(str(f)) for f in list(Path(module_full_path).rglob("*.py"))]
                return result
            if len(module_files) == 0:
                return [module]
            for f in module_files:
                if len(imports) == len(resolved_imports):
                    break
                with open(f, "r") as reader:
                    text = reader.read()
                    for imp in imports:
                        if imp in resolved_imports:
                            continue
                        # check if the file contains a class or definition
                        definition_regex = create_regex_for_def(imp)
                        class_regex = create_regex_for_class(imp)
                        if re.search(definition_regex, text) or re.search(class_regex, text):
                            result.add(module_name_from_file_path(str(f)))
                            resolved_imports.add(imp)


            if len(result) == 0:
                return module
            return list(result)



        y = re.search("^from (\S+)", line)
        if y:
            return [y.group(1)]

        y = re.search("^import (\S+)", line)
        if y:
            return [y.group(1)]
        return []
    except Exception as e:
        return []


def create_regex_for_class(cls: str):
    return f'class ({cls})(\(\S*\):|:)'


def create_regex_for_def(defi: str):
    return f'def ({defi})\('


def extract_import_entities_from_import_statement(string: str):
    # turns "from zeeguu.core.moel import User, x, y into a list [User, x, y]
    line_split = string.split("import")[-1]
    line_split = line_split.replace(",", "")
    line_split = line_split.rstrip()
    try:
        idx = line_split.index("as")
        line_split = line_split[:idx]
    except ValueError:
        ...
    return line_split.strip(" ").split(" ")


# assert(import_from_line("from zeeguu.core import model", ["..\\zeeguu-api\\zeeguu\\core\\model"]) == "hej")


# extracts all the imported modules from a file
# returns a module of the form zeeguu_core.model.bookmark, e.g.
def imports_from_file(file, files: List[str]) -> List[str]:
    all_imports = []

    lines = [line for line in open(file)]

    for line in lines:
        imp = import_from_line(line, files, file)
        all_imports.extend(imp)

    return all_imports
