# a DSL parser that parses the DSL and generates the AST
# used for data visualization and preparation

import lark
from lark.exceptions import UnexpectedInput

# define the grammar for the DSL
GRAMMAR = """
?start : expr

?expr : load_expr
      | select_expr
      | clean_cmds

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

filter_clause : "FILTER"i "(" condition ")"

?condition: simple_condition
          | condition LOP condition   -> logical_condition
          | "NOT"i condition          -> not
          | "(" condition ")"

simple_condition: COL_NAME OP value


OP : "==" | "<" | ">" | "<=" | ">=" | "!="
LOP : "AND"i | "OR"i 
?value : NUMBER | STRING

groupby_clause : "GROUP BY"i group_columns
group_columns : "(" COL_NAME ("," COL_NAME)* ")"

orderby_clause : "ORDER BY"i order_columns
order_columns : "(" order_column ("," order_column)* ")"
order_column : COL_NAME ORDER?
ORDER : "ASC"i | "DESC"i

clean_cmds : fillna_cmd
           | dropna_cmd
           | filter_outliers_cmd
           | normalize_cmd
           | plot_cmd

fillna_cmd : "FILL"i "NA"i TABLE_NAME COL_NAME "WITH"i fill_method ";"?
fill_method : "mean"i | "median"i | "mode"i | NUMBER

dropna_cmd : "DROP"i "NA"i TABLE_NAME ("ROWS"i | "COLUMNS"i) \
            ("WHERE"i ("ALL"i | "ANY"i))? \
            ("IN"i column ("," column)*)? ";"?

filter_outliers_cmd : "FILTER"i "OUTLIERS"i TABLE_NAME COL_NAME ("WITH"i outlier_method)? ";"?
outlier_method : "ZSCORE"i "(" NUMBER ")" | "IQR"i

normalize_cmd : "NORMALIZE"i TABLE_NAME COL_NAME ("WITH"i normalize_method)? ";"?
normalize_method : "MIN-MAX"i | "ZSCORE"i

plot_cmd : "PLOT"i plot_columns "FROM"i TABLE_NAME "AS"i plot_type ";"?
plot_columns : COL_NAME ("," COL_NAME)?
plot_type : "histogram"i | "scatter"i | "box"i | "line"i


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
            raise UnexpectedInput(f"DSL Parse Error: {e}") from e