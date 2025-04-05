"""
This is a benchmark to show how my DSL works.
It covers loading, filtering, cleaning (NA filling, string/number removal, outlier detection),
normalization, value replacement, and visualizations.
"""

from lib.interpreter.interpreter import Interpreter
from lib.parser import Parser
import pandas as pd

parser = Parser()
interpreter = Interpreter()

# -----------------------
# 1. Load the dataset
# -----------------------

dsl = "LOAD 'benchmark/Bank Data.csv' AS bank_data;"
tree = parser.parse(dsl)
interpreter.interpret(tree)

df = interpreter.table['bank_data']
print(f"\nThe query '{dsl}' executed successfully.")
print(df.head())

# -----------------------
# 2. Basic SELECT
# -----------------------

dsl = "SELECT Name FROM bank_data;"
tree = parser.parse(dsl)
result_df = interpreter.interpret(tree)
print(f"\nThe query '{dsl}' executed successfully.")
print(result_df.head())

# -----------------------
# 3. Filtering and Subsetting
# -----------------------

dsl = "SELECT Name, Age FROM bank_data FILTER(Name == 'Aaron Maashoh') AS aaron_subset;"
tree = parser.parse(dsl)
interpreter.interpret(tree)

original_df = interpreter.clean_interpreter.tables["aaron_subset"].copy()
print(f"\nThe query '{dsl}' executed successfully.")
print(original_df.head())

dsl = "SELECT Name, Age FROM bank_data FILTER(Name == 'Aaron Maashoh' AND Age < 24);"
tree = parser.parse(dsl)
print(f"\nThe query '{dsl}' will fail as expected.")
try:
    result_df = interpreter.interpret(tree)
except TypeError as e:
    print(f"TypeError '{e}' caught")

# -----------------------
# 4. Clean the invalid 'Age' entry in different ways
# -----------------------

interpreter.clean_interpreter.tables["aaron_subset"] = original_df.copy()
dsl1 = "DROP ROW 3 FROM aaron_subset;"
tree = parser.parse(dsl1)
result1 = interpreter.interpret(tree)
print("\n[Method 1] After dropping row 3:")
print(result1.head())

interpreter.clean_interpreter.tables["aaron_subset"] = original_df.copy()
dsl2 = "CLEAN NUMERIC aaron_subset Age REMOVE STRINGS;"
tree = parser.parse(dsl2)
result2 = interpreter.interpret(tree)
print("\n[Method 2] After cleaning non-numeric values from 'Age':")
print(result2.head())

interpreter.clean_interpreter.tables["aaron_subset"] = original_df.copy()
dsl3 = "REPLACE aaron_subset ROW 3 COLUMN Age WITH 24;"
tree = parser.parse(dsl3)
result3 = interpreter.interpret(tree)
print("\n[Method 3] After replacing cell (3, Age) with 24:")
print(result3.head())

# -----------------------
# 5. Clean and fill missing values
# -----------------------

dsl4 = "CLEAN NUMERIC bank_data Num_of_Delayed_Payment REMOVE STRINGS;"
tree = parser.parse(dsl4)
interpreter.interpret(tree)

dsl5 = "SELECT * FROM bank_data FILTER(Num_of_Delayed_Payment >= 0) AS delayed_payment;"
tree = parser.parse(dsl5)
interpreter.interpret(tree)

dsl6 = "SELECT COUNT(*) FROM delayed_payment;"
tree = parser.parse(dsl6)
result_df = interpreter.interpret(tree)
print("\nThe count of valid delayed payments:")
print(result_df.head())

df = pd.read_csv('benchmark/Bank Data.csv')
numeric_count = pd.to_numeric(df['Num_of_Delayed_Payment'], errors='coerce')
valid_count = (numeric_count >= 0).sum()
print("The count of valid delayed payments (pandas method):", valid_count)

dsl7 = "FILL NA delayed_payment Num_of_Delayed_Payment WITH MEAN;"
tree = parser.parse(dsl7)
result_df = interpreter.interpret(tree)
print("\nAfter filling missing values with mean in Num_of_Delayed_Payment:")
print(result_df['Num_of_Delayed_Payment'].head())


# -----------------------
# 6. Normalize income column
# -----------------------
print("\nNormalizing the 'Annual_Income' column using MIN-MAX normalization:")
dsl8 = "CLEAN NUMERIC bank_data Annual_Income REMOVE STRINGS;"
tree = parser.parse(dsl8)
interpreter.interpret(tree)

dsl9 = "NORMALIZE bank_data Annual_Income;"
tree = parser.parse(dsl9)
result_df = interpreter.interpret(tree)
print(result_df['Annual_Income'].head())

# -----------------------
# 7. Remove outliers in delay_from_due_date column
# -----------------------
print("\nRemove outliers in 'Delay_from_due_date' using Z-Score method:")
dsl10 = "SELECT * FROM bank_data FILTER(Delay_from_due_date >= 0) AS delay_from_due_date;"
tree = parser.parse(dsl10)
interpreter.interpret(tree)

dsl11 = "FILTER OUTLIERS delay_from_due_date Delay_from_due_date WITH ZSCORE(2.5);"
tree = parser.parse(dsl11)
result_df = interpreter.interpret(tree)

print("Before:")
print(df['Delay_from_due_date'].describe())
print("\nAfter:")
print(result_df['Delay_from_due_date'].describe())

# -----------------------
# 8. Plot Occupation Bar Chart
# -----------------------

dsl12 = "SELECT Occupation FROM bank_data FILTER(Occupation != '_______') AS occupation;"
tree = parser.parse(dsl12)
interpreter.interpret(tree)

dsl13 = "PLOT Occupation FROM occupation AS BAR;"
tree = parser.parse(dsl13)
interpreter.interpret(tree)