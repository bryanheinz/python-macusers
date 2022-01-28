"""
This module contains utilities to simplify getting user information on macOS.

You can get the current or last logged in console user on macOS instead of the
user running the script/program. This module can also return a list of all local
non-system users.

Functions
    console() -- Returns the current or last console user.
    users(root=True) -- Returns a list of users.
"""

import grp
import pwd
import subprocess


#
# TODO:
# - admin users
# - SSH enabled users
# - FV enabled users
# - securetoken enabled users
# - print each user with the above status'
#


# TODO: remove
print("loaded dev")


def _termy(cmd):
    """
    Run subprocess system commands and return the results as a String.
    
    NOTE: This function should be considered private. It may change at any point
          without consideration outside of this module working.
    
    Args:
        cmd ([Str])-- the command to run as a list of strings.
    
    Returns:
        stdout -- the commands STDOUT as a String.
        stderr -- the commands STDERR as a String.
    """
    task = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = task.communicate()
    return stdout.decode('utf-8'), stderr.decode('utf-8')

def console():
    """
    Return current or last logged in console user as a String.
    """
    user, _ = _termy([
        '/usr/bin/stat',
        '-f', '"%Su"',
        '/dev/console'
    ])
    
    user = user.replace('"', '')
    
    # fallback in case user is still root
    # if the user is still root after this, root is likely logged in or was the
    # last user to be logged in.
    if user == 'root':
        user, _ = _termy([
            "/usr/bin/defaults", "read",
            "/Library/Preferences/com.apple.loginwindow.plist", "lastUserName"
        ])
    
    return user.strip()

def users(root=True):
    """
    Return a list of local non-system users.
    
    Args:
        root (Bool): True by default to include the root user account. Set to
            False to not include the root account.
    """
    user_names = []
    # by default, all locally created users are in the staff group
    staff_users = grp.getgrgid(20).gr_mem
    for su in staff_users:
        u = pwd.getpwnam(su)
        # filter our macOS users by filtering out false pw_shells
        if u.pw_shell == '/usr/bin/false': continue
        # skip if ignoring root user
        if root == False and u.pw_uid == 0: continue
        user_names.append(u.pw_name)
    return user_names


if __name__ == '__main__':
    print(repr(users()))
    print(repr(console()))
