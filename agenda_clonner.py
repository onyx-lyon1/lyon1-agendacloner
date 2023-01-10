import json
import time
import copy
from os import mkdir

from dotenv import dotenv_values
import requests
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from os.path import exists
import jsonpickle


def get_magic_auth_code():
    global driver
    driver.get(
        "https://adelb.univ-lyon1.fr/direct/index.jsp?projectId=2&ShowPianoWeeks=true&days=0")
    driver.find_element(By.ID, "username").click()
    driver.find_element(By.ID, "username").send_keys(
        dotenv_values(".env")["USERNAME"])
    driver.find_element(By.ID, "password").click()
    driver.find_element(By.ID, "password").send_keys(
        dotenv_values(".env")["PASSWORD"])
    driver.find_element(By.NAME, "submit").click()
    time.sleep(3)
    for request in driver.requests:
        if "YW" in str(request.body) and "|" in str(request.body):
            tab = str(request.body).split("|")
            for t in tab:
                if "YW" in t:
                    return t
    print(driver.last_request)
    return str(driver.last_request.body).split("|")[-3]


class Dir:
    def __init__(self, name="", children=None, id=-1, opened=False):
        self.children = []
        if children is not None:
            self.children = children
        self.name = name
        self.id = id
        self.opened = opened

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


def request_to_dirs(raw_data, root=False, parent_name=""):
    fields = raw_data.split("{")
    fields = fields[3:]
    tmp_dirs = []
    names = []
    ids = []
    for field in fields:
        subfields = field.split("\\\"")
        if (
                subfields[1] == "StringField"
                and subfields[3] == "NAME"
                and subfields[5] == "LabelName"
        ):
            if parent_name != "" and field != fields[0]:
                names.append(f"{parent_name}.{subfields[7]}")
            else:
                names.append(subfields[7])
        elif subfields[1] != "ColorField":
            ids.append(0 if subfields[1] == "" else int(subfields[1]))
    if not root and names:
        tmp_dirs.append(Dir(name=names.pop(0)))
    tmp_dirs.extend(
        Dir(name=names[name_id], id=ids[name_id])
        for name_id in range(len(names))
        if name_id < len(ids)
    )
    return tmp_dirs


def dir_to_request(auth_code, dir_name, dir_id, depth, root):
    begin = '7|0|20|https://adelb.univ-lyon1.fr/direct/gwtdirectplanning/|D299C8C3CA21CA5E6AFCED14CFFB2A29|com' \
            '.adesoft.gwt.directplan.client.rpc.DirectPlanningServiceProxy|method4getChildren|J|java.lang.String' \
            '/2004016611|com.adesoft.gwt.directplan.client.ui.tree.TreeResourceConfig/2234901663|{"'
    end = f'[0][0]|[I/2970817851|java.util.LinkedHashMap/3008245022|COLOR|com.adesoft.gwt.core.client.rpc.config' \
          f'.OutputField/870745015|LabelColor||com.adesoft.gwt.core.client.rpc.config.FieldType/1797283245|NAME' \
          f'|LabelName|java.util.ArrayList/4159755760|com.extjs.gxt.ui.client.data.SortInfo/1143517771|com.extjs.gxt' \
          f'.ui.client.Style$SortDir/3873584144|1|2|3|4|3|5|6|7|' \
          f'{auth_code}|8|7|0|9|2|-1|-1|10|0|2|6|11|12|0|13|11|14|15|11|0|0|6|16|12|0|17|16|14|15|4|0|0|18|0|18|0|19' \
          f'|20|1|16|18|0|'
    return f'{begin}{str(dir_id)}""true""{str(depth)}""-1""0""0""0""false"[1]{"{"}"StringField""NAME""LabelName""' \
           f'{dir_name.split(".")[-1]}""false""false""{("" if depth == 0 else dir_name)}""{root}""1""0"{end}'


def obj_to_dict(obj):
    return obj if obj is list else obj.__dict__


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Accept': '*/*',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Content-Type': 'text/x-gwt-rpc; charset=utf-8',
    'X-GWT-Permutation': '7F5A0F77AAF986456BB12F64AF900F31',
    'X-GWT-Module-Base': 'https://adelb.univ-lyon1.fr/direct/gwtdirectplanning/',
    'Origin': 'https://adelb.univ-lyon1.fr',
    'Connection': 'keep-alive',
    'Referer': 'https://adelb.univ-lyon1.fr/direct/index.jsp?projectId=2&ShowPianoWeeks=true&days=0&ticket=ST-3100507'
               '-cRkd5pGuT37xEZrFrNkK-cas.univ-lyon1.fr',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


def get_everyone(parent, root_name, depth=0):
    global headers
    global session
    global magic_auth_code
    if exists(f"data/{root_name}/{parent.name.replace('/', '_slash_')}.json"):
        with open(f"data/{root_name}/{parent.name.replace('/', '_slash_')}.json", "r") as file:
            file_string = "".join(file)
            tmpdirs = jsonpickle.decode(file_string)
    else:
        response = session.post(
            'https://adelb.univ-lyon1.fr/direct/gwtdirectplanning/DirectPlanningServiceProxy',
            data=dir_to_request(
                auth_code=magic_auth_code, dir_name=parent.name, dir_id=parent.id, depth=depth,
                root=root_name).encode('utf-8'),
            cookies=session.cookies,
            headers=headers,

        )
        tmpdirs = request_to_dirs(raw_data=response.text, parent_name="" if depth == 0 else parent.name)
        if tmpdirs:
            tmpdirs.pop(0)
        with open(f"data/{root_name}/{parent.name.replace('/', '_slash_')}.json", "w") as file:
            file.write(jsonpickle.encode(tmpdirs))
    if not parent.opened:
        for dir_index in range(len(tmpdirs)):
            tmpdirs[dir_index].children.extend(copy.deepcopy(get_everyone(tmpdirs[dir_index], root_name, depth + 1)))
            tmpdirs[dir_index].opened = True
        parent.opened = True
        print(f"data/{root_name}/{parent.name.replace('/', '_slash_')}.json")
        with open(f"data/{root_name}/{parent.name.replace('/', '_slash_')}.json", "w") as file:
            file.write(jsonpickle.encode(tmpdirs))
    return tmpdirs


driver = webdriver.Firefox()
magic_auth_code = get_magic_auth_code()
session = requests.Session()
for cookie in driver.get_cookies():
    print(cookie["name"], cookie["value"])
    session.cookies.set(cookie["name"], cookie["value"])
driver.quit()

dirs = [
    Dir(name="trainee", id=-1),
    Dir(name="instructor", id=-2),
    Dir(name="classroom", id=-3),
    Dir(name="equipment", id=-4),
    Dir(name="category5", id=-5)
]

if not exists("data"):
    mkdir("data")

for i in range(0, len(dirs)):
    print(f"Getting {dirs[i].name}")
    if not exists(f"data/{dirs[i].name}"):
        mkdir(f"data/{dirs[i].name}")
    dirs[i].children.extend(copy.deepcopy(get_everyone(dirs[i], dirs[i].name)))
    dirs[i].opened = True
    with open(f"data/{dirs[i].name.replace('/', '_slash_')}.json", "w") as f:
        f.write(jsonpickle.encode(dirs[i]))

real_name = [
    "Etudiant (groupes)",
    "Enseignants",
    "Salles",
    "Etudiants (individus)",
    "Séquences"
]
with open('data/agenda_main.json', 'w') as f:
    final_dirs = []
    for directory in range(len(dirs)):
        with open(f"data/{dirs[directory].name.replace('/', '_slash_')}.json", "r") as f_dir:
            final_dirs.append(dirs[directory])
            final_dirs[directory].name = real_name[directory]
            string = "".join(f_dir)
            dirs[directory].children.extend(copy.deepcopy(jsonpickle.decode(string)))
    f.write(json.dumps(final_dirs, default=obj_to_dict))
