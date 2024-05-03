# pyResticBK
Python script to automate Restic Backup 

## pyresticbk.py
Download 
[Restic](https://restic.net/ )

Usage:
python pyresticbk.py file_config action

actions:
  - backup
  - status
  - clean


## file_config
plain text csv example:

```
# config variables 
config;restic_win=c:\bin\restic.exe
config;restic_linux=/usr/sbin/restic
config;password=ENV_RESTIC_PASSWORD

#path_source;path_destination;retention
c:\\users\\myuser;s:\\restic_bak\\myuser;--keep-daily 7 --keep-weekly 4 --keep-monthly 1
c:\\laragon\\;s:\\restic_bak\\laragon;--keep-daily 5 --keep-weekly 4 --keep-monthly 6

```

ENV_RESTIC_PASSWORD use environment RESTIC_PASSWORD

Examples: 

### Start backup all lines inside myfile_config

```
python pyresticbk.py myfile_config backup
```
### Show snapshots and stats for all repository inside myfile_config

```
python pyresticbk.py myfile_config status
```
### Clean repository using retention policy inside myfile_config

```
python pyresticbk.py myfile_config clean
```

```
