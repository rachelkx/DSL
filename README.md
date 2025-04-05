# **DataPrep DSL**

## **1. Introduction**
DataPrep aims to simplify data preparation tasks, including data cleaning and data visualization using a SQL-like domain-specific language (DSL).

## **2. Syntax and Semantics**

The formal syntax and semantics of the DSL are documented in detail in the [ Design Report (Section 4)](https://github.com/rachelkx/DSL/wiki/DataPrep-Design-Report#4-formal-syntax--semantics).
which includes:
- Grammar rules for SELECT, FILTER, GROUP BY, etc.
- Operational semantics for querying, cleaning, and plotting

## **3. Installation**
Python 3.9+ is required, then install the required dependencies:
```
pip install -r requirements.txt
```

## **4. Running DSL Example**
```
from lib.parser import Parser
from lib.interpreter.interpreter import Interpreter

parser = Parser()
interpreter = Interpreter()

dsl = "LOAD 'benchmark/Bank Data.csv' AS bank_data;"
tree = parser.parse(dsl)
interpreter.interpret(tree)
```

## **5. Running Tests**
```
pytest
```

## **6.Running Benchmark**
```
python DSL_benchmark.py
```
