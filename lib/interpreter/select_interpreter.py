import pandas as pd
from lark import Tree, Token

class SelectInterpreter:
    def __init__(self, table):
        self.table = table

    def execute(self, tree, interpreter):
        columns = self.execute_columns(tree.children[0])
        from_clause = tree.children[1]
        table_name = from_clause.children[0].value

        if table_name not in self.table:
            raise ValueError(f"Table '{table_name}' not found. Load it first!")
        
        df = self.table[table_name]

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
            elif isinstance(child, Tree) and child.data == "column":
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
        child = tree.children[0]
        if child.data == 'condition':
            # deal with single condition
            condition = self.execute_condition(child)
        else:
            # deal with nested conditions
            condition = self.execute_conditions(child)
        filtered_df = df.query(condition)
        return filtered_df


    def execute_condition(self, tree):
        if tree.data == "condition":
            if len(tree.children) == 1 and isinstance(tree.children[0], Tree):
                # deal with condition wrapped in parentheses
                return self.execute_condition(tree.children[0])

            if len(tree.children) == 3:
                if isinstance(tree.children[0], Token):
                    # deal with simple comparison
                    col = tree.children[0].value
                    op = tree.children[1].value
                    val = tree.children[2].value
                    if not val.isdigit() and not val.startswith(("'", '"')):
                        val = f"'{val}'"
                    return f"{col} {op} {val}"
                else:
                    # deal with nested condition, like condition1 AND condition2
                    return f"({self.execute_conditions(tree)})"

        elif tree.data == "not":
            # deal with NOT expression
            not_cond = self.execute_condition(tree.children[0])
            return f"~({not_cond})"

        raise ValueError("Invalid condition format")


    
    def execute_conditions(self, tree):
        conditions = []
        for child in tree.children:
            if isinstance(child, Tree): 
                conditions.append(self.execute_condition(child))

            elif isinstance(child, Token) and child.type == "LOP":
                # change logical operator to Python's bitwise operator
                op = child.value.upper()
                if op == "AND":
                    conditions.append("&")
                elif op == "OR":
                    conditions.append("|")
                else:
                    raise ValueError(f"Invalid logical operator: {child.value}")

        return " ".join(conditions)



    def execute_groupby(self, tree, df):
        columns = self.execute_columns(tree.children[0])
        # save groupby columns for later use
        self._groupby_columns = columns
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
