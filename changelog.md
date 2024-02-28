# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.0.0 -

### Added

- `User()` class which contains user details
- `primary()` function to supersede `console()`
- `admins()` function to return a list of admin `User()`
- `group_member()` function to check if a user is in a group
- `fv_status()` function to check if a user has FileVault access
- `apfs_owner()` function to check if a user is an APFS volume owner
- `secure_token_status()` function to check if the user has a secure token
- `users()` function can now filter by primary group IDs
- This changelog

### Changed

- `users()` now finds users by finding users with a shell
- `users()` now returns a list of User class
- Deprecated `console()` function, use `primary()`.username for similar functionality

### Fixed

- `users()` now returns more than just "root"

## v0.0.3 - 2021-02-05

Initial release
