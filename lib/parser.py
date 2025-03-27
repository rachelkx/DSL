# a DSL parser that parses the DSL and generates the AST
# used for data visualization and preparation

import lark

# define the grammar for the DSL
GRAMMAR = """
?start : expr

?expr : load_expr
      | query_expr

load_expr : "LOAD"i STRING "AS"i TABLE_NAME ";"? -> load

query_expr : "SELECT"i select_columns "FROM"i from_expr ";"?

select_columns : select_column ("," select_column)*
select_column : COL_NAME | "*" | agg_expr

?from_expr : TABLE_NAME (filter_expr | groupby_expr | orderby_expr)*

filter_expr : "FILTER"i "(" conditions ")" -> filter_expr

groupby_expr : "GROUP BY"i group_columns -> groupby_expr
group_columns : "(" COL_NAME ("," COL_NAME)* ")"

orderby_expr : "ORDER BY"i order_columns -> orderby_expr
order_columns : "(" order_column ("," order_column)* ")"
order_column : COL_NAME ORDER?
ORDER : "ASC"i | "DESC"i

agg_expr : agg_func "(" (COL_NAME | "*") ")" agg_filter_clause?
agg_filter_clause : "FILTER"i "(" conditions ")"
agg_func : "COUNT"i | "SUM"i | "AVG"i | "MIN"i | "MAX"i

?conditions : condition (LOP condition)*
?condition : COL_NAME OP value 
           | "NOT"i condition
           | "(" conditions ")"
OP : "=" | "<" | ">" | "<=" | ">=" | "!="
LOP : "AND"i | "OR"i 
?value : NUMBER | STRING

STRING : /'[^']*'/ | /"[^"]*"/
COL_NAME : CNAME
TABLE_NAME : CNAME

%import common.CNAME
%import common.NUMBER
%import common.WS
%ignore WS
"""



class Parser:
    def __init__(self):
        self.parser = lark.Lark(GRAMMAR, parser="lalr")

    def parse(self, dsl):
        return self.parser.parse(dsl)
"""
# move this to lib/interpreter.py
# define the interpreter for the AST
    def execute(self, tree):
        if tree.data == "load":
            return f"Loading {tree.children[0]} as {tree.children[1]}"
        elif tree.data == "select":
            columns = tree.children[:-1]
            source = self.execute(tree.children[-1])
            return f"SELECT {', '.join(columns)} FROM ({source})"
        elif tree.data == "filter":
            source = self.execute(tree.children[0])
            condition = tree.children[1]
            return f"FILTER({condition})"
        elif tree.data == "groupby":
            source = self.execute(tree.children[0])
            columns = ", ".join(tree.children[1:])
            return f"GROUP_BY({columns})"
        elif tree.data == "orderby":
            source = self.execute(tree.children[0])
            columns = ", ".join(tree.children[1:])
            return f"ORDER_BY({columns})"
        return "UNKNOWN"
"""

# test parser
if __name__ == "__main__":
    try:
        parser = Parser()
        print("Grammar loaded successfully!") 
    except Exception as e:
        print(f"Grammar error: {e}")  
