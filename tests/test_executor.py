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

