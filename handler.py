import json

import crawl_scoring


def test(event, context):
    return crawl_scoring.test(event, context)


def add_game(event, context):
    return crawl_scoring.add_game(event, context)
