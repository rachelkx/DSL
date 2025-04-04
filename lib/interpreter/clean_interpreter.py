from lark import Token
import pandas as pd


class CleanInterpreter:
    def __init__(self, tables):
        self.tables = tables

    def _get_table(self, table_name):
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found. Load it first!")
        return self.tables[table_name]

    def execute(self, tree):
        if tree.data == "fillna_cmd":
            return self.execute_fillna(tree)
        elif tree.data == "dropna_cmd":
            return self.execute_dropna(tree)
        elif tree.data == "filter_outliers_cmd":
            return self.execute_filter_outliers(tree)
        elif tree.data == "normalize_cmd":
            return self.execute_normalize(tree)
        elif tree.data == "remove_str_in_numeric_cmd":
            return self.execute_clean_remove_str_in_numeric(tree)
        elif tree.data == "remove_num_in_nonnumeric_cmd":
            return self.execute_clean_remove_num_in_nonnumeric(tree)
        elif tree.data == "drop_row_col_cmd":
            return self.execute_drop_row_col(tree)
        elif tree.data == "replace_cell_cmd":
            return self.execute_replace_cell(tree)
        else:
            raise ValueError(f"Unknown clean commands: {tree.data}")

    def execute_fillna(self, tree):
        table_name = tree.children[0].value 
        col = tree.children[1].value
        method = tree.children[2]

        df = self._get_table(table_name)
        if not isinstance(method, Token):
            raise ValueError("Invalid fill method: must be a token")

        method_type = method.type.upper()
        method_value = method.value

        if method_type == "MEAN":
            fill_value = df[col].mean()
        elif method_type == "MEDIAN":
            fill_value = df[col].median()
        elif method_type == "MODE":
            fill_value = df[col].mode().iloc[0]
        elif method_type == "NUMBER":
            fill_value = float(method_value)
        elif method_type == "STRING":
            fill_value = str(method_value)
        else:
            raise ValueError(f"Unsupported fill method: {method_value}")

        df[col] = df[col].fillna(fill_value)


    def execute_dropna(self, tree):
        table_name = tree.children[0].value 
        df = self._get_table(table_name)

        # set default values
        axis = 0
        how = 'any'
        col_list = None

        # iterate through the children of the tree
        children = tree.children[1:]
        i = 0

        # deal with axis parameter, 0 for rows, 1 for columns
        axis_token = children[i]
        axis = 0 if axis_token.lower() == "rows" else 1
        i += 1

        # deal with how parameter, 'any' for any NA, 'all' for all NA
        if i < len(children) and children[i].lower() == "where":
            i += 1
            how_token = children[i].lower()
            if how_token in ("all", "any"):
                how = how_token
                i += 1

        # deal with columns to drop NA from
        if i < len(children) and children[i].lower() == "in":
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


    def execute_clean_remove_str_in_numeric(self, tree):
        table_name = tree.children[0].value
        df = self._get_table(table_name)
        if len(tree.children) > 1:
            # specified columns
            cols_node = tree.children[1]
            cols = []
            for col in cols_node.children:
                if isinstance(col, Token):
                    cols.append(col.value)

        else:
            # if no columns specified, apply to all numeric columns
            cols = df.select_dtypes(include='number').columns

        for col in cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        self.tables[table_name] = df.dropna(subset=cols, how='any')

    def execute_clean_remove_num_in_nonnumeric(self, tree):
        table_name = tree.children[0].value
        df = self._get_table(table_name)
        if len(tree.children) > 1:
            cols_node = tree.children[1]
            cols = [col.value for col in cols_node.children if isinstance(col, Token)]
        else:
            cols = [col for col in df.columns if not pd.api.types.is_numeric_dtype(df[col])]

        for col in cols:
            df = df[~df[col].apply(lambda x: isinstance(x, (int, float)))]
        self.tables[table_name] = df

    def execute_drop_row_col(self, tree):
        drop_target = tree.children[0]
        table_name = tree.children[-1].value
        df = self._get_table(table_name)

        if drop_target.data == "row":
            row_index = int(drop_target.children[0].value)
            df = df.drop(index=row_index)
        elif drop_target.data == "column":
            col_name = drop_target.children[0].value
            df = df.drop(columns=col_name)
        else:
            raise ValueError("DROP must specify ROW or COLUMN")

        self.tables[table_name] = df

    def execute_replace_cell(self, tree):
        table_name = tree.children[0].value
        row_index = int(tree.children[1].value)
        col_name = tree.children[2].value
        val_node = tree.children[3]

        df = self._get_table(table_name)

        if val_node.type == "NUMBER":
            val = float(val_node.value) if "." in val_node.value else int(val_node.value)
        else:
            val = val_node.value.strip("'")

        df.at[row_index, col_name] = val
        self.tables[table_name] = df


    def execute_filter_outliers(self, tree):
        table_name = tree.children[0].value 
        col = tree.children[1].value
        df = self._get_table(table_name)

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

    def execute_normalize(self, tree):
        table_name = tree.children[0].value
        col = tree.children[1].value
        df = self._get_table(table_name)

        # default normalization method
        method = "MINMAX" 

        if len(tree.children) > 3:
            if tree.children[2].lower() == "with":
                method = tree.children[3].upper()

        s = df[col]

        if method == "MINMAX":
            min_val = s.min()
            max_val = s.max()
            normed = s if max_val - min_val == 0 else (s - min_val) / (max_val - min_val)
        elif method == "ZSCORE":
            mean = s.mean()
            std = s.std()
            normed = s if std == 0 else (s - mean) / std
        else:
            raise ValueError(f"Unknown normalization method: {method}")

        df[col] = normed
        self.tables[table_name] = df