import json
import os
import sys
from datetime import datetime
from manager import FileManager

import pop_engine as pop

DEBUG = True

# Wyjaśnienie sensu istnienia pliku:
# https://www.notion.so/szymanski/The-curious-case-of-the-UserInterface-socket-ab76cfc810d9486bb8ce9199f0cc7efc

if __name__ == "__main__":
    try:
        FileManager(DEBUG)

        # Log clearing
        if os.path.exists('log.log'):
            os.remove('log.log')

        # UserInterface socket generation
        UI = pop.Socket('UserInterface', os.path.abspath(
            'plugins/UserInterface'), '0.0.1', '__template__')

        # return exit code -1 to initiate a restart (useful for UI plugin switching)
        exit_code = -1  # Not implemented in cmd plugin
        while exit_code == -1:

            # App run
            with open('config/config.json', 'r') as file:
                config = json.load(file)
            UI.plug(config['chosen_plugins']['UserInterface'])
            exit_code = UI().run()

    except Exception as e:
        if DEBUG:
            raise e

        with open('log.log', 'r') as l:
            logs = l.read()
        with open(f'crashes/crash-{datetime.now().strftime("%d-%m-%Y-%H-%M")}.txt', 'w') as f:
            f.write(logs)
            f.write('\nEXCEPTION:\n')
            f.write(str(e))
    else:
        sys.exit(exit_code)
