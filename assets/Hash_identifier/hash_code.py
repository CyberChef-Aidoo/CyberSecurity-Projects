# This is a simple CMD line too to check the 
# hash type of a given hash string. It uses regex to identify the hash type based on its length and character set. 

#Argparse is used to handle command line arguments, allowing users to input a hash string and receive the identified hash type as output.
import argparse
#re is used for regex operations, enabling the script to match the input hash string against predefined patterns for different hash types.
import re
#sys is used for system-specific parameters and functions, allowing the script to handle errors and exit gracefully if necessary.
import sys
#os is used for interacting with the operating system, such as checking for the existence of files or directories, which can be useful for validating input or output paths.
import os
from importlib import import_module
#dataclasses is used to create data classes, which provide a convenient way to define classes that primarily store data, making the code cleaner and more readable.
from dataclasses import dataclass, field
#typing is used for type hinting, allowing the script to specify expected data types for function arguments and return values, which can improve code clarity and help with debugging.
from typing import Literal


try:
    #This block attempts to import the Console and Table classes from the rich library, which are used for creating visually appealing command-line interfaces. If the rich library is not installed, it prints an error message and exits the program. 
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("Missing dependency 'rich'. Run: uv sync", file=sys.stderr)
    sys.exit(1)
