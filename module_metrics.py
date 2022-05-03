

def get_LOC_of_file(file_path):
    return sum([1 for _ in open(file_path)])
