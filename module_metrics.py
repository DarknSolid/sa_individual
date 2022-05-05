from pydriller import Repository, ModificationType
from config import CODE_ROOT_FOLDER
from datetime import datetime
from typing import Dict
import json


def get_LOC_of_file(file_path):
    return sum([1 for _ in open(file_path)])


class FileGitHubMetrics:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.total_commits = 0
        self.code_churn = 0

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def fetch_vsc_info(since: datetime) -> Dict[str, FileGitHubMetrics]:
    """
    fetches relevant source control info from GitHub
    :param since: earliest commit data to get from
    :return: a dictionary with file path as key and GitHub info as value
    """
    cache_path = "github_metrics.json"
    try:
        with open(cache_path) as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError as e:
        print(f"No github metrics cache found, fetching all commits GitHub...")

    repo = Repository(CODE_ROOT_FOLDER, since=since)
    commits = list(repo.traverse_commits())
    file_path_to_vsc_info = dict()

    for commit in commits:
        for modification in commit.modified_files:

            new_path = modification.new_path
            old_path = modification.old_path

            if modification.change_type == ModificationType.RENAME:
                obj_new = FileGitHubMetrics(new_path)
                obj_old = file_path_to_vsc_info.get(old_path)
                obj_new.total_commits = obj_old.total_commits + 1
                obj_new.code_churn = obj_old.code_churn + modification.added_lines + modification.deleted_lines

                file_path_to_vsc_info[new_path] = obj_new

                try:
                    file_path_to_vsc_info.pop(old_path)
                except Exception as e:
                    # not sure why sometimes there's a rename w/o
                    # an old_path existing?
                    # print(f"could not pop {old_path}")
                    # print(f"new path: {new_path}")
                    # print(f"commit: {commit.hash} {commit.msg}")
                    pass

            elif modification.change_type == ModificationType.DELETE:
                if old_path in file_path_to_vsc_info:
                    file_path_to_vsc_info.pop(old_path)

            elif modification.change_type == ModificationType.ADD:
                new_obj = FileGitHubMetrics(new_path)
                new_obj.code_churn = modification.added_lines
                new_obj.total_commits = 1
                file_path_to_vsc_info[new_path] = new_obj

            else:   # modification to existing file
                if old_path not in file_path_to_vsc_info:
                    continue
                obj_old = file_path_to_vsc_info[old_path]
                obj_old.total_commits += 1
                obj_old.code_churn += modification.added_lines + modification.deleted_lines

    # return sorted(file_path_to_vsc_info.items(), key=lambda x: x[1].total_commits)
    with open(cache_path, "w") as outfile:
        json.dump(file_path_to_vsc_info, outfile, default=vars)
    return file_path_to_vsc_info
