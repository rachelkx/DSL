import pytest
import pandas as pd
from lark import Tree, Token
from lib.interpreter.clean_interpreter import CleanInterpreter

# test with user-defined data
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Rachel', 'Alice', 'Kristy', 'Peter', 'Xavier'],
    'age': [24, 20, None, 36, None],
    'salary': [1000000, 60000, 75000, 56000, 88000],
    'occupation': [None, 'engineer', 'doctor', 'teacher', 'engineer'],
    'score': ['98', '87', '85', 'not available', '91'],
    'comment': ['execellent', 'average', 3, 'good', 5]
}
df_users = pd.DataFrame(data)

@pytest.fixture
def clean_interpreter():
    return CleanInterpreter({'users': df_users})

def test_fillna_mean(clean_interpreter):
    tree = Tree('fillna_cmd', [
        Token('TABLE_NAME', 'users'),
        Token('COL_NAME', 'age'),
        Token('MEAN', 'mean')
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert df['age'].isnull().sum() == 0
    assert df['age'][2] == pytest.approx((24 + 20 + 36) / 3)

def test_fillna_string(clean_interpreter):
    tree = Tree('fillna_cmd', [
        Token('TABLE_NAME', 'users'),
        Token('COL_NAME', 'occupation'),
        Token('STRING', 'student') 
    ])

    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert df['name'].isnull().sum() == 0
    assert df['occupation'][0] == 'student'

def test_dropna_rows(clean_interpreter):
    tree = Tree('dropna_cmd', [
        Token('TABLE_NAME', 'users'),
        Token('ROWS', 'ROWS')
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert df.isnull().sum().sum() == 0
    assert len(df) == 5

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

def test_remove_str_in_numeric(clean_interpreter):
    tree = Tree('remove_str_in_numeric_cmd', [
        Token('TABLE_NAME', 'users'),
        Tree('columns', [Token('COL_NAME', 'score')])
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    # check if 'not available' is removed
    assert 'not available' not in df['score'].values
    # check if all values in column 'score' is numeric
    assert pd.api.types.is_numeric_dtype(df['score'])

def test_remove_num_in_nonnumeric(clean_interpreter):
    tree = Tree('remove_num_in_nonnumeric_cmd', [
        Token('TABLE_NAME', 'users'),
        Tree('columns', [Token('COL_NAME', 'comment')])
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    # check if all values in 'comment' are strings
    assert df['comment'].apply(lambda x: not isinstance(x, (int, float))).all()

def test_drop_row_by_index(clean_interpreter):
    tree = Tree('drop_row_col_cmd', [
        Tree('row', [Token('INT', '1')]),
        Token('TABLE_NAME', 'users')
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert 1 not in df.index

def test_drop_column(clean_interpreter):
    tree = Tree('drop_row_col_cmd', [
        Tree('column', [Token('COL_NAME', 'occupation')]),
        Token('TABLE_NAME', 'users')
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert 'occupation' not in df.columns

def test_replace_cell(clean_interpreter):
    tree = Tree('replace_cell_cmd', [
        Token('TABLE_NAME', 'users'),
        Token('INT', '0'),
        Token('COL_NAME', 'name'),
        Token('STRING', 'Bob')
    ])
    clean_interpreter.execute(tree)
    df = clean_interpreter.tables['users']
    assert df.at[0, 'name'] == 'Bob'
