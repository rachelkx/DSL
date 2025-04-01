import pytest
import pandas as pd
from lark import Tree, Token
from lib.interpreter.interpreter import Interpreter


# test with user-defined data
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Rachel', 'Alice', 'Kristy', 'Peter', 'Xavier'],
    'age': [24, 20, 24, 36, 45],
    'salary': [1000000, 60000, 75000, 56000, 88000]
}
df_users = pd.DataFrame(data)


@pytest.fixture
# create an interpreter instance
def interpreter():
    interpreter = Interpreter()
    interpreter.table['users'] = df_users
    return interpreter

"""
Test Select Queries
"""
def test_select_with_all_columns(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [Token('STAR', '*')]),
        Tree('from_clause', [Token('TABLE_NAME', 'users')])
    ])
    result_df = interpreter.interpret(tree)
    assert result_df.shape == df_users.shape  
    assert result_df.equals(df_users)  


def test_select_with_single_column(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [Tree('column', [Token('COL_NAME', 'name')])]),
        Tree('from_clause', [Token('TABLE_NAME', 'users')])
    ])
    result_df = interpreter.interpret(tree)
    assert list(result_df.columns) == ["name"]
    assert "Rachel" in result_df["name"].values


def test_select_with_multiple_columns(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [
            Tree('column', [Token('COL_NAME', 'name')]),
            Tree('column', [Token('COL_NAME', 'age')])
        ]),
        Tree('from_clause', [Token('TABLE_NAME', 'users')])
    ])
    result_df = interpreter.interpret(tree)
    assert list(result_df.columns) == ["name", "age"]
    assert "Rachel" in result_df["name"].values


def test_select_with_agg(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [
            Tree('agg_expr', [
                Tree('sum', []),
                Tree('agg_param', [Token('COL_NAME', 'salary')])
            ])
        ]),
        Tree('from_clause', [Token('TABLE_NAME', 'users')])
    ])
    result_df = interpreter.interpret(tree)
    # print(result_df)
    assert result_df.iloc[0, 0] == df_users["salary"].sum()



"""
Test Filter Queries
"""
def test_select_with_filter(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [Tree('column', [Token('COL_NAME', 'name')])]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('filter_clause', [
                Tree('condition', [
                    Token('COL_NAME', 'age'),
                    Token('OP', '>'),
                    Token('NUMBER', '18')
                ])
            ])
        ])
    ])

    result_df = interpreter.interpret(tree)
    assert list(result_df.columns) == ["name"]
    assert "Rachel" in result_df["name"].values


def test_select_with_filter_not(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [Tree('column', [Token('COL_NAME', 'name')])]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('filter_clause', [
                Tree('condition', [
                    Tree('not', [
                        Tree('condition', [
                            Token('COL_NAME', 'age'),
                            Token('OP', '>='),
                            Token('NUMBER', '30')
                        ])
                    ])
                ])
            ])
        ])
    ])
    result_df = interpreter.interpret(tree)
    assert list(result_df.columns) == ["name"]
    assert set(result_df["name"].values) == {"Rachel", "Alice", "Kristy"}



def test_select_with_multiple_filter(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [Tree('column', [Token('COL_NAME', 'name')])]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('filter_clause', [
                Tree('condition', [
                    Tree('condition', [
                        Token('COL_NAME', 'age'),
                        Token('OP', '>'),
                        Token('NUMBER', '18')
                    ]),
                    Token('LOP', 'AND'),
                    Tree('condition', [
                        Token('COL_NAME', 'age'),
                        Token('OP', '<'),
                        Token('NUMBER', '30')
                    ])
                ])
            ])
        ])
    ])
    result_df = interpreter.interpret(tree)
    assert list(result_df.columns) == ["name"]
    assert "Rachel" in result_df["name"].values
    assert "Alice" in result_df["name"].values
    assert "Peter" not in result_df["name"].values

    tree2 = Tree('select_expr', [
        Tree('columns', [Tree('column', [Token('COL_NAME', 'name')])]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('filter_clause', [
                Tree('condition', [
                    Tree('condition', [
                        Token('COL_NAME', 'age'),
                        Token('OP', '<'),
                        Token('NUMBER', '24')
                    ]),
                    Token('LOP', 'OR'),
                    Tree('condition', [
                        Token('COL_NAME', 'age'),
                        Token('OP', '>'),
                        Token('NUMBER', '36')
                    ])
                ])
            ])
        ])
    ])  
    result_df2 = interpreter.interpret(tree2)
    assert list(result_df2.columns) == ["name"]
    assert "Xavier" in result_df2["name"].values
    assert "Rachel" not in result_df2["name"].values

def test_select_with_compound_filter(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [
            Tree('column', [Token('COL_NAME', 'name')])
        ]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('filter_clause', [
                Tree('condition', [  
                    Tree('not', [    
                        Tree('condition', [
                            Tree('condition', [
                                Token('COL_NAME', 'age'),
                                Token('OP', '>'),
                                Token('NUMBER', '18')
                            ]),
                            Token('LOP', 'AND'),
                            Tree('condition', [
                                Token('COL_NAME', 'age'),
                                Token('OP', '<'),
                                Token('NUMBER', '30')
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ])
    result_df = interpreter.interpret(tree)
    assert list(result_df.columns) == ["name"]
    assert set(result_df["name"].values) == {"Peter", "Xavier"} 

"""
Test Group By Queries
"""
def test_group_by(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [
            Tree('column', [Token('COL_NAME', 'age')]),
            Tree('agg_expr', [
                Tree('count', []),
                Tree('agg_param', [Token('STAR', '*')])
            ])
        ]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('groupby_clause', [
                Tree('group_columns', [
                    Tree('column', [Token('COL_NAME', 'age')])
                ])
            ])
        ])
    ])
    result_df = interpreter.interpret(tree)
    assert "count" in result_df.columns
    assert 24 in result_df["age"].values


def test_group_by_multiple_columns(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [
            Tree('column', [Token('COL_NAME', 'age')]),
            Tree('agg_expr', [
                Tree('count', []),
                Tree('agg_param', [Token('STAR', '*')])
            ])
        ]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('groupby_clause', [
                Tree('group_columns', [
                    Tree('column', [Token('COL_NAME', 'age')]),
                    Tree('column', [Token('COL_NAME', 'name')])
                ])
            ])
        ])
    ])
    result_df = interpreter.interpret(tree)
    assert "count" in result_df.columns
    assert (24, "Rachel") in list(zip(result_df["age"], result_df["name"]))


"""
Test Order By Queries
"""
def test_order_by(interpreter):
    tree1 = Tree('select_expr', [
        Tree('columns', [Tree('column', [Token('COL_NAME', 'name')])]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('orderby_clause', [
                Tree('order_columns', [
                    Tree('order_column', [
                        Token('COL_NAME', 'age'),
                        Token('ORDER', 'ASC')
                    ])
                ])
            ])
        ])
    ])
    result_df1 = interpreter.interpret(tree1)
    assert result_df1.iloc[0]["name"] == "Alice"  

    tree2 = Tree('select_expr', [
        Tree('columns', [Tree('column', [Token('COL_NAME', 'name')])]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('orderby_clause', [
                Tree('order_columns', [
                    Tree('order_column', [
                        Token('COL_NAME', 'age'),
                        Token('ORDER', 'DESC')
                    ])
                ])
            ])
        ])
    ])
    result_df2 = interpreter.interpret(tree2)
    assert result_df2.iloc[0]["name"] == "Xavier" 


def test_order_by_multiple_columns(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [Tree('column', [Token('COL_NAME', 'name')])]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('orderby_clause', [
                Tree('order_columns', [
                    Tree('order_column', [
                        Token('COL_NAME', 'age'),
                        Token('ORDER', 'ASC')
                    ]),
                    Tree('order_column', [
                        Token('COL_NAME', 'name'),
                        Token('ORDER', 'DESC')
                    ])
                ])
            ])
        ])
    ])
    result_df = interpreter.interpret(tree)
    assert list(result_df["name"].values) == ["Alice", "Rachel", "Kristy", "Peter", "Xavier"]


"""
Test Compound Queries
"""
def test_select_with_agg_filter(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [
            Tree('agg_expr', [
                Tree('count', []),
                Tree('agg_param', [Token('STAR', '*')])
            ])
        ]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('filter_clause', [
                Tree('conditions', [
                    Tree('condition', [
                        Token('COL_NAME', 'age'),
                        Token('OP', '>'),
                        Token('NUMBER', '18')
                    ])
                ])
            ])
        ])
    ])
    result_df = interpreter.interpret(tree)
    assert result_df.iloc[0, 0] == len(df_users[df_users["age"] > 18])


"""
Test Complex Query
"""
def test_complex_query(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [
            Tree('column', [Token('COL_NAME', 'name')]),
            Tree('agg_expr', [
                Tree('count', []),
                Tree('agg_param', [Token('STAR', '*')])
            ])
        ]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('filter_clause', [
                Tree('condition', [
                    Tree('condition', [
                        Token('COL_NAME', 'age'),
                        Token('OP', '>'),
                        Token('NUMBER', '18')
                    ]),
                    Token('LOP', 'AND'),
                    Tree('condition', [
                        Token('COL_NAME', 'age'),
                        Token('OP', '<'),
                        Token('NUMBER', '30')
                    ])
                ])
            ]),
            Tree('groupby_clause', [
                Tree('group_columns', [
                    Tree('column', [Token('COL_NAME', 'name')]),
                    Tree('column', [Token('COL_NAME', 'age')])
                ])
            ]),
            Tree('orderby_clause', [
                Tree('order_columns', [
                    Tree('order_column', [
                        Token('COL_NAME', 'age'),
                        Token('ORDER', 'DESC')
                    ])
                ])
            ])
        ])
    ])

    result_df = interpreter.interpret(tree)
    assert "name" in result_df.columns
    assert "count" in result_df.columns
    assert 24 in result_df["age"].values

def test_invalid_group_by(interpreter):
    tree = Tree('select_expr', [
        Tree('columns', [
            Tree('column', [Token('COL_NAME', 'name')])
        ]),
        Tree('from_clause', [
            Token('TABLE_NAME', 'users'),
            Tree('groupby_clause', [
                Tree('group_columns', [
                    Tree('column', [Token('COL_NAME', 'age')])
                ])
            ])
        ])
    ])
    with pytest.raises(ValueError):
        interpreter.interpret(tree)