# execute the AST from the parser
from lark import Tree, Token

class Executor:
    def execute(self, tree):

        if isinstance(tree, Token):
            return tree.value
        
        if isinstance(tree, Tree):
            if tree.data == "load_expr":
                file_name = tree.children[0]
                table_name = tree.children[1]
                if not isinstance(file_name, Token) or file_name.type != "STRING":
                    raise ValueError("Invalid file format")
                if not isinstance(table_name, Token) or table_name.type != "TABLE_NAME":
                    raise ValueError("Invalid table name")
                return f"LOAD {file_name} AS {table_name}"
            
            elif tree.data == "select_expr":
                columns = self.execute(tree.children[0])
                if not columns:
                    raise ValueError("No columns selected")
                from_clause = self.execute(tree.children[1])
                return f"SELECT {columns} FROM {from_clause}"

            elif tree.data == "columns":
                columns_list = [] 
                for child in tree.children:
                    # a token can be * or a single column
                    if isinstance(child, Token) and child.value == "*": 
                        return "*"
                    elif isinstance(child, Tree) and child.data == "column":
                        # recursive call to handle multiple columns
                        columns_list.append(self.execute(child))
                
                if not columns_list:
                    raise ValueError("No valid columns found")
                return ", ".join(columns_list)

                
            elif tree.data == "column":
                child = tree.children[0]
                # check if the child is a token (column name) or a tree (an aggregate expression)
                if isinstance(child, Token) and child.type == "COL_NAME":
                    return child.value
                elif isinstance(child, Tree) and child.data == "agg_expr":
                    return self.execute(child)
                else:
                    raise ValueError("Invalid column name")

               
            elif tree.data == "agg_expr":
                agg_child = tree.children[0]
                param = tree.children[1]
                if isinstance(agg_child, Tree):
                    agg_func = agg_child.data.upper()
                if not agg_func:
                    raise ValueError("Invalid aggregate function")
                
                if isinstance(param, Tree) and param.data == "agg_param":
                    param_child = param.children[0]
                    if isinstance(param_child, Token) and param_child.type == "STAR":
                        param = "*"
                    elif isinstance(param_child, Token) and param_child.type == "COL_NAME":
                        param = param_child.value
                    else:
                        raise ValueError("Invalid aggregate parameter")
                return f"{agg_func}({param})"
                
                
            elif tree.data == "from_clause":
                source = tree.children[0]
                clauses = []
                for clause in tree.children[1:]:
                    clauses.append(self.execute(clause))
                
                if not source:
                    raise ValueError("No source table found")
                return f"{source} {' '.join(clauses)}"
            
            elif tree.data == "filter_clause":
                condition = self.execute(tree.children[0])
                return f"FILTER({condition})"
            
            elif tree.data == "conditions":
                conditions = []
                for child in tree.children:
                    if isinstance(child, Tree) and child.data == "condition":
                        conditions.append(self.execute(child))
                    elif isinstance(child, Token) and child.type == "LOP":
                        conditions.append(child.value)
                return " ".join(conditions)

            elif tree.data == "condition":
                col = tree.children[0]
                op = tree.children[1]
                val = tree.children[2]
                if isinstance(col, Token):
                    col = col.value
                if isinstance(op, Token):
                    op = op.value
                if isinstance(val, Token):
                    val = val.value
                return f"{col} {op} {val}"
            
            elif tree.data == "groupby_clause":
                columns = ", ".join(self.execute(c) for c in tree.children[0].children)
                if not columns:
                    raise ValueError("No valid group by columns found")
                return f"GROUP BY({columns})"
            
            elif tree.data == "orderby_clause":
                columns = ", ".join(self.execute(c) for c in tree.children[0].children)
                if not columns:
                    raise ValueError("No valid order by columns found")
                return f"ORDER BY({columns})" 
            
            elif tree.data == "order_column":
                child1 = tree.children[0]
                # assuming the order is always ascending if not specified
                order = "ASC" 
                if isinstance(child1, Token) and child1.type == "COL_NAME":
                    column = child1.value

                # if there is an order specified
                if len(tree.children) == 2:
                    child2 = tree.children[1]
                    if isinstance(child2, Token) and child2.type == "ORDER":
                        order = child2.value.upper()
                else:
                    order = "ASC"
                return f"{column} {order}"
            
            elif tree.data == "COL_NAME" or tree.data == "TABLE_NAME":
                return str(tree.children[0])
            
            elif tree.data == "STRING":
                return str(tree.children[0])[1:-1]
            
            elif tree.data == "NUMBER":
                return str(tree.children[0])
            
            else:
                return f"UNKNOWN({tree.data})"
