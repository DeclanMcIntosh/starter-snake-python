import subprocess
import shlex
import time
import json
import string


# Should end with the call to engine: '**/engine'
# Declan's directory: C:/Users/decla/Desktop/Snake Game Server
ENGINE_DIRECTORY = './engine ' 
JSON_FILE_LOCATION = 'snake_list.json '

CREATE_GAME = 'create -c '
RUN_GAME = 'run -g '
GAME_STATUS = 'status -g '

COMPLETE_STATUS = 'Status:"complete"'
SLEEP_TIME = 0.05

#runs command string
def run_command(command_line):
    # split command into list
    args = shlex.split(command_line)

    out = subprocess.Popen(args, \
           stdout=subprocess.PIPE, \
           stderr=subprocess.STDOUT)
    
    stdout, stderr = out.communicate()

    if stderr is None:
        return stdout
    else:
        raise RuntimeError('Error in command line execution. Aborting...')

def main():
    input("Press Enter to continue...")
    while(True):
        output = run_command(ENGINE_DIRECTORY + CREATE_GAME + JSON_FILE_LOCATION)

        hash = json.loads(output)["ID"]
        
        run_command(ENGINE_DIRECTORY + RUN_GAME + hash)

        while (run_command(ENGINE_DIRECTORY + GAME_STATUS + hash).decode("utf-8").find(COMPLETE_STATUS) == -1):
            time.sleep(SLEEP_TIME)

        # TODO generate new json file

# sentinel 
if __name__ == "__main__":
    main()