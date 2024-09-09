import yara
import os
import hashlib
from pathlib import Path
import datetime
import tensorflow as tf

class ForensicAnalyzer:
    def __init__(self):
        # Directory where YARA rules are located
        self.rules_directory = os.path.join(os.getcwd(), 'rules')
        print(f"YARA rules directory: {self.rules_directory}")  # Debugging line
        self.yara_rules = self.compile_yara_rules(self.rules_directory)
        self.model = self.load_model()
        self.class_labels = ['benign', 'malicious']  # Modify if your labels differ

    def load_model(self):
        try:
            # Path to your saved model
            model_path = './model/model.keras'
            return tf.keras.models.load_model(model_path)
        except Exception as e:
            print(f"Error loading CNN model: {e}")
            return None
        
    def compile_yara_rules(self, rule_dir):
        rule_files = {}
        for rule_file in os.listdir(rule_dir):
            if rule_file.endswith('.yar'):
                rule_path = os.path.join(rule_dir, rule_file)
                rule_id = os.path.splitext(rule_file)[0]  # Use filename as the rule identifier
                rule_files[rule_id] = rule_path

        try:
            compiled_rules = yara.compile(filepaths=rule_files)
            return compiled_rules
        except yara.SyntaxError as e:
            print(f"Syntax error in one of the rule files: {e}")
            return None
        except Exception as e:
            print(f"Error compiling YARA rules: {e}")
            return None

    def calculate_sha256(self, file_path):
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating SHA-256 for {file_path}: {e}")
            return None

    def list_files(self, directory):
        files = []
        for entry in Path(directory).rglob('*'):
            if entry.is_file():
                try:
                    file_info = {
                        'path': str(entry),
                        'modified_time': datetime.datetime.fromtimestamp(entry.stat().st_mtime).isoformat(),
                        'created_time': datetime.datetime.fromtimestamp(entry.stat().st_ctime).isoformat(),
                        'access_time': datetime.datetime.fromtimestamp(entry.stat().st_atime).isoformat(),
                        'size': entry.stat().st_size,
                        'sha256': self.calculate_sha256(entry),
                        'is_suspicious': self.is_suspicious(entry)  # Use YARA for suspicious check
                    }
                    files.append(file_info)
                except OSError as e:
                    print(f"Error accessing file {entry}: {e}")
        return files         

    def is_suspicious(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            if self.yara_rules:
                matches = self.yara_rules.match(data=file_content)
                return any(match.rule for match in matches)
            else:
                return False
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
            return False