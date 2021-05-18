import itertools

with open('scripts/engineFailures/negAutocoarsen.txt') as f:
    for line in itertools.islice(f, 4, None):
        while line:
            print(line)