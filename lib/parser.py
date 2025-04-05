# a DSL parser that parses the DSL and generates the AST
# used for data visualization and preparation

import lark
from lark import Tree, Token
from lark.exceptions import UnexpectedInput

# define the grammar for the DSL
GRAMMAR = """
?start : expr

?expr : load_stmt
      | select_stmt
      | clean_cmds
      | plot_cmd

load_stmt : "LOAD"i STRING "AS"i TABLE_NAME ";"? 

select_stmt : "SELECT"i select_columns "FROM"i from_clause ("AS" TABLE_NAME)? ";"?

select_columns : STAR | select_column ("," select_column)*
select_column : COL_NAME | agg_expr

agg_expr : agg_func "(" agg_param ")"
agg_param: COL_NAME | STAR
agg_func : "COUNT"i -> count
         | "SUM"i -> sum
         | "AVG"i -> avg
         | "MIN"i -> min
         | "MAX"i -> max

from_clause : TABLE_NAME (filter_clause | groupby_clause | orderby_clause)*

filter_clause : "FILTER"i "(" condition ")"

?condition: simple_condition
          | condition LOP condition   -> logical_condition
          | "NOT"i condition          -> not
          | "(" condition ")"

simple_condition: COL_NAME OP value


OP : "==" | "<" | ">" | "<=" | ">=" | "!="
LOP : "AND"i | "OR"i 
?value : NUMBER | STRING

groupby_clause : "GROUP BY"i columns
columns : "(" COL_NAME ("," COL_NAME)* ")"

orderby_clause : "ORDER BY"i order_columns
order_columns : "(" order_column ("," order_column)* ")"
order_column : COL_NAME ORDER?
ORDER : "ASC"i | "DESC"i

clean_cmds : fillna_cmd
           | dropna_cmd
           | remove_str_in_numeric_cmd
           | remove_num_in_nonnumeric_cmd
           | drop_row_col_cmd
           | replace_cell_cmd
           | filter_outliers_cmd
           | normalize_cmd

fillna_cmd : "FILL"i "NA"i TABLE_NAME COL_NAME "WITH"i fill_method ";"?
fill_method : "mean"i     -> mean
            | "median"i   -> median
            | "mode"i     -> mode
            | NUMBER
            | STRING

dropna_cmd : "DROP"i "NA"i TABLE_NAME (ROW | COLUMN) \
            ("WHERE"i ("ALL"i | "ANY"i))? \
            ("IN"i columns)? ";"?

remove_str_in_numeric_cmd : "CLEAN"i "NUMERIC"i TABLE_NAME (COL_NAME | columns) "REMOVE"i "STRINGS"i ";"?
remove_num_in_nonnumeric_cmd : "CLEAN"i "NONNUMERIC"i TABLE_NAME (COL_NAME | columns) "REMOVE"i "NUMBERS"i ";"?

drop_row_col_cmd : "DROP"i (ROW INT | COLUMN COL_NAME) FROM TABLE_NAME ";"?

replace_cell_cmd : "REPLACE"i TABLE_NAME ROW INT COLUMN COL_NAME "WITH"i value ";"?


filter_outliers_cmd : "FILTER"i "OUTLIERS"i TABLE_NAME COL_NAME ("WITH"i outlier_method)? ";"?
outlier_method : "ZSCORE"i "(" NUMBER ")" | "IQR"i

normalize_cmd : "NORMALIZE"i TABLE_NAME COL_NAME ("WITH"i normalize_method)? ";"?
normalize_method : "MIN-MAX"i | "ZSCORE"i

plot_cmd : "PLOT"i (COL_NAME | columns) "FROM"i TABLE_NAME "AS"i PLOT_TYPE ";"?
PLOT_TYPE : ("HIST"i | "HISTOGRAM"i) | "SCATTER"i | "BOX"i | "LINE"i | "BAR"i


STRING : /'[^']*'/ | /"[^"]*"/
STAR : "*"
ROW: /ROW/i
COLUMN: /COLUMN/i
FROM: /FROM/i


COL_NAME : CNAME
TABLE_NAME : CNAME

%import common.CNAME
%import common.NUMBER
%import common.INT
%import common.WS
%ignore WS
"""

class Parser:
    def __init__(self):
        self.parser = lark.Lark(GRAMMAR, parser="lalr")

    def normalize_tree(self, tree):
        # transform the tree to a more readable format:
        # convert all Token('RULE', 'xxx') to str type rule name
        if isinstance(tree, Tree):
            if isinstance(tree.data, Token):
                rule_name = tree.data.value 
            else: 
                rule_name = tree.data

            # Recursively normalize all children
            normalized_child = []
            for child in tree.children:
                normalized_child.append(self.normalize_tree(child))

            return Tree(rule_name, normalized_child)
        else:
            return tree

    def parse(self, dsl):
        try:
            tree = self.parser.parse(dsl)
            return self.normalize_tree(tree)
        except lark.LarkError as e:
            raise UnexpectedInput(f"DSL Parse Error: {e}") 