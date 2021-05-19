class VitalActions(Scenario):

    scenario_name = 'vital_actions'

    def start(self):


        print(Scenario.vital['actions'])

        with open(self.get_script('confirm_levers')) as calls:
            pass

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

        self.run_lines('confirm_levers')
