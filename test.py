import re

script = {'engineFailures': ['check_power', 'failure', 'negAutocoarsen']}


def search(d, search_pattern, prev_datapoint_path=''):
    '''
    From Vinay Kumar.
    https://stackoverflow.com/questions/22162321/search-for-a-value-in-a-nested-dictionary-python
    '''

    output = []
    current_datapoint = d
    current_datapoint_path = prev_datapoint_path
    if type(current_datapoint) is dict:
        for dkey in current_datapoint:
            if search_pattern in str(dkey):
                c = current_datapoint_path
                c+= dkey+"/"
                output.append(c)
            c = current_datapoint_path
            c+= dkey+"/"
            for i in search(current_datapoint[dkey], search_pattern, c):
                output.append(i)
    elif type(current_datapoint) is list:
        for i in range(0, len(current_datapoint)):
            if search_pattern in str(i):
                c = current_datapoint_path
                c += str(i) + "/"
                output.append(i)
            c = current_datapoint_path
            c+= str(i) +"/"
            for i in search(current_datapoint[i], search_pattern, c):
                output.append(i)
    elif search_pattern in str(current_datapoint):
        c = current_datapoint_path
        output.append(c)
    output = filter(None, output)
    return list(output)


def get_script_path(d, search_pattern):
    return 'scripts/' + re.sub(r'\d/.*', "", str(search(d, search_pattern)[0])) + search_pattern + '.txt'

t = get_script_path(script, 'check_power')

print(t)