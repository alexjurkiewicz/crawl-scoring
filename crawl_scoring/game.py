import json
import os
import re
import time

# We're going to use the low-level object API rather than the higher level
# "resource" API because it's a little faster. But we'll have to serialise
# and deserialise stuff ourselves.
import boto3
import boto3.dynamodb.types

from . import util

# Logfile format escapes : as ::, so we use re.split
# instead of the naive line.split(':')
LINE_SPLIT_PATTERN = re.compile("(?<!:):(?!:)")
DYNAMODB_CLIENT = boto3.client("dynamodb")
DYNAMO_GAMES_TABLE = os.environ["DYNAMO_GAMES_TABLE"]
INTEGER_FIELDS = (
    "xl",
    "sklev",
    "lvl",
    "absdepth",
    "hp",
    "mhp",
    "mmhp",
    "mp",
    "mmp",
    "bmmp",
    "str",
    "int",
    "dex",
    "ac",
    "ev",
    "sh",
    "dur",
    "turn",
    "aut",
    "kills",
    "gold",
    "goldfound",
    "goldspent",
    "scrollsused",
    "potionsused",
    "sc",
    "dam",
    "sdam",
    "tdam",
    "start",
    "end",
)


def _serialise_for_dynamo(obj):
    serialiser = boto3.dynamodb.types.TypeSerializer()
    return {k: serialiser.serialize(v) for k, v in obj.items()}


def _fixup_crawl_timestamp(timestamp):
    # Timestamps end in 'S' and the month is zero-indexed. Fix this up.
    return timestamp[:4] + "%02d" % (int(timestamp[4:6]) + 1) + timestamp[6:-1]


def _fixup_game(game):
    game["start"] = _fixup_crawl_timestamp(game["start"])
    game["end"] = _fixup_crawl_timestamp(game["end"])
    # Fix up races, classes, etc etc
    # TODO everything in https://github.com/zxc23/dcss-scoreboard/blob/master/scoreboard/log_import.py#L108
    for key, val in game.items():
        if key in INTEGER_FIELDS:
            game[key] = int(val)
    return game


def add_game(event, context):
    if "body" not in event:
        print("No body in event!")
        return util.error("Something went wrong.")

    # event["body"] is already decoded when running `sls invoke`
    if os.environ.get("IS_LOCAL"):
        body = event["body"]
    else:
        try:
            body = json.loads(event["body"])
        except:
            return util.error("Couldn't decode body into JSON")

    if "logfile" not in body:
        return util.error("'logfile' not in body")
    if "src" not in body:
        return util.error("'src' not in body")

    game_fields = re.split(LINE_SPLIT_PATTERN, body["logfile"])
    game = {}
    game["src"] = body["src"]
    for field in game_fields:
        key, value = field.split("=", 1)
        value = value.replace("::", ":")
        game[key] = value
    game = _fixup_game(game)

    dynamo_game = _serialise_for_dynamo(game)
    DYNAMODB_CLIENT.put_item(TableName=DYNAMO_GAMES_TABLE, Item=dynamo_game)

    resp = {"statusCode": 200, "body": json.dumps(game)}
    return resp
