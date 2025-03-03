# forgemind-backend

## Setup

1. Install Redis. `brew install redis` for Mac.
2. Install [pyenv](https://github.com/pyenv/pyenv) (For Windows, use [pyenv-win](https://github.com/pyenv-win/pyenv-win))
3. Install Python 3.10.12 via pyenv:
   - macOS/Linux: `pyenv install 3.10.12`
   - Windows (PowerShell): `pyenv install 3.10.12`
4. Activate Python 3.10.12 for the shell:
   - macOS/Linux: `pyenv shell 3.10.12`
   - Windows (PowerShell): `pyenv global 3.10.12` (or `pyenv local 3.10.12` if per-project)
5. Set up a virtual environment:
   - `python -m venv venv`
6. Activate the virtual environment:
   - macOS/Linux: `source venv/bin/activate`
   - Windows (PowerShell): `venv\Scripts\Activate.ps1`
7. Install Python dependencies:
   - `python -m pip install -r requirements.txt`
8. Verify installation:
   - `pip list`
9. Run the script:
   - macOS/Linux: `./run_local_mac.sh`
   - Windows (PowerShell): `.\run_local_windows.ps1`

## Adding a dependency
```
pip install <module>
pip freeze > requirements.txt
```

## TODO:
- Replace Flask with FastAPI