### SSH Transfer
Simple python script will transfer files or directory into private host using bastion (jump) server.

NOTE: Before using this script make sure you setup first your SSH config file.

Example:
```
Host bastion
    HostName bastion.example.com
    User bastion_user
    IdentityFile ~/.ssh/bastion_key

Host private
    HostName private.example.com
    User private_user
    IdentityFile ~/.ssh/private_key
    ProxyJump bastion
```
### Prerequisites
- Install the pipenv:

    - ``` sudo apt install pipenv -y ```
- Install the dependencies: 

    - ``` pipenv install paramiko scp ```

### Usage
1.  Change the parameters (hardcoded).

2.  Run script using pipenv: ``` pipenv run python ssh_transfer.py ```

3.  Remove the script on pipenv: ``` pipenv --rm ```
