# execute the AST from the parser
class Executor:
    def execute(self, tree):
        if tree.data == "load":
            return f"LOAD {tree.children[0]} AS {tree.children[1]}"
        
        elif tree.data == "query_expr":
            columns = self.execute(tree.children[0])
            source = self.execute(tree.children[1])
            return f"SELECT {columns} FROM {source}"


