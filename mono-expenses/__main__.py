import argparse
import os
import requests
import json
import time
from dotenv import load_dotenv
from http import HTTPStatus
import singlestoredb as s2
from pathlib import Path

load_dotenv()

API_ENDPOINT = "https://api.monobank.ua/"
API_TOKEN = os.environ.get("MONOBANK_API_TOKEN")


def GetCurTimestamp():
    return int(time.time())


def GetClientInfo():
    path = API_ENDPOINT + "personal/client-info"
    response = requests.get(url=path, headers={'X-Token': API_TOKEN})
    if response.status_code != HTTPStatus.OK:
        raise Exception("Status code is not OK(200): ", response.status_code, response.reason)
    # clientInfoJson = json.loads(clientInfoResponse.text)
    return response.json()


# https://api.monobank.ua/personal/statement/{account}/{from}/{to}
# - toUnix is optional (if not provided - current time is used).
#
def GetStatements(account, fromUnix, toUnix=None):
    # 31 days + 1 hour
    MAX_RANGE_TIME_SEC = 2682000
    if toUnix and fromUnix >= toUnix:
        raise Exception("Invalid time range (from > to)", fromUnix, toUnix)
    if toUnix and toUnix - fromUnix > MAX_RANGE_TIME_SEC:
        raise Exception("Invalid time range (to - from > MAX)", fromUnix, toUnix, MAX_RANGE_TIME_SEC)
    cur_time = GetCurTimestamp()
    if not toUnix and cur_time - fromUnix > MAX_RANGE_TIME_SEC:
        raise Exception("Invalid time range (CUR_TIME - from > MAX)", fromUnix, cur_time, MAX_RANGE_TIME_SEC)

    path = API_ENDPOINT + f"personal/statement/{account}/{fromUnix}"
    if toUnix:
        path = path + f"/{toUnix}"
    response = requests.get(url=path, headers={'X-Token': API_TOKEN}, params={})
    if response.status_code != HTTPStatus.OK:
        raise Exception("Status code is not OK(200): ", response.status_code, response.reason)
    return response.json()


def GetAllStatements(account=0, max_iterations=None):
    cur_time = GetCurTimestamp()
    toTime = cur_time
    fromTime = toTime - 31 * 24 * 60 * 60  # 31 days
    iterations = 0
    file = open("statements.json", "w")
    resultJson = json.loads('[]')

    while not max_iterations or iterations < max_iterations:
        print("Iteration(", iterations, ") fromTime: ", fromTime, " toTime: ", toTime)
        statementsJson = GetStatements(account, fromTime, toTime)
        iterations += 1
        if not statementsJson or len(statementsJson) == 0:
            print("Statements are empty, stopping")
            break
        numTransactions = len(statementsJson)
        print("Got transactions: ", numTransactions)
        if numTransactions == 500:
            print("Need to get more transactions")
            toTime = statementsJson[-1]['time'] - 1
        else:
            toTime = fromTime - 1
            fromTime = toTime - 31 * 24 * 60 * 60  # 31 days
        # TODO: print to file each iteration
        resultJson.extend(statementsJson)
        if max_iterations and iterations >= max_iterations:
            print("Max iterations reached, stopping")
            break
        time.sleep(60)

    # For inserting into the database, we need to convert JSON-array to individual JSON objects for each line
    string = json.dumps(resultJson)
    string = string.replace("}]", "},")
    string = string.replace("},", "}\n")
    string = string.replace("[{", "{")
    file.write(string)
    file.close()
    return resultJson


def GetAndStoreStatements():
    # 1. Get client info
    clientInfoJson = GetClientInfo()
    print("Client info:\n", clientInfoJson)
    # accountId = clientInfoJson['accounts'][0]['id']
    # This means default account
    accountId = 0
    print("Account ID(default = 0):\n", accountId)

    # TODO: 2 is just for test, remove it if you need to get all statements
    statementsJson = GetAllStatements(accountId, max_iterations=2)
    print("#StatementsJson: ", len(statementsJson))


def IngestStatementsToDB():
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_username = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")
    s2.options.local_infile = True
    s2.describe_option('local_infile')
    conn = s2.connect(host=db_host, user=db_username, password=db_password, port=db_port, database=db_name)
    cur = conn.cursor()
    # Check the connection
    cur.execute("SELECT @@singlestoredb_version")
    print("Singlestore version: ", cur.fetchone())

    ROOT_DIR = Path(__file__).parent
    table_schema_file = ROOT_DIR / 'schema.sql'
    table_schema_query = table_schema_file.read_text()
    cur.execute(table_schema_query)

    statements_file = ROOT_DIR / 'statements.json'
    statements_full_path = str(statements_file.absolute())

    load_data_file = ROOT_DIR / 'load_data.sql'
    load_data_query = load_data_file.read_text()
    load_data_query = load_data_query.replace('{file_name}', statements_full_path)
    cur.execute(load_data_query)

    # TODO: hardcoded table name
    cur.execute("SELECT COUNT(*) FROM Transactions1")
    print("Number of transactions inserted: ", cur.fetchone())

    cur.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    parser.add_argument('--get-statements', action='store_true', default=False, help='Get and store statements')
    parser.add_argument('--ingest-to-db', action='store_true', default=False, help='Ingest statements to the database')
    args = parser.parse_args()
    if args.get_statements:
        GetAndStoreStatements()
        print("Statements are stored in statements.json")
    if args.ingest_to_db:
        IngestStatementsToDB()
        print("Statements are ingested to the database")


if "__main__" == __name__:
    main()
