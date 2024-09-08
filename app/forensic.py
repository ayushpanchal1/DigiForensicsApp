import os

class ForensicAnalyzer:
    def list_files(self, directory):
        files = []
        for entry in os.scandir(directory):
            if entry.is_file():
                file_info = {
                    'name': entry.name,
                    'size': entry.stat().st_size,
                    'type': os.path.splitext(entry.name)[1]
                }
                files.append(file_info)
            elif entry.is_dir():
                # Recursively list files in subdirectories
                files.extend(self.list_files(entry.path))
        return files
