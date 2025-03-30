# a DSL parser that parses the DSL and generates the AST
# used for data visualization and preparation

import lark
from lark.exceptions import UnexpectedInput

# define the grammar for the DSL
GRAMMAR = """
?start : expr

?expr : load_expr
      | select_expr

load_expr : "LOAD"i STRING "AS"i TABLE_NAME ";"? 

select_expr : "SELECT"i columns "FROM"i from_clause ";"?

columns : STAR | column ("," column)*
column : COL_NAME | agg_expr

agg_expr : agg_func "(" agg_param ")"
agg_param: COL_NAME | STAR
agg_func : "COUNT"i -> count
         | "SUM"i -> sum
         | "AVG"i -> avg
         | "MIN"i -> min
         | "MAX"i -> max

?from_clause : TABLE_NAME (filter_clause | groupby_clause | orderby_clause)*

filter_clause : "FILTER"i "(" conditions ")"
?conditions : condition (LOP condition)*
?condition : COL_NAME OP value 
           | "NOT"i condition
           | "(" conditions ")"
OP : "=" | "<" | ">" | "<=" | ">=" | "!="
LOP : "AND"i | "OR"i 
?value : NUMBER | STRING

groupby_clause : "GROUP BY"i group_columns
group_columns : "(" COL_NAME ("," COL_NAME)* ")"

orderby_clause : "ORDER BY"i order_columns
order_columns : "(" order_column ("," order_column)* ")"
order_column : COL_NAME ORDER?
ORDER : "ASC"i | "DESC"i

STRING : /'[^']*'/ | /"[^"]*"/
STAR : "*"
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
        try:
            tree = self.parser.parse(dsl)
            return tree
        except lark.LarkError as e:
            raise UnexpectedInput(f"Error parsing DSL: {e}") from e