import numpy as np
from textwrap import dedent

def levenshtein(s, t, ratio_calc = True):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return "Your call is off by {} characters".format(distance[row][col])

def check_and_print(usr_input, sop, ratio=0.50, pedantic=True):
    if pedantic:
        while levenshtein(usr_input, sop) < ratio:
            if 'fuck' in usr_input:
                print("Sir, this is a Wendy's.")
            else:
                print('Wrong call!')
            usr_input = input('> ')
        return usr_input
    return usr_input

def settings():
    action = input('''Choose pedantic level.\n
This setting affects how well the program understands your inputs - to put it another way, it's a fancy spellchecker. \nFor example, in level 0 it doesn't matter what you write: the program will accept the input as correct. \nIn "Zurbuchen" mode, "flap 0" and "flaps 0" are two completely separate calls and the \nwrong one will not be accepted. In other words, you will have to type *exactly* what is written in the SOP manual.

The higher the pedantic level, the more pedantic the program will be. I don't recommend Level 3: you'll be incredibly frustrated because you will miss a period or something.

Choose pedantic level [enter number]:\n
0) level 0.
1) level 1.
2) level 2.
3) Zurbuchen.\n>''').lower()

    while action not in [0, 1, 2, 3, 'zurbuchen']:
        if action == '0':
            return 0
        elif action == '1':
            return 0.50
        elif action =='2':
            return 0.80
        elif action == '3':
            return 1
        else:
            action = input('Choose a valid number.\n>')