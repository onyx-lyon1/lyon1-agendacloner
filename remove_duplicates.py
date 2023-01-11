import collections
import copy
import json



files = [
    'trainee.json',
    'equipment.json',
    'instructor.json',
    'classroom.json',
    'category5.json',
    'agenda_main.json'

]

def clean_duplicate(dirs):
    if type(dirs) is not list:
        copied = dirs
        copied['children'] = clean_duplicate(copy.deepcopy(copied['children']))
    else:
        count={}
        for dir in dirs:
            count[str(dir["id"])] = count.get(str(dir["id"]), 0) + 1
        copied = []
        for dir in dirs:
            if count[str(dir["id"])] > 1:
                count[str(dir["id"])] -= 1
            else:
                copied.append(copy.deepcopy(dir))
        for dir in range(len(copied)):
            copied[dir]['children'] = clean_duplicate(copy.deepcopy(copied[dir]['children']))
    return copied


for file in files:
    print(file)
    with open(f'data/{file}', 'r') as f:
        data = json.load(f)
    clean_data = clean_duplicate(data)
    with open(f'data/{file}', 'w') as f:
        json.dump(clean_data, f)
