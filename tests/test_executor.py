import pytest
from lib.parser import Parser
from lib.interpreter.executor import Executor

parser = Parser()
executor = Executor()

def test_load():
    dsl_code = "LOAD 'data.csv' AS users;"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "LOAD 'data.csv' AS users"

def test_select_with_all_columns():
    dsl_code = "SELECT * FROM users;"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT * FROM users"


def test_select_with_single_column():
    dsl_code = "SELECT name FROM users;"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT name FROM users"

def test_select_with_multiple_columns():
    dsl_code = "SELECT name, age FROM users;"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT name, age FROM users"

def test_select_with_agg():
    dsl_code = "SELECT SUM(salary) FROM users;"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT SUM(salary) FROM users"

    dsl_code2 = "SELECT count(*) FROM users;"
    tree2 = parser.parse(dsl_code2)
    result2 = executor.execute(tree2)
    assert result2 == "SELECT COUNT(*) FROM users"

def test_select_with_filter():
    dsl_code = "SELECT name FROM users FILTER(age > 18);"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT name FROM users FILTER(age > 18)"

def test_select_with_multiple_filter():
    dsl_code = "SELECT name FROM users FILTER(age > 18 AND age < 30);"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT name FROM users FILTER(age > 18 AND age < 30)"

def test_select_with_agg_filter():
    dsl_code = "SELECT COUNT(*) FROM users FILTER(age > 18);"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT COUNT(*) FROM users FILTER(age > 18)"

def test_group_by():
    dsl_code = "SELECT name FROM users GROUP BY(age);"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT name FROM users GROUP BY(age)"

def test_multiple_group_by():
    dsl_code = "SELECT name FROM users GROUP BY(age, country);"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT name FROM users GROUP BY(age, country)"

def test_group_by_multiple_columns():
    dsl_code = "SELECT name FROM users GROUP BY(age, name);"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT name FROM users GROUP BY(age, name)"

def test_order_by():
    dsl_code1 = "SELECT name FROM users ORDER BY(age ASC);"
    tree1 = parser.parse(dsl_code1)
    result1 = executor.execute(tree1)
    assert result1 == "SELECT name FROM users ORDER BY(age ASC)"

    dsl_code2 = "SELECT name FROM users ORDER BY(age DESC);"
    tree2 = parser.parse(dsl_code2)
    result2 = executor.execute(tree2)
    assert result2 == "SELECT name FROM users ORDER BY(age DESC)"

def test_order_by_multiple_columns():
    dsl_code = "SELECT name FROM users ORDER BY(age, name DESC);"
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT name FROM users ORDER BY(age ASC, name DESC)"


def test_complex_query():
    dsl_code = '''
    SELECT name, COUNT(*) FROM users 
    FILTER(age > 18 AND age < 30)
    GROUP BY(age)
    ORDER BY(age DESC);
    '''
    tree = parser.parse(dsl_code)
    result = executor.execute(tree)
    assert result == "SELECT name, COUNT(*) FROM users FILTER(age > 18 AND age < 30) GROUP BY(age) ORDER BY(age DESC)"