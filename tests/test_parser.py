import pytest
from lib.parser import Parser

parser = Parser()
# test load statement
def test_load():
    dsl_code1 = "LOAD 'data.csv' AS users;"
    tree1 = parser.parse(dsl_code1)

    dsl_code2 = "LOAD 'data.csv' AS users"
    tree2 = parser.parse(dsl_code2)

    dsl_code3 = "load 'data.csv' as users"
    tree3 = parser.parse(dsl_code3)

    expected_ast = """
load
  'data.csv'
  users
"""
    assert tree1.pretty().strip() == expected_ast.strip()
    assert tree2.pretty().strip() == expected_ast.strip()
    assert tree3.pretty().strip() == expected_ast.strip()






