#These are the necessary imports for the program to function correctly. 

#This is for parsing command-line arguments.
import argparse
#This is for regular expression
import re
#This is for system interaction
import sys
#This is for data classes default boilerplate
from dataclasses import dataclass
#This is for typing hints.
from typing import Literal
#this is for making HTTP requests.
import requests
#this is for rich text formatting or colorful output in the terminal.
from rich.console import Console
#this is for creating panels in the terminal output.
from rich.panel import Panel
#This is for creating tables in the terminal output.
from rich.table import Table

'''This indicates that the Severity type can only take one of the four specified 
string values: "high "medium", "low", or "info". This is useful for type checking and 
ensuring that only valid severity levels are used in the code.'''
Severity = Literal["high", "medium", "low", "info"]
