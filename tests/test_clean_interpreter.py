import pytest
import pandas as pd
from lark import Tree, Token
from lib.interpreter.clean_interpreter import CleanInterpreter

# test with user-defined data
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Rachel', 'Alice', 'Kristy', 'Peter', 'Xavier'],
    'age': [24, 20, None, 36, None],
    'salary': [1000000, 60000, 75000, 56000, 88000]
}
df_users = pd.DataFrame(data)

@pytest.fixture
def clean_interpreter():
    return CleanInterpreter({'users': df_users.copy()})  # 🔁 用 copy 避免跨测试影响

def test_fillna_mean(clean_interpreter):
    tree = Tree('fillna_cmd', [
        Token('TABLE_NAME', 'users'),
        Token('COL_NAME', 'age'),
        Token('METHOD', 'mean')
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert df['age'].isnull().sum() == 0
    assert df['age'][2] == pytest.approx((24 + 20 + 36) / 3)

def test_dropna_rows(clean_interpreter):
    tree = Tree('dropna_cmd', [
        Token('TABLE_NAME', 'users'),
        Token('ROWS', 'ROWS')
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert df.isnull().sum().sum() == 0
    assert len(df) == 3 

def test_filter_outliers_zscore(clean_interpreter):
    tree = Tree('filter_outliers_cmd', [
        Token('TABLE_NAME', 'users'),
        Token('COL_NAME', 'salary'),
        Tree('outlier_method', [
            Token('ZSCORE', 'ZSCORE'),
            Token('NUMBER', '1')
        ])
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert df['salary'].max() < 1000000

def test_filter_outliers_iqr(clean_interpreter):
    tree = Tree('filter_outliers_cmd', [
        Token('TABLE_NAME', 'users'),
        Token('COL_NAME', 'salary'),
        Tree('outlier_method', [
            Token('IQR', 'IQR')
        ])
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert df['salary'].max() < 1000000

def test_normalize_zscore(clean_interpreter):
    tree = Tree('normalize_cmd', [
        Token('TABLE_NAME', 'users'),
        Token('COL_NAME', 'salary'),
        'with',
        'zscore'
    ])
    clean_interpreter.execute(tree)
    col = clean_interpreter.tables['users']['salary']
    assert abs(col.mean()) < 1e-6
    assert round(col.std(), 5) == 1.0
