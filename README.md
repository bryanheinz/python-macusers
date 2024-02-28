# macusers

Get details on macOS user accounts.

```python
>>> import macusers
# get the logged in user details.
>>> user = macusers.primary()
# get the logged in user's username.
>>> user.username
'bryanheinz'
# get logged in user's home folder as a `pathlib` object.
>>> user.home
PosixPath('/Users/bryanh')
# get a list of non-system user accounts.
>>> for user in macusers.users(False): print(user.username)
bryanheinz
morrismoss
# get a list of admin accounts.
>>> for admin in macusers.admins(False): print(admin.username)
bryanheinz
# check if the user has FileVault access. NOTE: requires admin.
>>> macusers.primary().fv_access()
True
# check if the user is an APFS volume owner.
>>> macusers.primary().apfs_owner()
True
# check if the user has a secure token.
>>> macusers.primary().secure_token_status()
True
```

This module is used to get the current or last (if the system currently doesn't have any logged in users) logged in console user on macOS instead of the user running the script/program.

This module now contains the following User properties:

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

These properties can be accessed via `User.PROPERTY` e.g. `macusers.primary().admin`.

## Installing
You can install macusers using pip. macusers has been tested with Python 3.7 and 3.9.

```console
python3 -m pip install macusers
```
