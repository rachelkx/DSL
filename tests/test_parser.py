import pytest
from lib.parser import Parser
from lark.exceptions import UnexpectedInput

def nice_print(dsl_code, tree):
    print("\nDSL Code:")
    print(dsl_code)
    print("\nParsed AST:")
    print(tree.pretty())

parser = Parser()
def test_load():
    dsl_code = "LOAD 'data.csv' AS users;"
    tree = parser.parse(dsl_code)
    expected_ast = "load_expr\n  'data.csv'\n  users"
    assert tree.pretty().strip() == expected_ast.strip()

def test_select_with_filter():
    dsl_code = "SELECT name FROM users FILTER(age > 18 AND age < 30);"
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
    dsl_code = "SELECT COUNT(*) FROM users FILTER(age > 18);"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)


def test_select_with_agg_where_filter():
    dsl_code = "SELECT COUNT(*) FROM users FILTER(age > 18);"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_group_by():
    dsl_code = "SELECT name FROM users GROUP BY(age);"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_group_by_multiple_columns():
    dsl_code = "SELECT name FROM users GROUP BY(age, name);"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_order_by():
    dsl_code1 = "SELECT name FROM users ORDER BY(age ASC);"
    tree1 = parser.parse(dsl_code1)
    nice_print(dsl_code1, tree1)

    dsl_code2 = "SELECT name FROM users ORDER BY(age DESC);"
    tree2 = parser.parse(dsl_code2)
    nice_print(dsl_code2, tree2)

def test_order_by_multiple_columns():
    dsl_code = "SELECT name FROM users ORDER BY(age DESC, name ASC);"
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_complex_query():
    dsl_code = """
    SELECT name, COUNT(*) FROM users 
    FILTER(age > 18 AND age < 30)
    GROUP BY(age)
    ORDER BY(age DESC);
    """
    tree = parser.parse(dsl_code)
    nice_print(dsl_code, tree)

def test_invalid_syntax():
    # test missing quotes
    with pytest.raises(UnexpectedInput):
        parser.parse("LOAD data.csv AS users;")

    # test missing column names
    with pytest.raises(UnexpectedInput):
        parser.parse("SELECT FROM users;")

    # test missing keyword FROM
    with pytest.raises(UnexpectedInput):
        parser.parse("SELECT name users;")

    # test invalid aggregate function
    with pytest.raises(UnexpectedInput):
        parser.parse("SELECT INVALID_FUNC(*) FROM users;")
