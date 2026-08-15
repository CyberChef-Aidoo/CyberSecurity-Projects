import argparse
import re
import sys
from dataclasses import dataclass
from typing import Literal
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
