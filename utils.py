def run(script, role, engine):
    with open(script, "r") as calls:
        print (f"You are the {role['duties']}")
        line = calls.readline()
        while line:
            if line[:2] == role['duties']:
                usr_input = input("> ")

                if role['duties'] == "PM" and not engine['autocoarsen']:
                    if not engine['usr_choice']:
                        if "left" in usr_input:
                            engine['side'] = 'left'
                            engine['usr_choice'] = True
                        elif "right" in usr_input:
                            engine['side'] = 'right'
                            engine['usr_choice'] = True
            else:
                print(line.format(**engine))
            line = calls.readline()
    fire_status = 'no fire'
    script = 'scripts/vitalActions/engineFailure.txt'
    run(script, role, engine)