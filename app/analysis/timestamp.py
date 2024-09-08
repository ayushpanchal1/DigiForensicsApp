import pytsk3
from datetime import datetime

def get_file_timestamps(file):
    created_time = datetime.utcfromtimestamp(file.info.meta.crtime)
    modified_time = datetime.utcfromtimestamp(file.info.meta.mtime)
    accessed_time = datetime.utcfromtimestamp(file.info.meta.atime)
    return created_time, modified_time, accessed_time

def print_file_timestamps(file):
    created_time, modified_time, accessed_time = get_file_timestamps(file)
    return {'created': created_time, 'modified': modified_time, 'accessed': accessed_time}
