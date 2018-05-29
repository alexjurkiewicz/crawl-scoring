import json


def error(message, code=500):
    print("Error: %s" % message)
    return response(message, code)


def response(message, code=200, data=None):
    resp = {"statusCode": code, "body": {"message": message}}
    if data:
        resp["body"]["data"] = data
    resp["body"] = json.dumps(resp["body"])
    return resp
