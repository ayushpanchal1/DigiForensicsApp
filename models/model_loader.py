import os
import pickle

class ModelLoader:
    @staticmethod
    def load_model(model_name):
        model_path = os.path.join('models/trained_models', model_name)
        with open(model_path, 'rb') as file:
            return pickle.load(file)
