import random

role = {
    "seat": ['captain', 'fo'],
    "duties": random.choice(['PF', 'PM'])
}

engine = {
    "side": random.choice(["left", "right"]),
    "autocoarsen" : random.choices([True, False], weights=(75, 25)),
    "usr_choice" : False,
    'fire_status': random.choice(['fire', 'no fire'])
}

if engine['autocoarsen']:
    script = 'scripts\engineFailures\engineFailAfterV1.txt'
else:
    script = 'scripts\engineFailures\engineFailAfterV1_negAutocoarsen.txt'