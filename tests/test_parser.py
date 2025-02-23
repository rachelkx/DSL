import pytest
from lib.parser import Parser
from lark.exceptions import UnexpectedInput

parser = Parser()
def nice_print(dsl_code, tree):
    print(dsl_code)
    print(tree.pretty())

def test_load():
    dsl_code1 = "LOAD 'data.csv' AS users;"
    tree1 = parser.parse(dsl_code1)

    dsl_code2 = "LOAD 'data.csv' AS users"
    tree2 = parser.parse(dsl_code2)

    dsl_code3 = "load 'data.csv' as users"
    tree3 = parser.parse(dsl_code3)

    expected_ast = "load\n  'data.csv'\n  users"
    # assert tree1.pretty().strip() == expected_ast.strip()
    # assert tree2.pretty().strip() == expected_ast.strip()
    # assert tree3.pretty().strip() == expected_ast.strip()
    nice_print(dsl_code1, tree1)
    nice_print(dsl_code2, tree2)
    nice_print(dsl_code3, tree3)


def test_select_with_filter():
    dsl_code = "SELECT name FROM users WHERE age > 18 AND age < 30;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_select_with_multiple_columns():
    dsl_code = "SELECT name, age FROM users;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_select_all_columns():
    dsl_code = "SELECT * FROM users;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)
    

def test_select_with_agg():
    dsl_code = "SELECT COUNT(*) FROM users;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_select_with_agg_where():
    dsl_code = "SELECT COUNT(*) FROM users WHERE age > 18;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)


def test_select_with_agg_where_filter():
    dsl_code = "SELECT COUNT(*) FILTER(WHERE age > 18) FROM users;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_group_by():
    dsl_code = "SELECT name FROM users GROUP BY age;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_group_by_multiple_columns():
    dsl_code = "SELECT name FROM users GROUP BY age, name;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)


def test_order_by():
    dsl_code1 = "SELECT name FROM users ORDER BY age ASC;"
    tree1 = parser.parse(dsl_code1)
    nice_print(dsl_code1, tree1)

    dsl_code2 = "SELECT name FROM users ORDER BY age DESC;"
    tree2 = parser.parse(dsl_code2)
    nice_print(dsl_code2, tree2)

def test_order_by_multiple_columns():
    dsl_code = "SELECT name FROM users ORDER BY age DESC, name ASC;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_complex_query():
    dsl_code = "SELECT name, COUNT(*) FILTER(WHERE age > 18 AND age < 30) FROM users WHERE age > 18 GROUP BY age ORDER BY age DESC;"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_invalid_syntax():
    # test missing quotes
    with pytest.raises(UnexpectedInput):
        parser.parse("LOAD data.csv AS users")

    # test missing column names
    with pytest.raises(UnexpectedInput):
        parser.parse("SELECT FROM users") 

    # test missing FROM keyword
    with pytest.raises(UnexpectedInput):
        parser.parse("SELECT name users") 


