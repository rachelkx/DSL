# a DSL parser that parses the DSL and generates the AST
# used for data visualization and preparation

import lark

# define the grammar for the DSL
GRAMMAR = """
?start : command

?command : load_cmd
         | query_cmd

load_cmd : "LOAD"i STRING "AS"i TABLE_NAME ";"? -> load

?query_cmd : select_stmt groupby_clause? orderby_clause? ";"?

select_stmt : "SELECT"i columns ("," columns)*  "FROM"i TABLE_NAME where_clause? ";"? -> query
?columns : COL_NAME | "*" | agg_expr

agg_expr : agg_func "(" (COL_NAME | "*") ")" agg_filter_clause? 
agg_filter_clause : "FILTER"i "(" where_clause ")"
agg_func : "COUNT"i | "SUM"i | "AVG"i | "MIN"i | "MAX"i

where_clause : "WHERE"i conditions 
?conditions : condition (LOP condition)*
?condition : COL_NAME OP value 
           | "NOT"i condition
           | "(" conditions ")"
OP : "=" | "<" | ">" | "<=" | ">=" | "!="
LOP : "AND"i | "OR"i 
?value : NUMBER | STRING

groupby_clause : "GROUP BY"i columns ("," columns)* -> groupby
orderby_clause : "ORDER BY"i columns ORDER? ("," columns ORDER?)*  -> orderby
ORDER : "ASC"i | "DESC"i


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

    