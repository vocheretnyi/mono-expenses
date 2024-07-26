# mono-expenses
Export expenses from Monobank and ingest them into SingleStoreDB

## Dependencies:
### Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
It will add the `poetry` command to Poetry's bin directory, located at: `/Users/USERNAME/.local/bin`.
You need Poetry's bin directory (`/Users/USERNAME/.local/bin`) in your `PATH` environment variable.

e.g. add `export PATH="/Users/USERNAME/.local/bin:$PATH"` to your shell configuration file.

### Poetry dependencies:
- `requests`
- `python-dotenv`

### Get Monobank API token
- Go to https://api.monobank.ua/ to get your API token
- set it in `MONOBANK_API_TOKEN` environment variable or in `.env` file (see next).

### Environment variables
Create `.env` file in the root of the project (see `env.example` for reference).

## Run:
```bash
poetry shell
python -m mono_expenses
```