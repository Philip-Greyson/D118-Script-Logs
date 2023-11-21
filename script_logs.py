import os


if __name__ == '__main__': # main file execution
    with open('warnings.txt','w') as warnings:
        with open('errors.txt','w') as errors:
            currentDir = os.getcwd() # get the current scripts direcotry
            parentDir = "" # reset parentDir to blank
            dirParts = currentDir.split("\\")
            for i in range(len(dirParts)-1): # go through as many parts as there are -1 to get the full path except the current actual directory, which results in our parent directory
                parentDir = parentDir + dirParts[i] + "\\" # append each part together replacing the \ to generate the parent directory

            entries = os.listdir(parentDir) # find all objects in this parent directory
            allDirectories = []
            for entry in entries:
                if os.path.isdir(parentDir + entry): # check to see if the entry is a directory or not, only continue if so
                    allDirectories.append(parentDir + entry)
            print(currentDir)
            print(parentDir)
            # print(entries)
            for directory in allDirectories:
                # print(f'Found directory {directory} in parent directory')
                entries = os.listdir(directory) # find all objects in the target directory
                for entry in entries:
                    if "log" in entry.lower() and entry != "script_logs.py": # look for files that have log in their name, case insensitive, but ignore this script
                        logFile = directory + "\\" + entry
                        print(f'Found file {logFile} in {directory}')
                        with open(logFile,'r') as readFile:
                            for line in readFile:
                                if "ERROR" in line:
                                    print(line.strip(), file=errors) # strip the newline character off the end and output it
                                if "WARN" in line:
                                    print(line.strip(), file=warnings)