import os
import json


def test(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event,
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response


def add_game(*args):
    from . import game

    return game.add_game(*args)
