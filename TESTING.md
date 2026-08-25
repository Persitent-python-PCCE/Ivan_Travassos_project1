# Running the tests

Activate the virtual environment first:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies if needed:

```powershell
pip install -r requirements.txt
```

Run the complete test suite with pytest:

```powershell
python -m pytest -q
```

For detailed output:

```powershell
python -m pytest -v
```

Do **not** use `python -m unittest discover` for this project. The test suite is written for **pytest** and uses pytest fixtures such as `client`, `auth_headers`, and `login_session`.

The tests use an in-memory SQLite database, so they do not modify the normal MySQL `hr_management` database.
