import pytest
import pandas as pd
from lark import Token, Tree
from lib.interpreter.load_interpreter import LoadInterpreter


@pytest.fixture
def interpreter():
    # create a DataLoader instance for every test
    return LoadInterpreter({})

def test_load_csv(interpreter):
    tree = Tree('load_stmt', [
        Token('STRING', "'benchmark/Bank Data.csv'"),
        Token('TABLE_NAME', 'users')
    ])

    table = interpreter.execute(tree)
    assert "Name" in table.columns
    assert isinstance(table, pd.DataFrame)

def test_load_json(interpreter):
    tree = Tree('load_stmt', [
        Token('STRING', "'benchmark/Students_Grading_Dataset.json'"),
        Token('TABLE_NAME', 'students')
    ])
    table = interpreter.execute(tree)
    assert "Student_ID" in table.columns
    assert isinstance(table, pd.DataFrame)

def test_load_invalid_file_format(interpreter):
    tree = Tree('load_stmt', [
        Token('STRING', "'benchmark/invalid_file.txt'"),
        Token('TABLE_NAME', 'invalid_table')
    ])
    with pytest.raises(ValueError):
        interpreter.execute(tree)

def test_load_file_not_exist(interpreter):
    tree = Tree('load_stmt', [
        Token('STRING', "'benchmark/nonexistent.csv'"),
        Token('TABLE_NAME', 'nonexistent_table')
    ])
    with pytest.raises(FileNotFoundError):
        interpreter.execute(tree)