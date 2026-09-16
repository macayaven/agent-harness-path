#!/usr/bin/env python3
"""Offline learner starter. Edit the two functions after writing your prediction.

Reports attempted outputs, never a learning grade; no network, imports from the
course runtime, rubric access, execution of model text, or file writes.
"""
import argparse
import json
from pathlib import Path


def repair_messages(fixture):
    # Your attempt: return a repaired transcript without deleting the assistant calls.
    return None


def useful_reply(reply, variant):
    # Your attempt: return a fixture-specific boolean for the in-scope answer.
    return None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant',choices=['immediate','delayed'],required=True)
    variant=parser.parse_args().variant
    fixture=json.loads(Path(__file__).with_name('fixtures.json').read_text())[variant]
    print('Fixture:',fixture['task_id'])
    print(json.dumps(fixture,indent=2))
    repair=repair_messages(fixture)
    verdicts={name:useful_reply(replies[0],variant) for name,replies in fixture['assistant_replies'].items()}
    if repair is None or any(value is None for value in verdicts.values()):
        print('Attempt pending: write your diagnosis, repair and useful-answer criterion before comparing references.')
    else:
        print('Your proposed transcript:',json.dumps(repair,indent=2))
        print('Your useful-answer results:',verdicts)
        print('Inspect your reasons and boundary cases; these outputs do not certify learning.')


if __name__=='__main__':main()
