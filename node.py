from collections import defaultdict


class Node:
    def __init__(self, file_path: str, module_name: str, imports: defaultdict, lines_of_code: int, code_churn: int, total_commits: int):
        self.file_path = file_path
        self.module_name = module_name
        self.lines_of_code = lines_of_code
        self.imports = imports
        self.code_churn = code_churn
        self.total_commits = total_commits