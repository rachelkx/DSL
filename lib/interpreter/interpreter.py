from lark import Tree, Token
from lib.interpreter.load_interpreter import LoadInterpreter
from lib.interpreter.select_interpreter import SelectInterpreter


class Interpreter:
    def __init__(self):
        self.table = {}
        self.load_interpreter = LoadInterpreter(self.table)
        self.select_interpreter = SelectInterpreter(self.table)

    def interpret(self, tree):
        if isinstance(tree, Token):
            return tree.value

        if isinstance(tree, Tree):
            if tree.data == "load_expr":
                return self.load_interpreter.execute(tree)
            
            elif tree.data == "select_expr":
                return self.select_interpreter.execute(tree, self)

            else:
                raise ValueError(f"Unknown operation: {tree.data}")
