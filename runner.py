from sys import exit
from textwrap import dedent
import random
import os
import re
import itertools


class Scenario:
    role = {
        "seat": 'fo',
        "duties": 'PM' #random.choice(['PF', 'PM'])
    }

    engine = {
        "side": {'failed':random.choice(["left", "right"]), 'choice':False},
        "autocoarsen" : random.choices([True, False], weights=(75, 25)),
        'fire_status': {'state':random.choice(['fire', 'no fire']), 'choice':False}
    }

    vital = {'actions': None}

    script = {'engineFailures': ['check_power', 'posAutocoarsen', 'negAutocoarsen'],
              'vitalActions': ['confirm_levers', 'engine_failure', 'engine_fire', 'engine_failure_fire']}

    #def __init__(self):
    #    pass

    def actions(self):
        action = input('> ').lower()

        if action == 'quit':
            self.quit_game()
        else:
            return action

    def get_script(self,search_pattern):
        search_pattern = search_pattern.replace(' ', '_')
        return 'scripts/' + re.sub(r'\d/.*', "", str(self.search(Scenario.script, search_pattern)[0])) + search_pattern + '.txt'

    def run_lines(self, script, *args, skip_first=False):
        with open(script, "r") as calls:
            line = calls.readline().rstrip()

            if Scenario.role['duties'] == "PM" and skip_first:
                line = calls.readline()

            while line:
                if line[:2] == Scenario.role['duties']:
                    usr_input = self.actions()

                    if 'vital actions' in usr_input:
                        Scenario.vital['actions'] = usr_input.split('vital')[0].split(None, 1)[1].strip()
                        return 'vital_actions'

                else:
                    print(line.format(*args))
                    if "vital actions" in line:
                        Scenario.vital['actions'] = line.split('vital')[0].split(None, 2)[2].strip()
                        return "vital_actions"

                line = calls.readline().rstrip()


    def quit_game(self):
        quit_game = input('Are you sure you want to quit? Progress will not be saved [Y/n]\n> ').lower()

        if quit_game == ('y' or 'yes'):
            exit(0)

        else:
            self.start()


    def start(self):
        pass

    def search(self, d, search_pattern, prev_datapoint_path=''):
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
                for i in self.search(current_datapoint[dkey], search_pattern, c):
                    output.append(i)
        elif type(current_datapoint) is list:
            for i in range(0, len(current_datapoint)):
                if search_pattern in str(i):
                    c = current_datapoint_path
                    c += str(i) + "/"
                    output.append(i)
                c = current_datapoint_path
                c+= str(i) +"/"
                for i in self.search(current_datapoint[i], search_pattern, c):
                    output.append(i)
        elif search_pattern in str(current_datapoint):
            c = current_datapoint_path
            output.append(c)
        output = filter(None, output)
        return list(output)

    def print_line(self, line, format):
        pass


class TakeOff(Scenario):

    scenario_name = 'takeoff'

    def start(self):
        print('take off scenario!')
        return 'vital_actions'


class EngineFailureAfterV1(Scenario):

    scenario_name = 'EngineFailureAfterV1'

    def start(self):

        # Only runs beginning of engine failure SOP, up to "confirm autocoarsen".
        # The first choice the user makes is *after* this script ends.
        self.run_lines(self.get_script('check_power'))

        # Check if user is PM; if so, check for failed side and autocoarsen status
        if Scenario.role['duties'] == 'PM':
            usr_input = self.actions()
            if 'negative' in usr_input:
                Scenario.engine['autocoarsen'] = False
            else:
                Scenario.engine['autocoarsen'] = True

            if "left" in usr_input:
                Scenario.engine['side']['failed'] = 'left'

            elif "right" in usr_input:
                Scenario.engine['side']['failed'] = 'right'


        if Scenario.engine['autocoarsen']:
            return self.run_lines(self.get_script('posAutocoarsen'), Scenario.engine['side']['failed'], skip_first=True)
        else:
            return self.run_lines(self.get_script('negAutocoarsen'), Scenario.engine['side']['failed'], skip_first=True)



class VitalActions(Scenario):

    scenario_name = 'vital_actions'

    def __init__(self):
        super().__init__()
        self.exits = {}
        self.side = Scenario.engine['side']
        self.fire_status = Scenario.engine['fire_status']

    def start(self):


        print(Scenario.vital['actions'])

        self.run_lines('confirm_levers')

        with open(self.get_script(Scenario.vital['actions']), "r") as calls:
            line = calls.readline().rstrip()

            while line:
                if line[:2] == Scenario.role['duties']:
                    usr_input = self.actions()

                    if 'vital actions' in usr_input:
                        Scenario.vital['actions'] = usr_input.split('vital')[0].strip()
                        return 'vital_actions'

                else:
                    print(line.format(self.engine['side']['failed']))
                    if "vital actions" in line:
                        Scenario.vital['actions'] = line.split('vital')[0].strip()
                        return "vital_actions"

                line = calls.readline()

    def engine_vital_actions(self):
        pass

class Map:

    scenarios = {
        'EngineFailureAfterV1' : EngineFailureAfterV1(),
        'vital_actions': VitalActions(),
        'takeoff': TakeOff()
    }

    def __init__(self, start_scenario):
        self.start_scenario = start_scenario

    def next_scenario(self, scenario_name):
        return Map.scenarios.get(scenario_name)

    def opening_scenario(self):
        return self.next_scenario(self.start_scenario)


class Runner:

    def __init__(self, scenario_map):
        self.scenario_map = scenario_map

    def begin(self):
        current_scenario = self.scenario_map.opening_scenario()
        last_scenario = self.scenario_map.next_scenario('last scenario')

        while current_scenario != last_scenario:
            next_scenario_name = current_scenario.start()
            current_scenario = self.scenario_map.next_scenario(next_scenario_name)

        current_scenario.start()

scenario_map = Map('EngineFailureAfterV1')
sop = Runner(scenario_map)
os.system('cls')
sop.begin()