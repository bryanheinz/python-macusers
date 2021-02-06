# macusers
Get the macOS console username and/or a list of local non-system users.

```python
>>> import macusers
>>> macusers.console()
'bryanheinz'
>>> macusers.users()
['root', 'bryanheinz']
>>> macusers.users(False)
['bryanheinz']
```

This module is used to get the current or last (if the system currently doesn't have any logged in users) logged in console user on macOS instead of the user running the script/program. This module can also return a list of all local non-system created users.

## Installing
You can install macusers using pip. macusers has been tested with Python 3.7 and 3.9.

```console
> python3 -m pip install macusers
```
