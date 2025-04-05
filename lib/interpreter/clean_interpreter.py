from lark import Token, Tree
import pandas as pd

class CleanInterpreter:
    def __init__(self, tables):
        self.tables = tables

    def execute(self, tree):
        cmd = tree.children[0]
        if cmd.data == "fillna_cmd":
            return self.execute_fillna(cmd)
        elif cmd.data == "dropna_cmd":
            return self.execute_dropna(cmd)
        elif cmd.data == "filter_outliers_cmd":
            return self.execute_filter_outliers(cmd)
        elif cmd.data == "normalize_cmd":
            return self.execute_normalize(cmd)
        elif cmd.data == "remove_str_in_numeric_cmd":
            return self.execute_clean_remove_str_in_numeric(cmd)
        elif cmd.data == "remove_num_in_nonnumeric_cmd":
            return self.execute_clean_remove_num_in_nonnumeric(cmd)
        elif cmd.data == "drop_row_col_cmd":
            return self.execute_drop_row_col(cmd)
        elif cmd.data == "replace_cell_cmd":
            return self.execute_replace_cell(cmd)
        else:
            raise ValueError(f"Unknown clean commands: {cmd.data}")

    def execute_fillna(self, tree):
        table_name = tree.children[0].value 
        col = tree.children[1].value
        method = tree.children[2] 

        df = self.tables[table_name]
        if isinstance(method, Tree):
            method_name = method.data
            # only check numeric dtype if it's a statistical method
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise TypeError(f"Column '{col}' contains non-numeric values, cannot compute {method_name}.")

            if method_name == "mean":
                fill_value = df[col].mean()
            elif method_name == "median":
                fill_value = df[col].median()
            elif method_name == "mode":
                fill_value = df[col].mode().iloc[0]
            else:
                raise ValueError(f"Unsupported fill method tree: {method_name}")


        elif isinstance(method, Token):
            if method.type == "NUMBER":
                fill_value = float(method.value)
            elif method.type == "STRING":
                fill_value = str(method.value.strip("'\""))
            else:
                raise ValueError(f"Unsupported token type in fill method: {method.type}")
        else:
            raise ValueError("Invalid fill method format")

        df[col] = df[col].fillna(fill_value)
        return df


    def execute_dropna(self, tree):
        table_name = tree.children[0].value 
        df = self.tables[table_name]

        # set default values
        axis = 0
        how = 'any'
        col_list = None

        # iterate through the children of the tree
        children = tree.children[1:]
        i = 0

        # deal with axis parameter, 0 for rows, 1 for columns
        axis_token = children[i]
        axis = 0 if axis_token.upper() == "ROWS" else 1
        i += 1

        # deal with how parameter, 'any' for any NA, 'all' for all NA
        if i < len(children) and children[i].upper() == "WHERE":
            i += 1
            how_token = children[i].upper()
            if how_token in ("ALL", "ANY"):
                how = how_token
                i += 1

        # deal with columns to drop NA from
        if i < len(children) and children[i].upper() == "IN":
            i += 1
            col_list = []
            while i < len(children) and isinstance(children[i], str):
                col = children[i]
                if col != ",":
                    col_list.append(col)
                i += 1

        # apply above parameters to dropna
        result = df.dropna(
            axis=axis,
            how=how,
            subset=col_list,
            inplace=False
        )
        self.tables[table_name] = result
        return result


    def execute_clean_remove_str_in_numeric(self, tree):
        table_name = tree.children[0].value
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found. Load it first!")

        df = self.tables[table_name]

        if len(tree.children) > 1:
            col_info = tree.children[1]
            if isinstance(col_info, Token):
                cols = [col_info.value]
            else:
                cols = [col.value for col in col_info.children if isinstance(col, Token)]
        else:
            # if no columns specified, apply to all numeric columns
            cols = df.select_dtypes(include='number').columns

        for col in cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        df = df.dropna(subset=cols, how='any')
        self.tables[table_name] = df
        return df


    def execute_clean_remove_num_in_nonnumeric(self, tree):
        table_name = tree.children[0].value
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found. Load it first!")

        df = self.tables[table_name]

        if len(tree.children) > 1:
            col_info = tree.children[1]
            if isinstance(col_info, Token):
                cols = [col_info.value]
            else:
                cols = [col.value for col in col_info.children if isinstance(col, Token)]
        else:
            cols = [col for col in df.columns if not pd.api.types.is_numeric_dtype(df[col])]

        for col in cols:
            df = df[~df[col].apply(lambda x: isinstance(x, (int, float)))]
        self.tables[table_name] = df
        return df


    def execute_drop_row_col(self, tree):
        drop_type_token = tree.children[0] 
        value_token = tree.children[1]  
        # FROM token is at index 2  
        table_name = tree.children[3].value

        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found. Load it first!")

        df = self.tables[table_name]

        if drop_type_token.type == "ROW":
            row_index = int(value_token.value)
            df = df.drop(index=row_index)
        elif drop_type_token.type == "COLUMN":
            col_name = value_token.value
            df = df.drop(columns=col_name)
        else:
            raise ValueError("DROP must specify ROW or COLUMN")

        self.tables[table_name] = df
        return df

        
    def execute_replace_cell(self, tree):
        table_name = tree.children[0].value
        row_index = int(tree.children[2].value) 
        col_name = tree.children[4].value
        val_node = tree.children[5]

        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found. Load it first!")

        df = self.tables[table_name]

        if row_index not in df.index:
            raise IndexError(f"Row index {row_index} does not exist in table '{table_name}'")

        if val_node.type == "NUMBER":
            val = float(val_node.value) if "." in val_node.value else int(val_node.value)
        else:
            val = val_node.value.strip("'")

        df.at[row_index, col_name] = val
        self.tables[table_name] = df
        return df



    def execute_filter_outliers(self, tree):
        table_name = tree.children[0].value 
        col = tree.children[1].value
        df = self.tables[table_name]

        # default outlier detection method
        method = "iqr"
        threshold = 1.5

        # if a method is specified
        if len(tree.children) > 2:
            method_tree = tree.children[2]
            method_token = method_tree.children[0]

            if method_token.type.upper() == "ZSCORE":
                method = "zscore"
                threshold_token = method_tree.children[1]
                threshold = float(threshold_token)
            elif method_token.type.upper() == "IQR":
                method = "iqr"

        if method == "zscore":
            col_mean = df[col].mean()
            col_std = df[col].std()
            z_scores = (df[col] - col_mean) / col_std
            df_filtered = df[z_scores.abs() <= threshold]
            self.tables[table_name] = df_filtered

        elif method == "iqr":
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            df_filtered = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            self.tables[table_name] = df_filtered

        return df_filtered

    def execute_normalize(self, tree):
        table_name = tree.children[0].value
        col = tree.children[1].value
        df = self.tables[table_name]

        # default normalization method
        method = "MINMAX" 

        if len(tree.children) > 3:
            if tree.children[2].upper() == "WITH":
                method = tree.children[3].upper()

        s = df[col]

        if method == "MINMAX":
            min = s.min()
            max = s.max()
            range = max - min

            # If all values are the same, keep them unchanged to avoid zero division error
            if range == 0:
                normed = s
            else:
                normed = (s - min) / range

        elif method == "ZSCORE":
            mean = s.mean()
            std = s.std()

            # If all values are the same, keep them unchanged
            if std == 0:
                normed = s
            else:
                normed = (s - mean) / std

        else:
            raise ValueError(f"Unknown normalization method: {method}")

        df[col] = normed
        self.tables[table_name] = df
        return df