#####################################################################################################
PROGRAM = "pyResticBK.py"
#  Author: Alessandro Carichini 
#    Date: 03-05-2024
VERSION = "1.2405b"
#    Note: Automate restic backup using a config file
#
#  params: backup = backups all files to repositories listed into config file
#          status = check integrity and shows all id snapshots
#          clean = set policy retention, for example:
#                  --keep-daily 10 --keep-weekly 4 --keep-monthly 6
#####################################################################################################
#

import os
import sys
import platform
import subprocess
import csv
import shlex

def ResticExec(restic_bin, path_src, path_repo, param_string):
    command_list = shlex.split(param_string)

    if command_list[0] == "backup":
        command = [restic_bin, "-r", path_repo, "-q", "backup", path_src ]
    else:
        command = [restic_bin, "-r", path_repo ]
        command.extend(command_list)

    try:
        result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if command_list[0] == "backup":
            return True
        else:
            return result.stdout
    except subprocess.CalledProcessError as e:
        if command_list[0] == "backup":
            return False
        else:
            print("Error:", e.stderr)
            return None

#####################################################################################################

config_dict = {}

if len(sys.argv) < 3:
    print(f"Usage: {PROGRAM} file_config backup|status|clean")
    sys.exit(1)
else:
    FILE_CONFIG = sys.argv[1]
    PARAM = sys.argv[2].upper()
    OS = platform.system()

    print(f"{PROGRAM}: {PARAM} - Platform: {OS} - rel.{VERSION}")
    print(f"reading: {FILE_CONFIG}")

    if os.path.isfile(FILE_CONFIG):
        with open(FILE_CONFIG, newline='', encoding='utf-8', ) as csvfile:
            reader = csv.reader(csvfile,delimiter=";")
            for row in reader:
                if row:  
                    if row[0][0] != '#':
                        if row[0].strip().lower() == "config":
                            key_value = row[1].split('=')
                            if len(key_value) == 2:
                                key, value = key_value
                                config_dict[key.strip()] = value.strip().lower()
                        else:
                            PATH_SRC = row[0]
                            PATH_REPO = row[1]
                            try:
                                RETENTION = row[2]
                            except:
                                RETENTION = None

                            if OS == "Windows":
                                RESTIC_EXE = config_dict["restic_win"]
                                SLASH = "\\"
                            else:
                                RESTIC_EXE = config_dict["restic_linux"]
                                SLASH = "/"

                            print(f"REPO: {PATH_REPO}")
                            
                            if not os.path.isfile(PATH_REPO+SLASH+"config"):
                                if os.path.isdir(PATH_SRC):
                                    print(f"INIT REPO {PATH_REPO}")
                                    result = ResticExec(RESTIC_EXE,PATH_SRC,PATH_REPO,"init")
                                    print(result)
                                else:
                                    print(f"NO SOURCE {PATH_SRC}")

                            if PARAM == 'BACKUP':
                                if os.path.isfile(PATH_REPO+SLASH+"config"):
                                    result = ResticExec(RESTIC_EXE,PATH_SRC,PATH_REPO,"backup")
                                    if result:
                                        print(f"OK BACKUP {PATH_SRC}")
                                    else:
                                        print(f"ERROR! BACKUP {PATH_SRC}")
                            elif PARAM == 'STATUS':
                                if os.path.isfile(PATH_REPO+SLASH+"config"):
                                    result1 = ResticExec(RESTIC_EXE,PATH_SRC,PATH_REPO,"snapshots")
                                    result2 = ResticExec(RESTIC_EXE,PATH_SRC,PATH_REPO,"stats")
                                    print(result1)
                                    print(result2)
                            elif PARAM == 'CLEAN':
                                if RETENTION:
                                    if os.path.isfile(PATH_REPO+SLASH+"config"):
                                        result = ResticExec(RESTIC_EXE,PATH_SRC,PATH_REPO,"forget "+RETENTION+" --prune")
                                        print(result)

    else:
        print(f"Config file {FILE_CONFIG} not found!")
