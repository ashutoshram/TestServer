import subprocess
import logprint
import re

# basic get/set test using v4l2
def get_set(device, prop, val, debug, log_file):
    subprocess.call(['{} -c {}={}'.format(device, prop, str(val))], shell=True)
    s = subprocess.check_output(['{} -C {}'.format(device, prop)], shell=True)
    s = s.decode('UTF-8')
    value = re.match("(.*): (\d+)", s)
    logprint.send("setting {} to: {}".format(prop, value.group(2)), debug, log_file)
    if value.group(2) != str(val):
        logprint.send("FAIL: {} get/set not working as intended".format(prop), debug, log_file)
        return -1
    else:
        logprint.send("PASS: Successful {} get/set".format(prop), debug, log_file)
        return 1

def eval_results(ctrl, values, debug, log_file):
    results = {}

    for c, v in zip(range(len(ctrl)), range(len(values))):
        if c == len(ctrl) - 1 or v == len(values) - 1:
            break 
        if (ctrl[c] < ctrl[c + 1] and values[v] < values[v + 1]) or (ctrl[c] > ctrl[c + 1] and values[v] > values[v + 1]):
            results[ctrl[c]] = 1
            results[ctrl[c + 1]] = 1
        else:
            results[ctrl[c]] = -1
            results[ctrl[c + 1]] = -1

    return results
