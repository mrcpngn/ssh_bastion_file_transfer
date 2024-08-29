import paramiko
import os
import argparse
from paramiko import SSHConfig
from scp import SCPClient

def load_ssh_config(private_host):
    ssh_config = SSHConfig()
    with open(os.path.expanduser('~/.ssh/config')) as f:
        ssh_config.parse(f)
    
    # Lookup the host in the SSH config
    config = ssh_config.lookup(private_host)
    return config

def transfer_directory_via_bastion(private_host):
    with SCPClient(private_host.get_transport()) as scp:
        scp.put(args.local_dir_path, args.remote_dir_path, recursive=True)
        print(f"INFO: Successfully transferred {args.local_dir_path} to {args.remote_dir_path}")

def ssh_to_private_server(private_host, private_passphrase, jumpbox_passphrase):
    try:
        # Load the SSH config for the private host
        config = load_ssh_config(private_host)

        if 'proxyjump' in config:
            # Load the Jumpbox SSH config
            jumpbox = config['proxyjump']
            jumpbox_config = load_ssh_config(jumpbox)
    
            # Create an SSH client for the jumpbox host
            jumpbox_client = paramiko.SSHClient()
            jumpbox_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to  the private server using SSH config settings
            jumpbox_client.connect(
                hostname=jumpbox_config['hostname'],
                username=jumpbox_config.get('user'),
                key_filename=jumpbox_config.get('identityfile'),
                passphrase=jumpbox_passphrase,
            )

            jumpbox_transport = jumpbox_client.get_transport()
            # Get the private address of the Jumpbox
            stdin, stdout, stderr = jumpbox_client.exec_command('hostname -I | awk \'{print $1}\'')
            src_addr = (stdout.read().decode().strip(), 22)
            dest_addr = (config['hostname'], 22)
            jumpbox_channel = jumpbox_transport.open_channel("direct-tcpip",dest_addr, src_addr )

        else:
            proxyjump = None

        # Create an SSH client for the private host
        private_client = paramiko.SSHClient()
        private_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


        # Connect to  the private server using SSH config settings
        private_client.connect(
            hostname=config['hostname'],
            username=config.get('user'),
            key_filename=config.get('identityfile'),
            passphrase=private_passphrase,
            sock=jumpbox_channel
        )

        # Execute a command on the private server
        stdin, stdout, stderr = private_client.exec_command('hostname')
        print(f"INFO: Successfully connected to {(stdout.read().decode().strip())}")

        # Transfer the file to the private host
        transfer_directory_via_bastion(private_client)

        # Close the connection
        private_client.close()
        jumpbox_client.close
    
    except paramiko.AuthenticationException:
        print("ERROR: Authentication failed. Please check your credentials.")
    except Exception as e:
        print(f"ERROR: An error occured: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # File transfer arguments
    parser.add_argument("local_dir_path") 
    parser.add_argument("remote_dir_path")

    # Private host arguments
    parser.add_argument("private_host")
    parser.add_argument("private_passphrase")

    # Jumpbox arguments
    parser.add_argument("jumpbox_passphrase")

    args = parser.parse_args()

    # Pass the arguments to the function
    ssh_to_private_server(args.private_host,args.private_passphrase,args.jumpbox_passphrase)
