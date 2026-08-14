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
from rich import print
import string

#this block defines a type alias for the confidence levels that can be assigned to hash identifications, allowing for clearer and more maintainable code when working with these confidence levels.
Confidence = Literal["high", "medium", "low"]


try:
    """
This block attempts to import the Console and Table classes from the rich library, 
which are used for creating visually appealing command-line interfaces. 
If the rich library is not installed, it prints an error message and exits the program. """
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("Missing dependency 'rich'. Run: uv sync", file=sys.stderr)
    sys.exit(1)


#hexdigits from 0-9 and a-f (case insensitive) are used to define the character set for hexadecimal hashes,
#which is important for identifying hash types that use hexadecimal encoding.
HEX_CHARS = frozenset(f"{string.hexdigits}")

#Remember to introduce the "+" symbol should the code not work as expected. 
BASE64_CHARS = frozenset(f"{string.ascii_letters}{string.digits}+/=.")
# base64url alphabet used by JWTs: like base64 but "-" and "_" replace "+" and "/"
BASE64URL_CHARS = frozenset(
    f"{string.ascii_letters}{string.digits}-_="
)


@dataclass(frozen=True)
class HashType:
    """One known hash format we can recognize."""

    name: str
    description: str
    length: int | None = None          # exact character length, if fixed
    prefixes: tuple[str, ...] = field(default_factory=tuple)
    charset: frozenset[str] = HEX_CHARS
    hashcat_mode: str | None = None
    notes: str = ""



#here we define a list of known hash types, each represented by a HashType dataclass instance. 
# This list is used to identify the type of a given hash string based on its characteristics 
# such as prefix, length, and character set.
KNOWN_HASHES: list[HashType] = [
    HashType(
        name="bcrypt",
        description="Slow, salted password hash. Self-announces its format.",
        prefixes=("$2a$", "$2b$", "$2x$", "$2y$"),
        charset=BASE64_CHARS,
        hashcat_mode="3200",
        notes="Cost factor is embedded in the hash itself (e.g. $2b$12$...).",
    ),
    HashType(
        name="Argon2id",
        description="Modern, memory-hard password hash. Winner of the 2015 Password Hashing Competition.",
        prefixes=("$argon2id$",),
        charset=BASE64_CHARS,
        hashcat_mode="34000",
    ),
    HashType(
        name="Argon2i",
        description="Argon2 variant tuned to resist side-channel attacks.",
        prefixes=("$argon2i$",),
        charset=BASE64_CHARS,
        hashcat_mode="34100",
    ),
    HashType(
        name="sha512crypt",
        description="Unix/Linux /etc/shadow password hash (SHA-512 based).",
        prefixes=("$6$",),
        charset=BASE64_CHARS,
        hashcat_mode="1800",
    ),
    HashType(
        name="sha256crypt",
        description="Unix/Linux /etc/shadow password hash (SHA-256 based).",
        prefixes=("$5$",),
        charset=BASE64_CHARS,
        hashcat_mode="7400",
    ),
    HashType(
        name="MD5crypt",
        description="Older Unix password hash format.",
        prefixes=("$1$",),
        charset=BASE64_CHARS,
        hashcat_mode="500",
    ),
    HashType(
        name="MD5",
        description="Fast, unsalted hash. Broken for security use; still common in old systems.",
        length=32,
        hashcat_mode="0",
    ),
    HashType(
        name="NTLM",
        description="Windows password hash (unsalted MD4 of UTF-16LE password).",
        length=32,
        hashcat_mode="1000",
        notes="Same length as MD5 — length alone can't tell them apart.",
    ),
    HashType(
        name="MD4",
        description="Predecessor to MD5. Rare in the wild outside of NTLM.",
        length=32,
        hashcat_mode="900",
    ),
    HashType(
        name="RIPEMD-128",
        description="Uncommon 128-bit hash, occasionally seen in legacy systems.",
        length=32,
        hashcat_mode=None,
    ),
    HashType(
        name="SHA-1",
        description="Fast, unsalted hash. Deprecated for security use since ~2017.",
        length=40,
        hashcat_mode="100",
    ),
    HashType(
        name="SHA-224",
        description="Truncated SHA-2 variant, less common than SHA-256.",
        length=56,
        hashcat_mode="1300",
    ),
    HashType(
        name="SHA-256",
        description="Widely used modern hash. Fast — not safe for passwords without heavy stretching.",
        length=64,
        hashcat_mode="1400",
    ),
    HashType(
        name="SHA-384",
        description="SHA-2 family, 384-bit output.",
        length=96,
        hashcat_mode="10800",
    ),
    HashType(
        name="SHA-512",
        description="SHA-2 family, largest common fixed-length output.",
        length=128,
        hashcat_mode="1700",
    ),
]


@dataclass
class Match:
    hash_type: HashType
    confidence: Confidence
    reason: str


def _looks_like_jwt(value: str) -> bool:
    """JSON Web Tokens are NOT hashes, but they're commonly mistaken for one."""
    parts = value.split(".")
    return len(parts) == 3 and all(BASE64URL_CHARS.issuperset(p) for p in parts if p)


def _matches_charset(value: str, charset: frozenset[str]) -> bool:
    return all(c in charset for c in value)


def identify(value: str) -> list[Match]:
    """Return a list of plausible hash types for the given string, most
    confident first."""
    value = value.strip()
    matches: list[Match] = []

    if _looks_like_jwt(value):
        matches.append(
            Match(
                hash_type=HashType(
                    name="JWT (not a hash)",
                    description="A JSON Web Token — three base64url segments separated by dots. "
                    "Structured and decodable, not a one-way hash.",
                ),
                confidence="high",
                reason="Matches the header.payload.signature JWT structure.",
            )
        )
        return matches

#The dataclass package help users to create classes that are primarily used to store data with less boilerplate code. 
# In this case, the Match class is defined as a dataclass, which automatically generates special 
# methods like __init__(), __repr__(), and __eq__() based on the class attributes. 
# This makes it easier to create instances of Match and work with them in a more structured way.

# 1. Prefix matches are the strongest signal — check these first.
    for h in KNOWN_HASHES:
        if h.prefixes and value.startswith(h.prefixes):
            matches.append(
                Match(
                    hash_type=h,
                    confidence="high",
                    reason=f"Starts with a known prefix for {h.name}.",
                )
            )

    if matches:
        return matches

    # 2. No prefix matched — fall back to length + charset.
    for h in KNOWN_HASHES:
        if h.length is None:
            continue
        if len(value) == h.length and _matches_charset(value, h.charset):
            confidence: Confidence = "medium" if h.charset is HEX_CHARS else "low"
            matches.append(
                Match(
                    hash_type=h,
                    confidence=confidence,
                    reason=f"Length {h.length} and charset match {h.name}.",
                )
            )

    return matches


def render(value: str, matches: list[Match]) -> None:
    console = Console()
    if not matches:
        console.print(
            f"[bold red]No idea[/] — '{value}' doesn't match any known hash "
            "pattern by prefix, length, or charset."
        )
        return

    table = Table(title=f"Possible matches for: {value}")
    table.add_column("Hash Type", style="cyan", no_wrap=True)
    table.add_column("Confidence")
    table.add_column("Hashcat Mode")
    table.add_column("Reason")

    confidence_style = {"high": "bold green", "medium": "yellow", "low": "dim"}

    for m in matches:
        table.add_row(
            m.hash_type.name,
            f"[{confidence_style.get(m.confidence, '')}]{m.confidence}[/]",
            m.hash_type.hashcat_mode or "-",
            m.reason,
        )

    console.print(table)
    if len(matches) == 1 and matches[0].hash_type.notes:
        console.print(f"[dim]{matches[0].hash_type.notes}[/]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hash-identifier",
        description="Guess what algorithm produced a given hash string.",
    )
    parser.add_argument("value", help="the hash string to identify")
    args = parser.parse_args(argv)

    matches = identify(args.value)
    render(args.value, matches)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


