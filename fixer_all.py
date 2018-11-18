import os

with open('errors.txt', 'r') as errFile:
    errs = errFile.readlines()
    for err in errs:
        [path, _, _] = err.split(',')
        path = "AP_Coll_Parsed/" + path.split("/")[-1]
        with open(path, 'r') as file:
            data = file.readlines()
            i = 0
            lastLine = ""
            for line in data:
                if lastLine.startswith("<DOCNO>") and line == '</TEXT>\n':
                    print(line, i)
                    data[i] = "<TEXT></TEXT>\n"
                lastLine = line
                i += 1
            with open(path + "_fixed", 'w') as fixed:
                fixed.writelines(data)
        os.remove(path)
