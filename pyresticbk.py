########################################################################################
# Program: pyresticbk.py
#  Author: Alessandro Carichini 
#    Date: 02-05-2024
# Version: 1.2405a
#    Note: Automate restic backup by config file
#
#    fasi: backup = esegue il backup da sorgente al repository di destinazione
#          status = verifica l'integrita del repository mostrando gli snapshots eseguiti
#          clean = gestione delle retention con pulizia degli snapshot più vecchi a 
#                  seconda della policy adottata, esempio:
#                  forget --keep-daily 10 --keep-weekly 4 --keep-monthly 6 --prune
########################################################################################

import os
import sys
import platform
import subprocess
import csv
import shlex

def ResticCommand(RESTIC_EXE,PATH_SRC,PATH_DST,command):
    command = [RESTIC_EXE, "-r", PATH_DST, command, PATH_SRC]
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def ResticQuery(RESTIC_EXE,PATH_DST,param_string):
    command_list = shlex.split(param_string)
    command = [RESTIC_EXE, "-r", PATH_DST ]
    
    command.extend(command_list)

    try:
        result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
        return None

config_dict = {}

if len(sys.argv) < 3:
    print("Utilizzo: pyresticbk.py file_config [backup|status|clean]")
    sys.exit(1)
else:
    FILE_CONFIG = sys.argv[1]
    PARAM = sys.argv[2].upper()

    print(f"pyresticbk {PARAM}")

    if os.path.isfile(FILE_CONFIG):
        with open(FILE_CONFIG, newline='', encoding='utf-8', ) as csvfile:
            reader = csv.reader(csvfile,delimiter=";")
            for row in reader:
                if row:  # Controlla se la riga non è vuota
                    if row[0][0] != '#':
                        if row[0].strip() == 'config':
                            key_value = row[1].split('=')
                            if len(key_value) == 2:
                                key, value = key_value
                                config_dict[key.strip()] = value.strip()
                        else:
                            PATH_SRC = row[0]
                            PATH_DST = row[1]
                            try:
                                RETENTION = row[2]
                            except:
                                RETENTION = None

                            if platform.system() == 'Windows':
                                RESTIC_EXE = config_dict["restic_win"]
                                SLASH = "\\"
                            else:
                                RESTIC_EXE = config_dict["restic_linux"]
                                SLASH = "/"

                            print(f"REPO: {PATH_DST}")
                            
                            if not os.path.isfile(PATH_DST+SLASH+"config"):
                                if os.path.isdir(PATH_SRC):
                                    print(f"INIT REPO {PATH_DST}")
                                    result = ResticQuery(RESTIC_EXE,PATH_DST,'init')
                                    print(result)
                                else:
                                    print(f"NO SOURCE {PATH_SRC}")

                            if PARAM == 'BACKUP':
                                if os.path.isfile(PATH_DST+SLASH+"config"):
                                    result = ResticCommand(RESTIC_EXE,PATH_SRC,PATH_DST,'backup')
                                    if result:
                                        print(f"OK BACKUP {PATH_SRC}")
                                    else:
                                        print(f"ERROR! BACKUP {PATH_SRC}")
                            elif PARAM == 'STATUS':
                                if os.path.isfile(PATH_DST+SLASH+"config"):
                                    result1 = ResticQuery(RESTIC_EXE,PATH_DST,'snapshots')
                                    result2 = ResticQuery(RESTIC_EXE,PATH_DST,'stats')
                                    print(result1)
                                    print(result2)
                            elif PARAM == 'CLEAN':
                                if RETENTION:
                                    if os.path.isfile(PATH_DST+SLASH+"config"):
                                        result = ResticQuery(RESTIC_EXE,PATH_DST,'forget '+RETENTION+' --prune')
                                        print(result)

    else:
        print(f"Il file {FILE_CONFIG} non esiste!")
