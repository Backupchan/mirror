# Backup-chan Mirror

This is the mirror software for Backup-chan, which mirrors backups from a main Backup-chan instance.

## How it works

A mirror is configured to mirror backups from the main server. It has a list of targets to mirror.
A mirroring operation is performed on a set interval and on startup. For every backup it wants to
mirror, it performs these steps:

1. If both the mirror and the server have a backup, the mirror assumes it is unchanged.
2. If the server has a backup, but the mirror does not, the mirror downloads the backup.
3. If the mirror has a backup, but the server does not or lists it as recycled, the mirror deletes the backup.

Shrimple as that.

## Installing

Before setting up a mirror, make sure you've got a [server](https://github.com/Backupchan/server) that the mirror can access.

1. Clone the repository
   ```bash
   git clone https://github.com/Backupchan/mirror backupchan-mirror
   ```
1. Install needed dependencies
   ```bash
   pip install -r requirements.txt
   ```
1. Inside the `backupchan-mirror` directory, there are two example configuration files: `config.jsonc.example` and `targets.jsonc.example`. Copy both as `config.jsonc` and `targets.jsonc` respectively.
1. Inside `config.jsonc`, configure connection and download path according to your setup.
1. Configure `targets.jsonc` with target IDs to mirror.
1. Run the server by running `main.py`. If all went well, it should start mirroring backups shortly.
