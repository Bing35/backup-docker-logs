from helper import runShell
import os 
import sys
import datetime
from dotenv import load_dotenv
import time

load_dotenv()

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

def main():
    
    #verify sudo permission
    if runShell('id -u').stdout[:-1] != '0':
        print('you need to run this script as sudo')
        sys.exit()
    
    #get container ids and names
    dockerArray = runShell('docker ps --format "{{.ID}},{{.Names}}"').stdout[:-1].split('\n')
    containerArray = []
    for dockerString in dockerArray:
        itemArray = dockerString.split(',')
        containerArray.append({
            'id': itemArray[0],
            'name': itemArray[1]
        })

    #create backup folders  
    for containerObject in containerArray:
        containerObject['dirPath'] = os.path.abspath(f'/var/backupScripts/{containerObject["name"]}')
        runShell(f'mkdir -p {containerObject["dirPath"]}')
        print(f'{containerObject["id"]}')

    # create backups periodically
    while True:
        for containerObject in containerArray:
            backupTime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            backupFilePath = f'\"{containerObject["dirPath"]}/{backupTime}\"'
            #write logs to file
            #print('docker logs:\n', f'docker logs {containerObject["id"]} > {backupFilePath}')
            print(runShell(f'docker logs {containerObject["id"]} > {backupFilePath}').stderr)

            #clear docker logs
            print(runShell(f'echo > $(docker inspect --format="{{{{.LogPath}}}}" {containerObject["id"]})').stderr)

            #tar and compress logs
            #print('tar: ', f'tar -ca -C {containerObject["dirPath"]} -f {backupTime}.tar.gz {backupTime}')
            print(runShell(f'tar -caf {backupFilePath}.tar.gz -C {containerObject["dirPath"]} {backupTime}').stderr)

            #encrypt file
            runShell(f'gpg --passphrase {os.getenv("ENCRYPT_PASSWORD")} --batch --cipher-algo AES256 --symmetric {backupFilePath}.tar.gz')
            
            #upload to the cloud
            localIpAddress = runShell(f"ip addr | grep -E 'inet .*global dynamic' | head -1 | sed -E 's/ +/ /g' | cut -d' ' -f 3 | cut -d'/' -f 1").stdout[:-1]
            # You can change this command if you use another cloud provider.
            print(runShell(f'aws s3 cp {backupFilePath}.tar.gz.gpg s3://yourS3Bucket/{localIpAddress}/{containerObject["name"]}/').stderr)

            #delete local backups
            runShell(f'rm {containerObject["dirPath"]}/*')
        
        #sleep before next backup
        time.sleep(60*60*24)

            
if __name__ == '__main__':
    main()
