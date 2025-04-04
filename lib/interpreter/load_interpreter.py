import pandas as pd
import os

class LoadInterpreter:
    def __init__(self, table):
        self.table = table

    def execute(self, tree):
        file_name = tree.children[0].value.strip("'\"")
        table_name = tree.children[1].value

        # check if the file exists
        if not os.path.isfile(file_name):
             raise FileNotFoundError(f"File {file_name} not found")
        
        # only allow loading from csv or json files
        if file_name.endswith(".csv"):
            self.table[table_name] = pd.read_csv(file_name)
        elif file_name.endswith(".json"):
            self.table[table_name] = pd.read_json(file_name)
        else:
            raise ValueError(f"Unsupported file format: {file_name}. Must be .csv or .json")
        
        return self.table[table_name]
