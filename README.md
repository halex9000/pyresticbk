# pyResticBK
Python script to automate Restic Backup 

## pyResticBK.py
Download 
[Restic](https://restic.net/ )

Usage:
python pyResticBK.py file_config action

actions:
  - backup
  - status
  - clean


## file_config
plain text csv example:

```
# config_file format
#
# path_source[0];path_dest[1];retention[2]
#
# Config Section
config;restic_win=c:\bin\restic.exe
config;restic_linux=/usr/bin/restic
config;password=ENV_RESTIC_PASSWORD
# Repository Section
c:\\users\\halex;s:\\restic_bak\\halex;--keep-daily 7 --keep-weekly 4 --keep-monthly 1
c:\\laragon;s:\\restic_bak\\laragon;--keep-daily 7 --keep-weekly 4 --keep-monthly 1

```

ENV_RESTIC_PASSWORD use environment RESTIC_PASSWORD

Examples: 

### Start backup all lines inside myfile_config

```
python pyResticBK.py myfile_config backup
```
### Show snapshots and stats for all repository inside myfile_config

```
python pyResticBK.py myfile_config status
```
### Clean repository using retention policy inside myfile_config

```
python pyResticBK.py myfile_config clean
```

```
