import os

class ForensicAnalyzer:
    def list_files(self, directory):
        files = []
        for root, dirs, file_names in os.walk(directory):
            for file_name in file_names:
                file_path = os.path.join(root, file_name)
                file_info = {
                    'name': file_name,
                    'size': os.path.getsize(file_path),
                    'type': os.path.splitext(file_name)[1]
                }
                files.append(file_info)
        return files
