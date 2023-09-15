import json
import os


def find_missing_directories(dir1, dir2):
    missing_dirs = []

    for child1 in dir1 if type(dir1) is list else dir1['children']:
        found = False
        for child2 in dir2 if type(dir2) is list else dir2['children']:
            if child1['name'] == child2['name']:
                found = True
                missing_dirs.extend(find_missing_directories(child1, child2))
                break
        if not found:
            missing_dirs.append(child1['name'])
    return missing_dirs


def main():
    files = os.listdir("comparator")
    datas = []
    for i in sorted(files):
        print(f'loading file : {i}')
        with open(f'comparator/{i}', 'r') as f:
            datas.append(json.load(f))
    first_dir = datas.pop(0)
    for i in datas:
        missing_directories = find_missing_directories(first_dir, i)
        if missing_directories:
            print("Missing directories:")
            for dir_name in missing_directories:
                print(dir_name)
        else:
            print("No missing directories found.")


main()