import copy
import json
import os

files = [
    'agenda_main.json',
    'trainee.json',
    'equipment.json',
    'instructor.json',
    'classroom.json',
    'category5.json',
    'category6.json',
    'category7.json',
    'category8.json',
]

dirs = [
    'category8',
    'category7',
    'category6',
    'category5',
    'classroom',
    'equipment',
    'instructor',
    'trainee'
]


def clean_duplicate(directories):
    if type(directories) is not list:
        copied = directories
        copied['children'] = clean_duplicate(copy.deepcopy(copied['children']))
    else:
        count = {}
        for directory in directories:
            count[str(directory["id"])] = count.get(str(directory["id"]), 0) + 1
        copied = []
        for directory in directories:
            if count[str(directory["id"])] > 1:
                count[str(directory["id"])] -= 1
            else:
                copied.append(copy.deepcopy(directory))
        for item in copied:
            item['children'] = clean_duplicate(copy.deepcopy(item['children']))
    return copied


for dir in dirs:
    subFiles = os.listdir(f'data/{dir}')
    for file in subFiles:
        print(file)
        with open(f'data/{dir}/{file}', 'r') as f:
            data = json.load(f)
        clean_data = clean_duplicate(data)
        with open(f'data/{dir}/{file}', 'w') as f:
            json.dump(clean_data, f)

for file in files:
    print(file)
    with open(f'data/{file}', 'r') as f:
        data = json.load(f)
    clean_data = clean_duplicate(data)
    with open(f'data/{file}', 'w') as f:
        json.dump(clean_data, f)
