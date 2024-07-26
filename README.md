# mono-expenses
Export expenses from [Monobank](https://api.monobank.ua/docs/index.html#tag/Kliyentski-personalni-dani/paths/~1personal~1statement~1{account}~1{from}~1{to}/get) and ingest them into [SingleStoreDB](https://www.singlestore.com/)

Make sure to set environment variables in `.env` file before run. See below.

## Run:
Open a shell and run: `poetry shell`
```bash
python -m mono_expenses --get-statements
python -m mono_expenses --ingest-to-db
```

Once you ingested your data, we may run some queries.
We may either use `mysql` client or use `SQL Editor` in SingleStore cloud portal.
```shell
mysql> select time, description, mcc, amount, comment from Transactions limit 5;
+---------------------+-------------------+------+----------+---------+
| time                | description       | mcc  | amount   | comment |
+---------------------+-------------------+------+----------+---------+
| 2024-07-20 18:20:38 | Atlas United 2024 | 5813 |  -390.00 | NULL    |
| 2024-07-20 10:23:17 | FILATOVA          | 5912 |  -335.14 | NULL    |
| 2024-07-19 12:50:37 | Atlas United 2024 | 4829 | -2975.00 | NULL    |
| 2024-06-28 11:19:03 | Novapay           | 8999 |   -50.00 | NULL    |
| 2024-06-05 11:22:12 | Novus             | 5411 |  -203.85 | NULL    |
+---------------------+-------------------+------+----------+---------+
5 rows in set (0.18 sec)
```

## Dependencies:

- Python3

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
- `singlestoredb` (https://github.com/singlestore-labs/singlestoredb-python)

### Get Monobank API token
- Go to https://api.monobank.ua/ to get your API token
- set it in `MONOBANK_API_TOKEN` environment variable or in `.env` file (see next).

### SingleStoreDB
As for the storage we will use `SingleStoreDB` (formerly known as `MemSQL`).
It allows both on-premises and cloud deployments.
For this project we will use cloud deployment.
You need to create a cluster at https://portal.singlestore.com/
Once you have a cluster, you need to set the following environment variables:
- `DB_HOST`
- `DB_PASSWORD`
- `DB_PORT`, by default `3306`
- `DB_NAME`, your database name
- `DB_USER`, usually `admin`

### Environment variables
Create `.env` file in the root of the project (see `env.example` for reference).
