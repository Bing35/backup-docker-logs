import subprocess

def runShell(command):
    runObject = subprocess.run(command, capture_output=True, shell=True, text=True)
    return runObject

