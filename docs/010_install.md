# 010 · Install

## Before the lab: checklist for IT

Participants need on their (VDI) machine:

- **Python 3.11–3.14** with the `py` launcher (the default python.org installer). dlt doesn't support Python 3.15 yet.
- **Git**, or permission to download the repository as a ZIP.
- **VS Code** with the *Python* and *Jupyter* extensions, or **PyCharm**.
- **Access to pypi.org** and files.pythonhosted.org, or the URL of an internal package mirror.
- **A local folder that is kept between sessions and not synced by OneDrive**, e.g. `C:\dev`.
- *Lab 060 only:*
  - "ODBC Driver 18 for SQL Server", and network access to the on-prem MinIO and to SQL Server.
  - A MinIO access key, and a SQL Server login (username and password) that can create a schema.
  - If MinIO uses a certificate from the company's own CA, that CA as a PEM file.

## Install

Pick one:

| Option | For |
|--------|-----|
| [A. Windows (PowerShell)](#a-windows-powershell) | Most participants |
| [B. WSL, macOS or Linux](#b-wsl-macos-or-linux) | |
| [C. uv](#c-uv) | If you already use [uv](https://docs.astral.sh/uv/) |

### A. Windows (PowerShell)

Run each command on its own line.

**1. Get the code** into a short local path that OneDrive doesn't sync. Long paths can break the install.

```powershell
mkdir -Force C:\dev
cd C:\dev
git clone https://github.com/kayentaconsulting/dlt_lab.git
cd dlt_lab
```

No Git? Download the ZIP, unzip it to `C:\dev\dlt_lab` and `cd` into that folder.

**2. Check your Python versions.** You need one of 3.11–3.14.

```powershell
py --list
```

**3. Create and activate a virtual environment.** Replace `3.12` with a version from the list:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

Your prompt now starts with `(.venv)`. In every new terminal, `cd` into the repo and activate again.

**4. Install the dependencies:**

```powershell
python -m pip install -r requirements.txt
```

> **"Running scripts is disabled on this system"?** The execution policy is blocking `Activate.ps1`. Pick one:
> - Allow scripts in this window only (no admin needed), then activate again: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
> - Skip activation, and use `.venv\Scripts\python.exe` wherever these docs say `python`.
> - Use Command Prompt (cmd) and activate with `.venv\Scripts\activate.bat`.

### B. WSL, macOS or Linux

```bash
cd ~
git clone https://github.com/kayentaconsulting/dlt_lab.git
cd dlt_lab
python3 --version   # must be 3.11–3.14
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- **"ensurepip is not available"** (Ubuntu/Debian/WSL): run `sudo apt install python3-venv`, then create the venv again.
- **WSL:** clone into your WSL home (`~`), not `/mnt/c`, which is much slower. Open the folder with `code .` (VS Code's WSL extension).
- **Using both Windows and WSL?** Create one `.venv` on each side. A venv from one doesn't work in the other.

### C. uv

```bash
uv sync
```

uv creates `.venv` and downloads a matching Python if needed. Activate `.venv` as above, or prefix commands with `uv run`. Behind corporate SSL inspection, use `uv sync --system-certs`.

## Verify

With the venv activated:

```powershell
python -c "import dlt, duckdb"
dlt --version
```

The first command prints nothing. The second prints `dlt 1.32.0`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` opens the Microsoft Store, or "Python was not found" | Use `py` until the venv is activated, or turn off the *App execution aliases* for `python.exe` in Windows Settings. |
| `py` is not recognised | Python isn't installed from python.org. Ask IT (see the checklist). |
| `SSL: CERTIFICATE_VERIFY_FAILED` during `pip install` | Your network inspects SSL traffic. pip 24.2+ uses the Windows certificate store automatically, so upgrade pip with `python -m pip install --use-feature=truststore --upgrade pip` and rerun the install. |
| Internal package mirror required | `python -m pip config set global.index-url https://<your-mirror>/simple`, then rerun the install. |
| "No matching distribution found for dlt==…" or "requires a different Python" | Python is outside 3.11–3.14. Delete the venv (`Remove-Item -Recurse -Force .venv`) and recreate it with a supported version. |
| Errors about paths being too long | Move the repo to a shorter path, e.g. `C:\dev\dlt_lab`. |

## For maintainers

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. `requirements.txt` is **generated** from the lock for pip users, so don't edit it by hand. After changing dependencies:

```bash
uv add <package>
uv export --format requirements-txt --no-hashes --no-emit-project -o requirements.txt
```

Commit `pyproject.toml`, `uv.lock` and `requirements.txt` together.

---

[Next: 020 Project outline →](020_project_outline.md)
