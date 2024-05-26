""" module for model specific concretisation of abstract interfaces """

import os
import pandas as pd
from tools.converter import Converter
from tools.inference import Inferencer


class ConcreteConverter(Converter):
    def process_file(self, filepath: str, output_filename: str):
        """ implement for specific model """
        df = pd.read_csv(filepath, delimiter=",")
        df.rename(columns={"prediction": "Prediction"}, inplace=True)
        df.to_csv(output_filename, sep="\t", index=False)


class ConcreteInferencer(Inferencer):
    def process_file(self, filepath: str, output_filename: str):
        """ implement for specific model """
        command = f"python -m classif.inference -i {filepath} -o {output_filename}"
        print(command)
        os.system(command)
