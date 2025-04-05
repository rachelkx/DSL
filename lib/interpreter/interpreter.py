from lark import Tree, Token
from lib.interpreter.load_interpreter import LoadInterpreter
from lib.interpreter.select_interpreter import SelectInterpreter
from lib.interpreter.clean_interpreter import CleanInterpreter
from lib.interpreter.plot_interpreter import PlotInterpreter

class Interpreter:
    def __init__(self):
        self.table = {}
        self.load_interpreter = LoadInterpreter(self.table)
        self.select_interpreter = SelectInterpreter(self.table)
        self.clean_interpreter = CleanInterpreter(self.table)
        self.plot_interpreter = PlotInterpreter(self.table)

    def interpret(self, tree):
        if isinstance(tree, Token):
            return tree.value

        if isinstance(tree, Tree):
            if tree.data == "load_stmt":
                return self.load_interpreter.execute(tree)
            elif tree.data == "select_stmt":
                return self.select_interpreter.execute(tree)
            elif tree.data == "clean_cmds":
                return self.clean_interpreter.execute(tree)
            elif tree.data == "plot_cmd":
                return self.plot_interpreter.execute(tree)
            else:
                raise ValueError(f"Unknown operation: {tree.data}")
