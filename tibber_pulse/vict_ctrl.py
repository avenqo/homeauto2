import os
import time
import subprocess

some_time_in_seconds = 10
while 1:

    # pkill -9 Chromium

    try:
        #Kill Chromium instances from any (preceeding) call
        subprocess.check_call(['pkill', '-9', 'Chromium'],
                              timeout=some_time_in_seconds)
    except subprocess.TimeoutExpired:
        print('subprocess has been killed on timeout')
    except subprocess.CalledProcessError:
        print('No Chromium running')
    else:
        print('Chromium process(es) successfully killed!')

    # Run the 'real' controlling script
    os.system("python3 simple_control.py")
    print("=== Restarting <simple_control.py> ===")
    time.sleep(10.0)  # some time to CTR+C twice
