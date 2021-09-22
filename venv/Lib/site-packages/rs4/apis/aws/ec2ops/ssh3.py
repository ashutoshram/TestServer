import boto3
import botocore
import paramiko

if __name__ == "__main__":
    key = paramiko.RSAKey.from_private_key_file("path/to/mykey.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname=instance_ip, username="ubuntu", pkey=key)
    stdin, stdout, stderr = client.exec_command(cmd)
    print (stdout.read())
    client.close()
