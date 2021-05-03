
# print to file (and optionally terminal)
def send(args, debug, log_file):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)
