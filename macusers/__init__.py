"""Get the macOS console username and/or a list of local non-system users.

This module is used to get the current or last logged in console user on macOS
instead of the user running the script/program. This module can also return a list of
all local non-system users.

console() - Returns the current or last console user.
users(root=True) - Returns a list of users.
"""

import grp
import pwd
import subprocess


def console():
    """Return current or last console user."""
    def termy(cmd):
        task = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = task.communicate()
        return(out.decode('utf-8'), err.decode('utf-8'))
    
    user, err = termy([
        '/usr/bin/stat',
        '-f', '"%Su"',
        '/dev/console'
    ])
    
    user = user.replace('"', '')
    
    # fallback in case user is still root
    # if the user is still root after this, root is likely logged in or was the
    # last user to be logged in.
    if user == 'root':
        user, err = termy([
            "/usr/bin/defaults", "read",
            "/Library/Preferences/com.apple.loginwindow.plist", "lastUserName"
        ])
    
    user = user.strip()
    
    return(str(user))

def users(root=True):
    """Return a list of local non-system users.
    
    Set root=False to ignore the root/system user.
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
    return(user_names)


if __name__ == '__main__':
    print(repr(users()))
    print(repr(console()))

# install into '/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages' or the equivalent Python version's site-packages folder.
