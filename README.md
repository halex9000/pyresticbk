# pyresticbk
Script python to automate Restic Backup

Download Restic https://restic.net/ 

python pyresticbk.py file_config action

actions:
  - backup
  - status
  - clean


# config file
plain test csv example:

config;restic_win=c:\bin\restic.exe
config;restic_linux=/usr/sbin/restic
config;password=ENV_RESTIC_PASSWORD
c:\\users\\myuser;s:\\restic_bak\\myuser;--keep-daily 7 --keep-weekly 4 --keep-monthly 1

