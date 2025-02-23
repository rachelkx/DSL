# a DSL parser that parses the DSL and generates the AST
# used for data visualization and preparation

import lark

# define the grammar for the DSL
GRAMMAR = """

?start : command

?command : load_cmd
        | query_cmd

load_cmd : "LOAD"i STRING "AS"i TABLE_NAME ";"? -> load

query_cmd : select_stmt ("UNION"i query_cmd)? groupby_clause? orderby_clause? ";"? -> query

select_stmt : "SELECT"i columns "FROM"i TABLE_NAME filter_clause? join_clause ";"? -> select
columns : COL_NAME ("," COL_NAME)* 
        | "*" 
        | agg_expr
agg_expr : agg_func "(" (COL_NAME | "*") ")" agg_filter_clause?
agg_filter_clause : "FILTER"i "(" conditions ")" -> agg_filter
agg_func : "COUNT"i | "SUM"i | "AVG"i | "MIN"i | "MAX"i

filter_clause : "WHERE"i conditions -> filter
conditions : condition (LOP condition)*
condition : COL_NAME OP value 
            | "NOT"i condition
            | "(" conditions ")"
OP : "=" | "<" | ">" | "<=" | ">=" | "!="
LOP : "AND"i | "OR"i 
value : NUMBER | STRING

groupby_clause : "GROUP BY"i COL_NAME ("," COL_NAME)* -> groupby
orderby_clause : "ORDER BY"i COL_NAME ("," COL_NAME)* order? -> orderby
order : "ASC"i | "DESC"i

join_clause : "JOIN"i TABLE_NAME "ON"i join_condition -> join
join_condition : COL_NAME "=" COL_NAME ("AND"i COL_NAME "=" COL_NAME)*

STRING : /'[^']*'/ | /"[^"]*"/
COL_NAME : CNAME
TABLE_NAME : CNAME

%import common.CNAME
%import common.NUMBER
%import common.WS
%ignore WS
""".strip()



class Parser():
    def __init__(self):
        self.parser = lark.Lark(GRAMMAR, parser='lalr')
    
    def parse(self, dsl):
        return self.parser.parse(dsl)

# test parser
if __name__ == "__main__":
    try:
        parser = Parser()
        print("Grammar loaded successfully!") 
    except Exception as e:
        print(f"Grammar error: {e}")  

    