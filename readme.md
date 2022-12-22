# Backup Docker Logs

This script creates a full backup of every docker container's logs periodically. It works on the containers that are running on the same os that the script is running on. The script compresses the backups using gzip and encrypts them using aes-256. Then, it uploads the backup to the cloud, aws s3, inside a folder named as the container name. The structure of the path in the cloud looks like `/ipAddress/containerName/timestamp`. You can change the command so that it uploads to a different storage location. The script should run continually in the background.

## Dependencies
tar gzip gpg docker aws-cli

The scripts uses a `.env` file that contains the password to encrypt the backups with. The content looks like `ENCRYPT_PASSWORD="your password"`.