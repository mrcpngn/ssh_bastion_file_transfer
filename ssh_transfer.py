import paramiko
import os
from scp import SCPClient

def load_ssh_config(hostname):
    ssh_config_file = os.path.expanduser("~/.ssh/config")
    ssh_config = paramiko.SSHConfig()
    with open(ssh_config_file) as f:
        ssh_config.parse(f)
    return ssh_config.lookup(hostname)

def transfer_directory_via_bastion(private_client):
    with SCPClient(private_client.get_transport()) as scp:
        scp.put(local_dir_path, remote_dir_path, recursive=True)
        print(f"Successfully transferred {local_dir_path} to {remote_dir_path}")
        
def ssh_login_and_transfer_files(hostname_alias, key_passphrase):
    try:
        # Load SSH config
        config = load_ssh_config(hostname_alias)

        # Retrieve connection details from SSH config
        hostname = config.get('hostname')
        username = config.get('user')
        key_file = os.path.expanduser(config.get('identityfile')[0]) if 'identityfile' in config else None
        port = int(config.get('port', 22))

        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the private key with the passphrase
        key = paramiko.RSAKey.from_private_key_file(key_file, password=key_passphrase)

        # Connect to the SSH server using the SSH config settings
        client.connect(hostname=hostname, port=port, username=username, pkey=key)
        print(f"Successfully connected to {hostname_alias} ({hostname})")

        transfer_directory_via_bastion(client)

        # Close the connection
        client.close()
    
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with your SSH alias (defined in ~/.ssh/config)
    hostname_alias = "enter_private_host_here"
    key_passphrase = "enter_ssh_passphase_here"  # Hardcoded passphrase
    local_dir_path = "/path/to/local/directory"  # Local directory to transfer
    remote_dir_path = "/path/to/remote/directory"  # Destination directory on the remote server

    ssh_login_and_transfer_files(hostname_alias, key_passphrase)
