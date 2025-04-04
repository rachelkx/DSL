import pandas as pd
from lark import Tree, Token

class SelectInterpreter:
    def __init__(self, tables):
        self.tables = tables

    def execute(self, tree):
        columns = self.execute_columns(tree.children[0])
        from_clause = tree.children[1]
        table_name = from_clause.children[0].value

        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found. Load it first!")
        
        df = self.tables[table_name]

        # execute from_clause
        for clause in from_clause.children[1:]:
            if clause.data == "filter_clause":
                df = self.execute_filter(clause, df)
            elif clause.data == "groupby_clause":
                df = self.execute_groupby(clause, df)
            elif clause.data == "orderby_clause":
                df = self.execute_orderby(clause, df)

        # apply aggregate functions and perform final column selection
        if columns == "*":
            result_df = df
        else:
            result_df = self.apply_column_selected(columns, df)

        return result_df

    def execute_columns(self, tree):
        columns_list = []
        for child in tree.children:
            if isinstance(child, Token) and child.type == "STAR":
                return "*"
            elif isinstance(child, Tree) and child.data == "select_column":
                # return a list of columns if multiple columns are selected
                columns_list.append(self.execute_column(child))  
            elif isinstance(child, Tree) and child.data == "agg_expr":
                # return a list of column that need to be aggregated
                columns_list.append(child)
        return columns_list


    def execute_column(self, tree):
        child = tree.children[0]
        if isinstance(child, Token) and child.type == "COL_NAME":
            return child.value
        elif isinstance(child, Tree) and child.data == "agg_expr":
            return child
        raise ValueError("Invalid column name")


    def execute_agg_expr(self, tree):
        agg_child = tree.children[0]
        param = tree.children[1]

        if isinstance(agg_child, Tree):
            agg_func = agg_child.data.upper() 
        else:
            raise ValueError("Invalid aggregate function")

        if isinstance(param, Tree) and param.data == "agg_param":
            param_child = param.children[0]
            if isinstance(param_child, Token):
                if param_child.type == "STAR":
                    param = "*"
                elif param_child.type == "COL_NAME":
                    param = param_child.value
                else:
                    raise ValueError("Invalid aggregate parameter")
        else:
            raise ValueError("Invalid aggregate parameter format")
        # return a tuple of aggregation function and parameter for later use
        return (agg_func, param)


    def execute_filter(self, tree, df):
        cond = self.execute_condition(tree.children[0])
        try:
            filtered_df = df.query(cond)
        except TypeError as e:
            raise TypeError(f"Invalid filter condition: {e}") from None

        return filtered_df


    def execute_condition(self, tree):
        if tree.data == "simple_condition":
            col = tree.children[0].value
            op = tree.children[1].value
            val = tree.children[2].value

            try:
                float(val)
                is_val_numeric = True
            except ValueError:
                is_val_numeric = False

            if not is_val_numeric and not val.startswith(("'", '"')):
                val = f"'{val}'"

            return f"{col} {op} {val}"


        elif tree.data == "logical_condition":
            left = self.execute_condition(tree.children[0])
            lop_token = tree.children[1]
            right = self.execute_condition(tree.children[2])
            op = lop_token.value.upper()
            if op == "AND":
                return f"({left}) & ({right})"
            elif op == "OR":
                return f"({left}) | ({right})"
            else:
                raise ValueError(f"Unknown logical operator: {lop_token}")

        elif tree.data == "not":
            inner = self.execute_condition(tree.children[0])
            return f"~({inner})"

        elif tree.data == "condition":
            # condition wrapped by parentheis
            return self.execute_condition(tree.children[0])

        raise ValueError("Invalid condition format")


    def execute_groupby(self, tree, df):
        # extract the list of COL_NAME tokens from the 'columns' subtree
        columns_node = tree.children[0]  # This is the Tree('columns', [...])
        group_cols = []

        for child in columns_node.children:
            if isinstance(child, Token) and child.type == "COL_NAME":
                group_cols.append(child.value)

        # save the column names for later use in aggregation
        self._groupby_columns = group_cols

        # do not perform aggregation here, as it will be handled in apply_column_selected
        return df



    def execute_orderby(self, tree, df):
        columns = []
        ascending_list = []

        for child in tree.children[0].children:
            column_name = child.children[0].value
            # set default order to ascending
            order = "ASC"  
            if len(child.children) == 2:
                order = child.children[1].value.upper()
            ascending_list.append(order == "ASC")
            columns.append(column_name)

        sorted_df = df.sort_values(columns, ascending=ascending_list)
        return sorted_df


              
    def apply_column_selected(self, columns, df):
        normal_cols = []
        agg_exprs = []

        for col in columns:
            if isinstance(col, Tree) and col.data == "agg_expr":
                agg_exprs.append(col)
            elif isinstance(col, str):
                normal_cols.append(col)

        if hasattr(self, "_groupby_columns") and self._groupby_columns:
            group_cols = self._groupby_columns

            # check if the normal_cols are in the groupby columns
            for col in normal_cols:
                if col not in group_cols:
                    raise ValueError(f"Column '{col}' must appear in GROUP BY clause or be used in an aggregate function.")

        if agg_exprs:
            # handle groupby
            if hasattr(self, "_groupby_columns") and self._groupby_columns:
                agg_dict = {}
                for expr in agg_exprs:
                    func, param = self.execute_agg_expr(expr)
                    if func == "COUNT" and param == "*":
                        result_df = df.groupby(group_cols).size().reset_index(name="count")
                        return result_df
                    else:
                        col_name = f"{func.lower()}_{param}"
                        agg_dict[col_name] = (param, func.lower())

                result_df = df.groupby(group_cols).agg(**agg_dict).reset_index()
                return result_df

            else:
                # handle other aggregate functions
                agg_results = {}
                for expr in agg_exprs:
                    func, param = self.execute_agg_expr(expr)
                    if func == "COUNT" and param == "*":
                        agg_results["count"] = df.shape[0]
                    else:
                        col_name = f"{func.lower()}_{param}"
                        agg_results[col_name] = getattr(df[param], func.lower())()
                return pd.DataFrame([agg_results])

        # if no aggregation is needed, just return the selected columns
        return df[normal_cols]
