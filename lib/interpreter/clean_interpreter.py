from lark import Token

class CleanInterpreter:
    def __init__(self, tables):
        self.tables = tables

    def execute(self, tree):
        if tree.data == "fillna_cmd":
            return self.execute_fillna(tree)
        elif tree.data == "dropna_cmd":
            return self.execute_dropna(tree)
        elif tree.data == "filter_outliers_cmd":
            return self.execute_filter_outliers(tree)
        elif tree.data == "normalize_cmd":
            return self.execute_normalize(tree)
        else:
            raise ValueError(f"Unknown clean commands: {tree.data}")

    def execute_fillna(self, tree):
        table_name = tree.children[0].value 
        col = tree.children[1].value
        method = tree.children[2]

        df = self.tables[table_name]
        if isinstance(method, Token):
            method = method.value.upper()

            if method == "MEAN":
                value = df[col].mean()
            elif method == "MEDIAN":
                value = df[col].median()
            elif method == "MODE":
                # may be multiple modes, take the first one
                value = df[col].mode().iloc[0] 
            else:
                # fillna with a constant value if specified
                value = float(method) 

            df[col] = df[col].fillna(value)


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

    def execute_normalize(self, tree):
        table_name = tree.children[0].value
        col = tree.children[1].value
        df = self.tables[table_name]

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