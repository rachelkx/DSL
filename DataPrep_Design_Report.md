# DataPrep
CMPT 982 - Special Topics in Networks and Systems: Domain-Specific Languages 

**Kexin Liu**  
**Email**: kla298@sfu.ca  
**Date**: April 3, 2025  

---

## 1. Introduction

This project aims to simplify data preparation tasks, including data cleaning and data visualization, using a SQL-like domain-specific language (DSL).

---

## 2. Domain

The target users of this DSL are data analysts, business analysts, and researchers who have limited programming knowledge. This DSL will help them quickly perform data transformations and cleaning tasks using simple and human-readable rules.

It can be used for:
- Machine learning data preparation  
- Scientific data preprocessing  
- Business data analysis  

---

## 3. Motivation

Many users lack programming skills but need to perform common data preprocessing tasks. This project is designed to lower the barrier for such users by allowing them to prepare data with a human-readable DSL, simplifying the data preprocessing workflow.

---

## 4. Formal Syntax & Semantics

### 4.1 Formal Syntax

```
Program ::= Statement+
Statement ::= LoadStatement
            | SelectStatement
            | CleanCommand
            | PlotCommand
```

#### Load Statement
```
LoadStatement ::= "LOAD" STRING "AS" Identifier 
```

#### Select Statement
```
SelectStatement ::= "SELECT" Columns "FROM" FromClause  
SelectColumns ::= "*" | SelectColumn ("," SelectColumn)*
SelectColumn ::= Identifier | AggExpression

AggExpression ::= AggFunction "(" AggParam ")"
AggFunction ::= "COUNT" | "SUM" | "AVG" | "MIN" | "MAX"
AggParam ::= Identifier | "*"
```

#### Selects with Filters, Group Bys, Order Bys
```
FromClause ::= Identifier (FilterClause | GroupByClause | OrderByClause)*

FilterClause ::= "FILTER" "(" Condition ")"
Condition ::= SimpleCondition
            | Condition LogicalOp Condition
            | "NOT" Condition
            | "(" Condition ")"
SimpleCondition ::= Identifier ComparisonOp Value 
LogicalOp ::= "AND" | "OR"
ComparisonOp ::= "==" | "<" | ">" | "<=" | ">=" | "!="
Value ::= STRING | NUMBER

GroupByClause ::= "GROUP BY" Columns
Columns ::= "(" Identifier ("," Identifier)* ")"

OrderByClause ::= "ORDER BY" OrderColumns
OrderColumns ::= "(" OrderColumn ("," OrderColumn)* ")"
OrderColumn ::= Identifier OrderDirection
OrderDirection ::= "ASC" | "DESC"
```

#### Data Cleaning Commands
```
CleanCommand ::= FillNACommand
               | DropNACommand
               | RemoveStrInNumericCommand
               | RemoveNumInNonNumericCommand
               | DropRowOrColumnCommand
               | ReplaceCellCommand
               | FilterOutliersCommand
               | NormalizeCommand

FillNACommand ::= "FILL NA" Identifier Identifier "WITH" FillMethod 
FillMethod ::= "MEAN" | "MEDIAN" | "MODE" | NUMBER | STRING

DropNACommand ::= "DROP NA" Identifier ("ROWS" | "COLUMNS")
                  ["WHERE" ("ALL" | "ANY")]
                  ["IN" "(" Identifier ("," Identifier)* ")"]

RemoveStrInNumericCommand ::= "CLEAN Numeric" Identifier (Identifier | Columns) "REMOVE STRINGS"

RemoveNumInNonNumericCommand ::= "CLEAN NonNumeric" Identifier (Identifier | Columns) "REMOVE NUMBERS"

DropRowOrColumnCommand ::= "DROP" ("ROW" INT | "COLUMN" Identifier) "FROM" Identifier

ReplaceCellCommand ::= "REPLACE" Identifier "ROW" INT "COLUMN" Identifier "WITH" Value

FilterOutliersCommand ::= "FILTER OUTLIERS" Identifier Identifier
                          ["WITH" OutlierMethod] 
OutlierMethod ::= "ZSCORE" "(" NUMBER ")" | "IQR"

NormalizeCommand ::= "NORMALIZE" Identifier Identifier
                     ["WITH" NormalizeMethod] 
NormalizeMethod ::= "MIN-MAX" | "ZSCORE"
```

#### Plot Command
```
PlotCommand ::= "PLOT" PlotColumns "FROM" Identifier "AS" PlotType 
PlotColumns ::= Identifier ("," Identifier)?
PlotType ::= "HIST" | "HISTOGRAM" | "SCATTER" | "BOX" | "LINE" | "BAR"
```

#### Notes
- `Identifier` represents a user-defined table name or column name.
- Tokens are case-insensitive (e.g., `"LOAD"` matches both `load` and `LOAD`).
- `STRING`, `NUMBER` follow standard string and numeric formats.
- For readability, semicolons(;) used to terminate DSL statements are ignored in this formal syntax. They are optional in the actual DSL grammar.

---

### 4.2 Formal Semantics of DataPrep DSL

Let:
- `Env` be a mapping from table names to Pandas DataFrames.
- `df = Env[T]` means retrieving the DataFrame bound to identifier T.
- `col` represents the name of a column.
- `cols` represents a list of columns, or `"*"` to represent all columns.

---

#### Load Statements
⟦ LOAD "file.csv" AS T ⟧(Env) 
⇒ Env[T] := pd.read_csv("file.csv")

---

#### Select Statements
⟦ SELECT cols FROM T ⟧(Env)  
⇒ Env[T][cols]  

---

##### Select With Filters
⟦ SELECT cols FROM T FILTER(cond) ⟧(Env)  
⇒ df = Env[T]  
⇒ cond_expr = execute_condition(cond)  
⇒ filtered_df = df.query(cond_expr)  
⇒ filtered_df[cols]

Note:
- `cond` is a condition parsed from the DSL (represented as an AST).
- `execute_condition(cond)` compiles it into a Pandas-compatible boolean expression string used in df.query(...).

---

##### Select with GROUP BY
⟦ SELECT col FROM T GROUP BY(cols) ⟧(Env)  
⇒ Env[T].groupby(cols)

---

##### Select with ORDER BY
⟦ SELECT cols FROM T ORDER BY(col1 ORD1, col2 ORD2) ⟧(Env)  
⇒ df = Env[T]  
⇒ sorted_df = df.sort_values(by=[col1, col2], ascending=[True, False])  
⇒ sorted_df[cols]

---

##### Select With Aggregates
⟦ SELECT AggExpr FROM T GROUP BY(cols) ⟧(Env)  
⇒ df = Env[T]  
⇒ result_df = apply_column_selected([AggExpr], df)  
⇒ result_df

Note:
- If any non-aggregated column appears in SELECT, it must also appear in the GROUP BY clause.
- The interpreter stores group-by columns as `self._groupby_columns` for later use inside `apply_column_selected()`, where aggregation expressions are compiled and evaluated using Pandas aggregation functions.

---

#### Clean Commands

##### Fill NA
⟦ FILL NA T col WITH MEAN ⟧(Env)  
⇒ Env[T][col] = Env[T][col].fillna(Env[T][col].mean())

⟦ FILL NA T col WITH 0 ⟧(Env)  
⇒ Env[T][col] = Env[T][col].fillna(0)

---

##### Drop NA
⟦ DROP NA T ROWS WHERE ANY IN (cols) ⟧(Env)  
⇒ Env[T] = Env[T].dropna(subset=[cols], how="any")

⟦ DROP NA T ROWS ⟧(Env)  
⇒ Env[T] = Env[T].dropna()

---

##### Clean Numeric/Non-numeric Values From Non-numeric/Numeric Columns
⟦ CLEAN NUMERIC T col REMOVE STRINGS ⟧(Env)
⇒ Env[T][col] = pd.to_numeric(Env[T][col], errors='coerce')
⇒ Env[T] = Env[T].dropna(subset=[col])

⟦ CLEAN NONNUMERIC T col REMOVE NUMBERS ⟧(Env)
⇒ Env[T] = Env[T][~Env[T][col].apply(lambda x: isinstance(x, (int, float)))]

---

##### Drop Row/Column
⟦ DROP ROW i FROM T ⟧(Env)
⇒ Env[T] = Env[T].drop(index=i)

⟦ DROP COLUMN col FROM T ⟧(Env)
⇒ Env[T] = Env[T].drop(columns=col)

---

##### Replace with Value

⟦ REPLACE T ROW i COLUMN col WITH val ⟧(Env)
⇒ Env[T].at[i, col] = val

---

##### Filter Outliers
⟦ FILTER OUTLIERS T col WITH ZSCORE(k) ⟧(Env)  
⇒ Env[T] = Env[T][abs(zscore(Env[T][col])) < k]

⟦ FILTER OUTLIERS T col WITH IQR ⟧(Env)  
⇒ Env[T] = Env[T][(col ≥ Q1 - 1.5 × IQR) & (col ≤ Q3 + 1.5 × IQR)] 

Note: Q1 is the 25th percentile of col, Q3 is 75th percentile, and IQR is Q3 - Q1.

---

##### Normalize
⟦ NORMALIZE T col WITH MIN-MAX ⟧(Env)  
⇒ Env[T][col] = (Env[T][col] - min) / (max - min)

⟦ NORMALIZE T col WITH ZSCORE ⟧(Env)  
⇒ Env[T][col] = (Env[T][col] - mean) / std

---

#### Plot Commands
⟦ PLOT col FROM T AS HIST ⟧(Env)  
⇒ Env[T][col].plot.hist()

⟦ PLOT col1, col2 FROM T AS SCATTER ⟧(Env)  
⇒ Env[T].plot.scatter(x=col1, y=col2)

---

#### Notes
- `NA` refers to any missing value (e.g., `NaN`, `None`, or `pd.NA`) in a dataset.

---

## 5. Design Considerations
Although the DSL currently only supports **single-table operations**, a dictionary structure is used for the environment variable for two main reasons:
- Most DSL queries require referencing a table name (e.g. `SELECT ... FROM table_name`). Using a dictionary allows the interpreter to check if a table exists before executing queries.
- The use of a dictionary allows future extension to support **multi-table operations** (such as joins) without changing the current structure.
