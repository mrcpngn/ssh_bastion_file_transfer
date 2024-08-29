import paramiko
import os
from scp import SCPClient

def load_ssh_config(hostname):
    ssh_config_file = os.path.expanduser("~/.ssh/config")
    ssh_config = paramiko.SSHConfig()
    with open(ssh_config_file) as f:
        ssh_config.parse(f)
    return ssh_config.lookup(hostname)

def transfer_directory_via_bastion(target_host):
    with SCPClient(target_host.get_transport()) as scp:
        scp.put(local_dir_path, remote_dir_path, recursive=True)
        print(f"Successfully transferred {local_dir_path} to {remote_dir_path}")
        
def ssh_login_and_transfer_files(jumpbox_host_alias, jumpbox_key_passphrase, target_host_alias, target_key_passphrase):
    try:
        # Load the SSH Config for the Jumpbox
        jumpbox_config = load_ssh_config(jumpbox_host_alias)

        # Retrieve connection details from SSH config
        jumpbox_hostname = jumpbox_config.get('hostname')
        jumpbox_username = jumpbox_config.get('user')
        jumpbox_key_file = os.path.expanduser(jumpbox_config.get('identityfile')[0]) if 'identityfile' in jumpbox_config else None
        jumpbox_port = int(jumpbox_config.get('port', 22))

        # Load the SSH Config for the target host
        target_config = load_ssh_config(target_host_alias)

        # Retrieve connection details from SSH config
        target_hostname = target_config.get('hostname')
        target_username = target_config.get('user')
        target_key_file = os.path.expanduser(target_config.get('identityfile')[0]) if 'identityfile' in target_config else None
        target_port = int(target_config.get('port', 22))

        # Create the Jumpbox SSH client
        jumpbox = paramiko.SSHClient()
        jumpbox.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the private key with the passphrase
        jumpbox_key = paramiko.RSAKey.from_private_key_file(jumpbox_key_file, password=jumpbox_key_passphrase)
        target_key = paramiko.RSAKey.from_private_key_file(target_key_file, password=target_key_passphrase)

        # Connect to the SSH server using the SSH config settings
        jumpbox.connect(hostname=jumpbox_hostname, port=jumpbox_port, username=jumpbox_username, pkey=jumpbox_key)
        jumpbox_transport = jumpbox.get_transport()

        # Get the private address of the Jumpbox
        stdin, stdout, stderr = jumpbox.exec_command('hostname -I | awk \'{print $1}\'')
        src_addr = (stdout.read().decode().strip(), 22)
        dest_addr = (target_hostname, 22)
        jumpbox_channel = jumpbox_transport.open_channel("direct-tcpip",dest_addr, src_addr )

        # Create the taret host SSH client
        target = paramiko.SSHClient()
        target.set_missing_host_key_policy(paramiko.AutoAddPolicy())    
        target.connect(hostname=target_hostname, port=target_port, username=target_username, pkey=target_key, sock=jumpbox_channel)

        # Transfer the file to the target host
        transfer_directory_via_bastion(target)

        # Close the connection
        target.close
        jumpbox.close()
    
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with your SSH alias (defined in ~/.ssh/config)
    jumpbox_host_alias = "enter_jumpbox_host"
    jumpbox_key_passphrase = "enter_jumpbox_ssh_passphrase"

    target_host_alias = "enter_target_host"
    target_key_passphrase = "enter_target_ssh_passphrase"

    local_dir_path = "/path/to/local/directory"  # Local directory to transfer
    remote_dir_path = "/path/to/remote/directory"  # Destination directory on the remote server

    ssh_login_and_transfer_files(jumpbox_host_alias, jumpbox_key_passphrase, target_host_alias, target_key_passphrase)
    