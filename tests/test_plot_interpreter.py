import pytest
import pandas as pd
import matplotlib.pyplot as plt
from lark import Tree, Token
from lib.interpreter.plot_interpreter import PlotInterpreter

@pytest.fixture
def sample_table():
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45],
        'height': [160, 165, 170, 175, 180],
        'weight': [55, 60, 65, 70, 75],
        'category': ['A', 'B', 'A', 'C', 'B']
    })
    return {'people': df.copy()}

def test_histogram_plot(monkeypatch, sample_table):
    monkeypatch.setattr(plt, "show", lambda: None)
    interpreter = PlotInterpreter(sample_table)
    tree = Tree('plot_cmd', [
        Token('COL_NAME', 'age'),
        Token('TABLE_NAME', 'people'),
        Token('PLOT_TYPE', 'HISTOGRAM')
    ])
    interpreter.execute(tree)

def test_scatter_plot(monkeypatch, sample_table):
    monkeypatch.setattr(plt, "show", lambda: None)
    interpreter = PlotInterpreter(sample_table)
    tree = Tree('plot_cmd', [
        Token('COL_NAME', 'height'),
        Token('COL_NAME', 'weight'),
        Token('TABLE_NAME', 'people'),
        Token('PLOT_TYPE', 'SCATTER')
    ])
    interpreter.execute(tree)

def test_box_plot(monkeypatch, sample_table):
    monkeypatch.setattr(plt, "show", lambda: None)
    interpreter = PlotInterpreter(sample_table)
    tree = Tree('plot_cmd', [
        Token('COL_NAME', 'height'),
        Token('TABLE_NAME', 'people'),
        Token('PLOT_TYPE', 'BOX')
    ])
    interpreter.execute(tree)

def test_line_plot_two_columns(monkeypatch, sample_table):
    monkeypatch.setattr(plt, "show", lambda: None)
    interpreter = PlotInterpreter(sample_table)
    tree = Tree('plot_cmd', [
        Token('COL_NAME', 'age'),
        Token('COL_NAME', 'weight'),
        Token('TABLE_NAME', 'people'),
        Token('PLOT_TYPE', 'LINE')
    ])
    interpreter.execute(tree)

def test_bar_plot(monkeypatch, sample_table):
    monkeypatch.setattr(plt, "show", lambda: None)
    interpreter = PlotInterpreter(sample_table)
    tree = Tree('plot_cmd', [
        Token('COL_NAME', 'category'),
        Token('TABLE_NAME', 'people'),
        Token('PLOT_TYPE', 'BAR')
    ])
    interpreter.execute(tree)