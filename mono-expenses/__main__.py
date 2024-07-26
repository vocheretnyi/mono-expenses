import os
import requests
import json
import time
from dotenv import load_dotenv
from http import HTTPStatus

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


def main():
    # 1. Get client info
    clientInfoJson = GetClientInfo()
    print("Client info:\n", clientInfoJson)
    # accountId = clientInfoJson['accounts'][0]['id']
    # This means default account
    accountId = 0
    print("Account ID(default = 0):\n", accountId)

    statementsJson = GetAllStatements(accountId, max_iterations=2)
    print("#StatementsJson: ", len(statementsJson))


if "__main__" == __name__:
    main()
