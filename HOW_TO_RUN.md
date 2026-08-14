# How to Run Hash Identifier

This guide covers two ways to run the tool: directly on **Windows (PowerShell)**, or inside **WSL (Ubuntu)**. Pick whichever matches your setup — you don't need both.

---

## Option A — Windows PowerShell (no WSL needed)

### 1. Install dependencies

```powershell
pip install rich pytest
```

If you see an error like `externally-managed-environment`, use a virtual environment instead:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install rich pytest
```

### 2. Navigate to the project folder

```powershell
cd C:\Users\USER\Downloads\CyberSecurity-Projects\hash-identifier
```

(Adjust the path to wherever you actually saved the project.)

### 3. Run the tool

```powershell
python hash_identifier.py 5f4dcc3b5aa765d61d8327deb882cf99
```

**Important:** hashes starting with `$` (like bcrypt) need **double quotes** on Windows:

```powershell
python hash_identifier.py "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQNQy.uK4Of2T7G"
```

### 4. Run the tests

```powershell
python -m pytest test_hash_identifier.py -v
```

---

## Option B — WSL (Ubuntu)

### 1. Open your WSL terminal

Click Start → type "Ubuntu" → open it.

### 2. Navigate to your project

Windows drives are mounted under `/mnt/`. Example:

```bash
cd /mnt/c/Users/USER/Downloads/CyberSecurity-Projects/hash-identifier
```

### 3. Install Python tools (first time only)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-full
```

### 4. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should now show `(.venv)` at the start — that means it's active.

> You'll need to run `source .venv/bin/activate` again every time you open a new terminal window for this project.

### 5. Install dependencies

```bash
pip install rich pytest
```

### 6. Run the tool

```bash
python3 hash_identifier.py 5f4dcc3b5aa765d61d8327deb882cf99
```

Hashes starting with `$` need **single quotes** on Linux/WSL:

```bash
python3 hash_identifier.py '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQNQy.uK4Of2T7G'
```

### 7. Run the tests

```bash
python3 -m pytest test_hash_identifier.py -v
```

---

## Example inputs to try

| Type | Example |
|---|---|
| MD5 | `5f4dcc3b5aa765d61d8327deb882cf99` |
| SHA-1 | `a9993e364706816aba3e25717850c26c9cd0d89d` |
| SHA-256 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| SHA-512 | `cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3` |
| bcrypt | `$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQNQy.uK4Of2T7G` |
| JWT (not a hash) | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U` |
| Garbage / no match | `helloworld` |

---

## Troubleshooting

**`pip install rich pytest` fails with `externally-managed-environment`**
Use a virtual environment (see step 1 in Option A or steps 4-5 in Option B) instead of installing system-wide.

**`ModuleNotFoundError: No module named 'rich'`**
You're not inside the virtual environment, or you forgot to install dependencies. Re-run `pip install rich pytest` in the same terminal you're using to run the tool.

**`python: command not found` (WSL) or `python not recognized` (Windows)**
- WSL: use `python3` instead of `python`.
- Windows: try `py` instead of `python`, or confirm Python is installed and added to PATH.

**A `$`-prefixed hash gets mangled or chopped up**
You forgot to quote it. Use double quotes on Windows (`"$2b$..."`), single quotes on WSL/Linux (`'$2b$...'`).

**`usage: hash-identifier [-h] value` printed with nothing else**
You ran the script without giving it a hash to check. Add one after the command, e.g. `python hash_identifier.py 5f4dcc3b5aa765d61d8327deb882cf99`.
