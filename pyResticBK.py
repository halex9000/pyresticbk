#####################################################################################################
PROGRAM = "pyResticBK.py"
#  Author: Alessandro Carichini 
#    Date: 02-05-2024
#  Update: 06-05-2024
VERSION = "1.2405_10a"
#    Note: Automate restic backup using a config file
#
#  params: backup = Start backup all lines inside myfile_config
#          status = Show snapshots and stats for all repository inside myfile_config
#          clean =  Clean repository using retention policy inside myfile_config. Example:
#                  --keep-daily 10 --keep-weekly 4 --keep-monthly 6
#####################################################################################################
#    Todo: 
#       - Send file log to email
#       - Check Repository disk space 
#       - Check Integrity Repository 
#####################################################################################################
# restic usage:
#
# restic -r /path_repo init
# restic -r /path_repo backup /path_source  
# restic -r /path_repo stats 
# 
#####################################################################################################
#

import os
import sys
import platform
import subprocess
import csv
import shlex
import json
from datetime import datetime

#####################################################################################################
def WriteLogFile(filename,buffer=None):
    date_obj = datetime.now()
    log_date = date_obj.strftime("%Y-%m-%d %H:%M.%S")
    if buffer is None:
        fhandle = open(filename, 'a')
        return fhandle
    else:
        filename.write(f"{log_date};{buffer}\n")
        return None

def ResticExec(restic_bin, path_src, path_repo, param_string):
    command_list = shlex.split(param_string)

    if command_list[0] == "backup":
        command = [restic_bin, '-r', path_repo, '-q', 'backup', path_src ]
    else:
        command = [restic_bin, '-r', path_repo ]
        command.extend(command_list)

    try:
        result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return "error: "+e.stderr

def GetDirSize(directory):
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            fp = os.path.join(dirpath, filename)
            try:
                total_size += os.stat(fp).st_size
            except:
                total_size += 0
                
    return total_size / (1024 ** 3)

#####################################################################################################

config_dict = {}

if len(sys.argv) < 3:
    print(f"Usage: {PROGRAM} file_config backup|status|clean")
    sys.exit(1)
else:
    date_obj = datetime.now()
    log_date = date_obj.strftime("%Y%m%d")
    FILE_CONFIG = sys.argv[1]
    FILE_LOG = log_date+"_"+os.path.splitext(os.path.basename(FILE_CONFIG))[0]+".log"
    PARAM = sys.argv[2].upper()
    OS = platform.system()

    print(f"{PROGRAM}: {PARAM} - Platform: {OS} - rel.{VERSION}")
    print(f"reading: {FILE_CONFIG}")

    # Create log file
    flog = WriteLogFile(FILE_LOG)

    if os.path.isfile(FILE_CONFIG):
        with open(FILE_CONFIG, newline='', encoding='utf-8', ) as csvfile:
            reader = csv.reader(csvfile,delimiter=";")
            for row in reader:
                if row:  
                    # Skip comments #
                    if row[0][0] != '#':
                        # Get config vars
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

                            # Check Platform
                            if OS == "Windows":
                                RESTIC_EXE = config_dict["restic_win"]
                            else:
                                RESTIC_EXE = config_dict["restic_linux"]

                            head_log = f"{PARAM};{PATH_REPO}"

                            print(f"working: {PARAM} into {PATH_REPO}")
                            
                            file_repo_config = os.path.join(PATH_REPO,"config")
                            # Init Repository and check PATH_SRC exist
                            if not os.path.isfile(file_repo_config):
                                if os.path.isdir(PATH_SRC):
                                    WriteLogFile(flog,f"{head_log};INIT")
                                    result = ResticExec(RESTIC_EXE,PATH_SRC,PATH_REPO,"init")
                                else:
                                    result = f"NO SOURCE {PATH_SRC}"

                                WriteLogFile(flog,f"{head_log};{result}")

                            # Action if Repository exist
                            if os.path.isfile(file_repo_config):
                                if PARAM == 'BACKUP':
                                    result = ResticExec(RESTIC_EXE,PATH_SRC,PATH_REPO,"backup")
                                    WriteLogFile(flog,f"{head_log};{result}")
                                elif PARAM == 'STATUS':
                                    json_result = ResticExec(RESTIC_EXE,PATH_SRC,PATH_REPO,"snapshots --json")
                                    snapshots = json.loads(json_result)
                                    for snapshot in snapshots:
                                        snapshot_id = snapshot["short_id"]
                                        iso_string = snapshot["time"]
                                        iso_date = datetime.fromisoformat(iso_string[:19])
                                        snapshot_date = iso_date.strftime("%d-%m-%Y %H:%M")
                                        
                                        WriteLogFile(flog,f"{head_log};SNAPSHOT: {snapshot_id} = {snapshot_date}")

                                    size_gb = GetDirSize(PATH_REPO)
                                    WriteLogFile(flog,f"{head_log};SIZE GB: {size_gb:.2f}")
                                elif PARAM == 'CLEAN':
                                    if RETENTION:
                                        result = ResticExec(RESTIC_EXE,PATH_SRC,PATH_REPO,"forget "+RETENTION+" --prune")
                                        WriteLogFile(flog,f"{head_log};{result}")
        flog.close()
        print(f"FileLog: {FILE_LOG}")
    else:
        print(f"Config file {FILE_CONFIG} not found!")
