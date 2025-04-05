import matplotlib.pyplot as plt
import pandas as pd
from lark import Token, Tree

class PlotInterpreter():
    def __init__(self, table):
        self.table = table

    def execute(self, tree):
        col_list = []
        table_name = None
        plot_type = None

        # define the set of valid plot_type values
        PLOT_TYPES = {"HIST", "HISTOGRAM", "SCATTER", "BOX", "LINE"}

        for child in tree.children:
            if isinstance(child, Token):
                if child.type == "COL_NAME":
                    col_list.append(child.value)
                elif child.type == "TABLE_NAME":
                    table_name = child.value
                elif child.type == "PLOT_TYPE":
                    plot_type = child.value.upper()
                else:
                    raise ValueError(f"Unknown token type: {child.type}")
            
            elif isinstance(child, Tree):
                if child.data == "columns":
                    for token in child.children:
                        if isinstance(token, Token) and token.type == "COL_NAME":
                            col_list.append(token.value)
                else:
                    raise ValueError(f"Unknown tree type: {child.data}")

            else:
                raise ValueError(f"Unknown child type: {type(child)}")

        if not table_name or not plot_type:
            raise ValueError("Missing required parameters: table_name or plot_type.")

        if table_name not in self.table:
            raise ValueError(f"Table '{table_name}' not found.")

        df = self.table[table_name]

        # plot
        plt.style.use("default")  
        fig, ax = plt.subplots(figsize=(8, 5), facecolor="#f4f4f4") 

        if plot_type in ["HIST", "HISTOGRAM"]:
            if len(col_list) != 1:
                raise ValueError("Histogram plot requires exactly one column.")
            df[col_list[0]].plot.hist(ax=ax, edgecolor="black", bins=10)  

        elif plot_type == "SCATTER":
            if len(col_list) != 2:
                raise ValueError("Scatter plot requires exactly two columns.")
            df.plot.scatter(
                x=col_list[0], y=col_list[1], ax=ax,
                s=100, edgecolor="black", linewidth=0.8, alpha=0.8  
            )

        elif plot_type == "BOX":
            data = [df[col].dropna().values for col in col_list]
            ax.boxplot(
                data,
                patch_artist=True,
                boxprops=dict(facecolor="#cfe2f3", linewidth=2),
                whiskerprops=dict(linewidth=2),
                capprops=dict(linewidth=2),
                medianprops=dict(color="red", linewidth=2)
            )
            ax.set_xticks(range(1, len(col_list) + 1))
            ax.set_xticklabels(col_list)

        elif plot_type == "LINE":
            if len(col_list) == 1:
                df[col_list].plot.line(ax=ax)
            elif len(col_list) == 2:
                df.plot.line(x=col_list[0], y=col_list[1], ax=ax)
            else:
                raise ValueError("Line plot supports only one or two columns.")
            
        elif plot_type == "BAR":
            if len(col_list) != 1:
                raise ValueError("Bar plot only supports one column.")
            if not pd.api.types.is_object_dtype(df[col_list[0]]) and not pd.api.types.is_categorical_dtype(df[col_list[0]]):
                raise TypeError(f"Bar plot requires a categorical (string-like) column, got {df[col_list[0]].dtype}")
            df[col_list[0]].value_counts().plot.bar(ax=ax, edgecolor="black")
            plt.xticks(rotation=45, ha='right', fontsize=10)
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")

        ax.set_title(f"{plot_type.capitalize()} Plot", fontsize=14)
        if plot_type != "BOX":
            ax.set_xlabel(col_list[0], fontsize=12)
        if len(col_list) > 1:
            ax.set_ylabel(col_list[1], fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()