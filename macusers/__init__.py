"""
This module contains utility functions to simplify getting user information on macOS.

Primary Class
    User() -- Contains details about a user on macOS.

Primary Functions
    primary() -- Returns the current or last logged in console user as a User.
    users() -- Returns a list of users as a User class.
    admins() -- Returns a list of admin users as a User class.
"""

import pathlib
import plistlib
import subprocess
import warnings
from typing import Any, Optional, Union

APFS_LIST: Optional[str] = None
FDE_LIST: Optional[str] = None

class User:
    """
    This class contains details about a user on macOS.
    
    Args:
        username (str): The username to initialize information about.
    
    The following properties can be accessed from this class:
    
    - username        : The user's username
    - real_name       : Full name
    - uid             : The user's ID
    - gid             : Primary group ID
    - guid            : Generated user ID - used by APFS
    - home            : Home folder
    - shell           : Default shell
    - admin           : If the user is an admin
    - ssh_access      : If the user has SSH access
    - volume_owner    : If the user is an APFS volume owner
    - secure_token    : If the user has a secure token
    - created         : Epoch time when the user was created
    - password_updated: Epoch time when the user's password was last changed
    """
    
    def __init__(self, username):
        comp = subprocess.run(
            ['dscl', '-plist', '.', 'read', f'/Users/{username}'],
            capture_output=True, check=False)
        self.data = _plist(comp.stdout)
        # `dscl` nestles a PLIST with some data i want, so i unwrap it here.
        self.account_policy_data = _plist(_first(
            self.data.get('dsAttrTypeNative:accountPolicyData', {})))
        
        self.username: str = username
        self.real_name: str = _first(self.data.get('dsAttrTypeStandard:RealName'))
        self.uid: int = int(_first(self.data.get('dsAttrTypeStandard:UniqueID')))
        self.gid: int = int(_first(self.data.get(
            'dsAttrTypeStandard:PrimaryGroupID')))
        # guid is used to match the user to APFS volume ownership.
        self.guid: str = _first(self.data.get('dsAttrTypeStandard:GeneratedUID'))
        self.home: Optional[pathlib.Path] = _path(_first(self.data.get(
            'dsAttrTypeStandard:NFSHomeDirectory')))
        self.shell: Optional[pathlib.Path] = _path(_first(self.data.get(
            'dsAttrTypeStandard:UserShell')))
        self.admin: bool = group_member(self.uid, 'admin')
        self.ssh_access: bool = group_member(self.uid, 'com.apple.access_ssh')
        # volume_owner defaults to the volume '/' which might be incorrect in
        # some cases. anyone running into this should make a subsequent call to
        # resolve. e.g.:
        # user = User('bryan.heinz')
        # user.volume_owner # False
        # user.volume_owner = apfs_owner(self.guid, volume='/System/Volumes/OTHER_DISK')
        # user.volume_owner # True
        self.volume_owner: bool = apfs_owner(self.guid)
        self.secure_token: bool = secure_token_status(username)
        self.created: Optional[str] = self.account_policy_data.get('creationTime')
        self.password_updated: Optional[str] = self.account_policy_data.get('passwordLastSetTime')
    
    def fv_access(self) -> Optional[bool]:
        """
        Return if a user has FileVault access. This is a shortcut for calling fv_access('USERNAME').
        
        NOTE: Requires running with sudo/root. Because of this, it was left outside
              of the User class.
        
        Returns: True if the user has FileVault access, False if not, None if run
            without sudo.
        """
        return fv_access(self.username)
    
    def apfs_owner(self, volume: str = '/') -> bool:
        """
        Return if a user is a volume owner. This is a shortcut for calling apfs_owner(User.guid).
        
        Args:
            volume (str): The volume to check. Defaults to /.
        
        Returns: True of the user is listed as a volume owner, False otherwise.
        """
        return apfs_owner(self.guid, volume)
    
    def secure_token_status(self) -> bool:
        """
        Return if a user has a secure token. This is a shortcut for calling secure_token_status('USERNAME').
        
        Returns: True if the user has a secure token, False otherwise.
        """
        return secure_token_status(self.username)
    
    def dump(self):
        """
        Print all attributes for this User.
        """
        for key, value in self.__dict__.items():
            if key == 'data': continue
            if key == 'account_policy_data': continue
            print(f"{key}: {value}")

def _first(item: Optional[list[Any]]) -> Any:
    """
    Return the first item in a list.
    
    NOTE: This function should be considered private. It may change at any point
          without consideration outside of this module working.
    
    Args:
        item (list): Any type of list.
    
    Returns: The first item in the list or None if there isn't one.
    """
    return next(iter(item or []), None)

def _path(path: Optional[str]) -> Optional[pathlib.Path]:
    """
    Returns a pathlib.Path object if the input path exists.
    
    NOTE: This function should be considered private. It may change at any point
          without consideration outside of this module working.
    
    Args:
        path (str): A path to a file or folder.
    
    Returns: A pathlib.Path object if the path exists or None.
    """
    if path:
        _path = pathlib.Path(path)
        if _path.exists():
            return _path
    return None

def _plist(data: Union[str, bytes]) -> dict:
    """
    Returns a dict object from the input plist data.
    
    NOTE: This function should be considered private. It may change at any point
          without consideration outside of this module working.
    
    Args:
        data (str|bytes): A string (encoded or not) of plist data.
    
    Returns: A dict object with the plist data if valid, otherwise an empty dict.
    """
    if not data: return {}
    if isinstance(data, str):
        data = data.encode('utf-8')
    return plistlib.loads(data)

def primary() -> User:
    """
    Return best-guess primary user for the Mac.
    
    This function does this by getting the current or last logged in console user.
    
    Returns: The best-guess primary user as a User class.
    """
    comp = subprocess.run(
        ['/usr/bin/stat', '-f', '"%Su"', '/dev/console'],
        capture_output=True, check=False)
    username: str = comp.stdout.decode('utf-8')
    
    username = username.replace('"', '')
    
    # fallback in case user is still root
    # if the user is still root after this, root is likely logged in or was the
    # last user to be logged in.
    if username == 'root':
        comp = subprocess.run(
            ["/usr/bin/defaults", "read",
            "/Library/Preferences/com.apple.loginwindow.plist",
            "lastUserName"],
            capture_output=True, check=False)
        username = comp.stdout.decode('utf-8')
    
    user = User(username.strip())
    
    return user

def users(root: bool = True, gid: Optional[int] = None) -> list[User]:
    """
    Return a list of users with a shell.
    
    Args:
        root (bool): True by default to include the root user account. Set to
            False to not include the root account.
        gid   (int): Filter users based on their primary group ID. The default
            is None which returns all users with a shell.
    
    Returns: A list of Users.
    
    Examples:
        macOS Users: root, _www, bryan.heinz, morris.moss
        > macusers.users()
        >> [root, bryan.heinz]
        > macusers.users(gid=20)
        >> [bryan.heinz, morris.moss]
    """
    user_list = []
    comp = subprocess.run(
        ['dscl', '.', 'list', '/Users', 'UserShell'],
        capture_output=True, check=False)
    dscl_users: str = comp.stdout.decode('utf-8')
    for line in dscl_users.splitlines():
        if 'false' in line: continue
        username = line.split(' ')[0]
        user_list.append(User(username))
    if gid is not None:
        return list(filter(lambda u: u.gid == gid, user_list))
    elif root is False:
        return list(filter(lambda u: u.username != 'root', user_list))
    return user_list

def admins(root: bool = True, gid: Optional[int] = None) -> list[User]:
    """
    Returns a list admin users with a shell.
    
    Args:
        root (bool): True by default to include the root user account. Set to
            False to not include the root account.
        gid  (int): Filter users based on their primary group ID. The default
            is None which returns all admin users with a shell.
    
    Returns: A list of admin users as the User class.
    
    Examples:
        macOS Users: root, _www, bryan.heinz (admin), morris.moss (user)
        > macusers.admins()
        >> [root, bryan.heinz]
        > macusers.admins(gid=20)
        >> [bryan.heinz]
    """
    user_list = users(root=root, gid=gid)
    admin_list = list(filter(lambda u: u.admin is True, user_list))
    return admin_list

def group_member(uid: int, group: str) -> bool:
    """
    Check if a user is in a group.
    
    Args:
        uid   (str): User's ID as an int or str.
        group (str): The group name.
    
    Returns: True if the user is an admin, False if not.
    
    Examples:
        > macusers.group_member(501, 'admin')
        >> True
        > macusers.group_member(501, 'com.apple.access_ssh')
        >> False
    """
    comp = subprocess.run(
        ['dsmemberutil', 'checkmembership', '-u', str(uid), '-G', group],
        capture_output=True, check=False)
    output: str = comp.stdout.decode('utf-8')
    if 'group not found' in output.lower():
        warnings.warn(
            "Getting FileVault status requires this script to run as admin.", RuntimeWarning,
            stacklevel=2)
    if 'is a member' in output:
        return True
    return False

def console() -> str:
    """
    Return current or last logged in console user as a String.
    
    DEPRECATED: this function will be removed in the future.
    """
    
    warnings.warn(
        "console() is deprecated, use primary().username for similar functionality.",
        DeprecationWarning, stacklevel=2)
    
    comp = subprocess.run(
        ['/usr/bin/stat', '-f', '"%Su"', '/dev/console'],
        capture_output=True, check=False)
    user: str = comp.stdout.decode('utf-8')
    user = user.replace('"', '')
    
    # fallback in case user is still root
    # if the user is still root after this, root is likely logged in or was the
    # last user to be logged in.
    if user == 'root':
        comp = subprocess.run(
            ["/usr/bin/defaults", "read",
            "/Library/Preferences/com.apple.loginwindow.plist",
            "lastUserName"],
            capture_output=True, check=False)
        user = comp.stdout.decode('utf-8')
    
    return user.strip()

def fv_access(username: str) -> Optional[bool]:
    """
    Return if a user has FileVault access.
    
    NOTE: Requires running with sudo/root. Because of this, it was left outside
          of the User class.
    
    Args:
        username (str): The username for the account to check.
    
    Returns: True if the user has FileVault access, False if not, None if run
        without sudo.
    """
    # using a global to speed up subsequent FDE checks.
    global FDE_LIST
    if FDE_LIST is None:
        comp = subprocess.run(
            ['fdesetup', 'list'],
            capture_output=True, check=False)
        FDE_LIST = comp.stdout.decode('utf-8')
        err: str = comp.stderr.decode('utf-8')
        if 'requires root access' in err:
            warnings.warn(
                "Getting FileVault status requires this script to run as admin.",
                RuntimeWarning, stacklevel=2)
            FDE_LIST = ''
    if FDE_LIST == '':
        return None
    if username in FDE_LIST:
        return True
    return False

def apfs_owner(guid: str, volume: str = '/') -> bool:
    """
    Return if a user is a volume owner.
    
    Args:
        guid   (str): The GeneratedUID of the user to check.
        volume (str): The volume to check. Defaults to /.
    
    Returns: True of the user is listed as a volume owner, False otherwise.
    """
    # getting the APFS owner list is slow. using a global here to make the call once to speed up subsequent user checks.
    global APFS_LIST
    if APFS_LIST is None:
        comp = subprocess.run(
            ['diskutil', 'apfs', 'listUsers', volume],
            capture_output=True, check=False)
        APFS_LIST = comp.stdout.decode('utf-8')
    if guid in APFS_LIST:
        return True
    return False

def secure_token_status(username: str) -> bool:
    """
    Return if a user has a secure token.
    
    Args:
        username (str): The username to check for a secure token.
    
    Returns: True if the user has a secure token, False otherwise.
    """
    # for some reason this commands sends output to stderr instead of stdout...
    comp = subprocess.run(
        ['sysadminctl', '-secureTokenStatus', username],
        capture_output=True, check=False)
    err: str = comp.stderr.decode('utf-8')
    if 'Secure token is ENABLED' in err:
        return True
    return False


if __name__ == '__main__':
    for user in users():
        user.dump()
        print("\n---\n")
    print(repr(console()))
    print(repr(primary().username))
    print([admin.username for admin in admins()])
    print(fv_access('bryanh')) # only works if run as root
