_globals = dict((key, value) for key, value in globals().items())

import subprocess
while not raw_input("enter when finished developing and ready for testing; any key + enter to exit: "):
    #subprocess.call(["cd", "C:\\Users\\_\\pythonbs"])
    #subprocess.call(["python", "setup.py install"])
    #subprocess.call(["cd", "C:\\Users\\_\\Documents\\GitHub\\gamestuff"])
    #subprocess.call(["python", "setup.py develop"])
    #subprocess.call(["python", "-m pride.main"])
        
    subprocess.call("cd C:\\Users\\_\\pythonbs", shell=True)
    subprocess.call("python setup.py install", shell=True)
    subprocess.call("cd C:\\Users\\_\\Documents\\GitHub\\gamestuff", shell=True)
    subprocess.call("python  setup.py develop", shell=True)#C:\\Users\\_\\Documents\\GitHub\\gamestuff\\setup.py develop; python -m pride.main", shell=True)    
    subprocess.call("python -m pride.main", shell=True)