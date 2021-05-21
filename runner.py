#!/usr/bin/python3
import os
import re
import random
import numpy as np
from platform import system
from sys import exit

from utils import check_and_print, settings

plt = system()

if plt == 'Windows':
    scripts_path = 'C:/Users/adrav/projects/pasco/'
    os.system('cls')
else:
    scripts_path = '/home/ubuntu/sops/'
    os.system('clear')

class Scenario:
    role = {
        "seat": 'FO',
        "duties": random.choice(['PF', 'PM'])
    }

    engine = {
        "side": {'failed':random.choice(["left", "right"])},
        "autocoarsen" : random.choices([True, False], weights=(75, 25)),
        "fire_status": random.choice(["fire", "no fire"]),
        "extinguisher_fired_count": 0
    }

    systems = {'autopilot': {'yaw damp':False, 'autopilot':False},
               'autocoarsen':True,
               'CWP_cancelled': False
    }

    vital = {'actions': None}

    script = {'briefings': ['any_malfunction', 'confirm_autocoarsen'],
              'engineFailures': ['check_power', 'posAutocoarsen', 'negAutocoarsen', 'above_1500', 'confirm_failure', 'shutdown'],
              'vitalActions': ['confirm_levers', 'engine_failure', 'engine_fire', 'engine_failure_fire', 'continued_fire']
    }

    settings = {'pedantic':False}

    def actions(self):
        action = input('> ').lower()

        if action == 'quit':
            return self.quit_game()

        else:
            return action

    def get_script(self,search_pattern):
        search_pattern = search_pattern.replace(' ', '_')
        return scripts_path + 'scripts/' + re.sub(r'\d/.*', "", str(self.search(Scenario.script, search_pattern)[0])) + search_pattern + '.txt'

    def run_lines(self, script, *args, skip_first=False):
        with open(self.get_script(script), "r") as calls:
            line = calls.readline().rstrip()

            if skip_first:
                line = calls.readline().rstrip()

            while line:
                if line[:2] == Scenario.role['duties'] or line[:2] == Scenario.role['seat']:
                    if Scenario.settings['pedantic']:
                        usr_input = check_and_print(self.actions(), line[3:].strip(), pedantic = True)
                    else:
                        usr_input = self.actions()

                    if 'autopilot' in usr_input and Scenario.role['duties'] == 'PF':
                        print('PM: engaged.')
                        Scenario.systems['autopilot']['autopilot'] = True

                    if 'yaw damp' in usr_input and Scenario.role['duties'] == 'PF':
                        print('PM: engaged.')
                        Scenario.systems['autopilot']['yaw damp'] = True

                    if 'vital actions' in usr_input:
                        try:
                            Scenario.vital['actions'] = usr_input.split('vital')[0].split(None, 1)[1].strip()
                        except IndexError:
                            continue
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
            return self.actions()

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

class Briefing(Scenario):
    scenario_name = 'briefing'

    def start(self):
        self.emergency()

    def emergency(self):
        self.run_lines('any_malfunction')

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

            self.run_lines('confirm_autocoarsen', Scenario.engine['side']['failed'], skip_first=True)
        else:
            self.run_lines('confirm_autocoarsen', Scenario.engine['side']['failed'])

        self.run_lines('confirm_failure', Scenario.engine['side']['failed'])
        self.run_lines('confirm_levers', Scenario.engine['side']['failed'])
        if Scenario.role['duties'] == 'PF':
            self.actions()
        else:
            print('PF: engine fire status.')
        self.run_lines('engine_failure', Scenario.engine['side']['failed'])

class TakeOff(Scenario):

    scenario_name = 'takeoff'

    def start(self):
        print('take off scenario!')
        return 'vital_actions'


class EngineFailure(Scenario):

    scenario_name = 'EngineFailure'

    def start(self):

        if Scenario.systems['autocoarsen']:
            return self.after_v1()

        elif 'shutdown' in Scenario.vital['actions']:
            return self.shutdown()

        else:
            return self.above_1500()

    def after_v1(self):
        # Only runs beginning of engine failure SOP, up to "confirm autocoarsen".
        # The first choice the user makes is *after* this script ends.
        self.run_lines('check_power')

        # Check if user is PM; if so, check for failed side and autocoarsen status from user input
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
            if Scenario.role['duties'] == 'PF':
                return self.run_lines('posAutocoarsen', Scenario.engine['side']['failed'])
            else:
                return self.run_lines('posAutocoarsen', Scenario.engine['side']['failed'], skip_first=True)
        else:
            if Scenario.role['duties'] == 'PF':
                return self.run_lines('negAutocoarsen', Scenario.engine['side']['failed'])
            else:
                return self.run_lines('negAutocoarsen', Scenario.engine['side']['failed'], skip_first=True)

    def above_1500(self):
        self.run_lines('above_1500')
        if Scenario.role['duties'] == 'PF':
            usr_input = self.actions()
            if 'left' in usr_input:
                Scenario.engine['side']['failed'] = 'left'

            else:
                Scenario.engine['side']['failed'] = 'right'

            return self.run_lines('confirm_failure', Scenario.engine['side']['failed'], skip_first=True)

        else:
            return self.run_lines('confirm_failure', Scenario.engine['side']['failed'])

    def shutdown(self):
        if Scenario.role['duties'] == 'PF':
            usr_input = self.actions()
            if 'left' in usr_input:
                Scenario.engine['side']['failed'] = 'left'

            else:
                Scenario.engine['side']['failed'] = 'right'

            return self.run_lines('shutdown', Scenario.engine['side']['failed'], skip_first=True)

        else:
            return self.run_lines('shutdown', Scenario.engine['side']['failed'])

class VitalActions(Scenario):

    scenario_name = 'vital_actions'

    def start(self):
        # Add logic for calling vital actions without specifying which ones (AKA when Scenario.vital['actions'] = None)
        if 'engine failure' in Scenario.vital['actions']:
            return self.engine_vital_actions()

        elif 'engine shutdown' in Scenario.vital['actions']:
            return self.run_lines('confirm_levers', Scenario.engine['side']['failed'])

    def engine_vital_actions(self):

        self.run_lines('confirm_levers', Scenario.engine['side']['failed'])

        if Scenario.role['duties'] == 'PM':
            print('PF: engine fire status.')
            usr_input = self.actions()
            if 'no' in usr_input:
                Scenario.engine['fire_status'] = 'no fire'
            else:
                Scenario.engine['fire_status'] = 'fire'

        if Scenario.engine['fire_status'] == 'fire':
            if Scenario.role['duties'] == 'PM':
                self.run_lines('engine_fire', Scenario.engine['side']['failed'], Scenario.engine['fire_status'], skip_first=True)
                Scenario.engine['extinguisher_fired_count'] += 1
                usr_input = self.actions()

                if 'no' in usr_input:
                    Scenario.engine['fire_status'] = 'no fire'
                    self.run_lines('engine_failure', Scenario.engine['side']['failed'], Scenario.engine['fire_status'], skip_first=True)

                else:
                    self.run_lines('continued_fire', Scenario.engine['side']['failed'], Scenario.engine['fire_status'], skip_first=True)

            else:
                self.run_lines('engine_fire', Scenario.engine['side']['failed'], Scenario.engine['fire_status'])
                Scenario.engine['fire_status'] = random.choice(['fire', 'no fire'])

                if Scenario.engine['fire_status'] == 'fire':
                    self.run_lines('continued_fire', Scenario.engine['side']['failed'], Scenario.engine['fire_status'])

                else:
                    self.run_lines('engine_failure', Scenario.engine['side']['failed'])
        else:
            if Scenario.role['duties'] == 'PM':
                self.run_lines('engine_failure', Scenario.engine['side']['failed'], skip_first=True)

            else:
                self.actions()
                self.run_lines('engine_failure', Scenario.engine['side']['failed'])

        return 'after takeoff checks'


class SOP:

    scenarios = {
        'Briefing' : Briefing(),
        'EngineFailure' : EngineFailure(),
        'vital_actions': VitalActions(),
        'takeoff': TakeOff()
    }

    def __init__(self, start_scenario):
        self.start_scenario = start_scenario

    def next_scenario(self, scenario_name):
        return SOP.scenarios.get(scenario_name)

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

        try:
            current_scenario.start()
        except Exception as e:
            return 'EngineFailure'
            print(e)
            print('Invalid input, re-starting')


scenario_map = SOP('EngineFailure')
sop = Runner(scenario_map)
print('You are the ' + Scenario.role['duties'] + ". \nThis an engine failure scenario.")
Scenario.settings['pedantic'] = settings()
sop.begin()
