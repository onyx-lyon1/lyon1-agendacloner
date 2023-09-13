import time
import copy
from os import mkdir

from dotenv import dotenv_values
import requests
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from os.path import exists
import jsonpickle
import re


def get_magic_auth_code(driver):
    driver.get(
        "https://adelb.univ-lyon1.fr/direct/index.jsp?projectId=3&ShowPianoWeeks=true&days=2")
    driver.find_element(By.ID, "username").click()
    driver.find_element(By.ID, "username").send_keys(
        dotenv_values(".env")["USERNAME"])
    driver.find_element(By.ID, "password").click()
    driver.find_element(By.ID, "password").send_keys(
        dotenv_values(".env")["PASSWORD"])
    driver.find_element(By.NAME, "submit").click()
    input("press enter when the connection is completed")
    for request in driver.requests:
        if "|" in str(request.body):
            tab = str(request.body).split("|")
            for t in tab:
                # check that it is 7 characters long and that there is no special characters
                if len(t) == 7:
                    return t
    return str(driver.last_request.body).split("|")[-3]


class Dir:
    def __init__(self, name="", children=None, identifier=-1, opened=False):
        self.children = []
        self.children = children
        self.name = name
        self.identifier = identifier
        self.opened = opened

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class SmallDir:
    def __init__(self, name="", children=None, identifier=-1):
        if children is None:
            children = []
        self.children = children
        self.name = name
        self.identifier = identifier

    def from_dir(self, directory):
        # function to import data from a Dir object
        self.name = directory.name
        self.identifier = directory.identifier
        for child in directory.children:
            self.children.append(copy.deepcopy(SmallDir().from_dir(child)))
        return self


def request_to_dirs(raw_data, root=False, parent_name=""):
    # fields = raw_data.split("{")
    fields = re.findall(r'(\{\\"\d+\\".*?)(?=\{\\"\d|$)', raw_data)
    fields = fields[2 if not root else 1:]
    tmp_dirs = []
    for field in fields:
        subfields = field.split("\\\"")
        if len(subfields) > 3:
            if parent_name != "":
                name = parent_name + "." + subfields[subfields.index('LabelName') + 2]  # subfields[35]
            else:
                name = subfields[subfields.index('LabelName') + 2]  # subfields[35]
            # id= check after
            children = None if subfields[3] == 'false' else []
            identifier = subfields[1]
            tmp_dirs.append(Dir(name=name, children=children, identifier=identifier))
    return tmp_dirs


def dir_to_request(auth_code, dir_name, dir_id, depth, root):
    begin = '7|0|20|https://adelb.univ-lyon1.fr/direct/gwtdirectplanning/|067818807965393FC5DCF6AECC2CA8EC|com' \
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
    'Referer': 'https://adelb.univ-lyon1.fr/direct/index.jsp?projectId=3&ShowPianoWeeks=true&days=0&ticket=ST-3100507'
               '-cRkd5pGuT37xEZrFrNkK-cas.univ-lyon1.fr',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


def get_everyone(parent, root_name, session, request_headers, magic_auth_code, depth=0):
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
            headers=request_headers
        )
        tmpdirs = request_to_dirs(
            raw_data=response.text, parent_name="" if depth == 0 else parent.name)
        if tmpdirs:
            tmpdirs.pop(0)
        with open(f"data/{root_name}/{parent.name.replace('/', '_slash_')}.json", "w") as file:
            file.write(jsonpickle.encode(tmpdirs))
    if not parent.opened:
        for dir_index in range(len(tmpdirs)):
            tmpdirs[dir_index].children.extend(copy.deepcopy(
                get_everyone(tmpdirs[dir_index], root_name=root_name, depth=depth + 1, magic_auth_code=magic_auth_code,
                             session=session, request_headers=request_headers)))
            tmpdirs[dir_index].opened = True
        parent.opened = True
        print(f"data/{root_name}/{parent.name.replace('/', '_slash_')}.json")
        with open(f"data/{root_name}/{parent.name.replace('/', '_slash_')}.json", "w") as file:
            file.write(jsonpickle.encode(tmpdirs))
    return tmpdirs


def main():  # sourcery skip: for-index-replacement, remove-zero-from-range
    driver = webdriver.Firefox()
    magic_auth_code = get_magic_auth_code(driver)
    session = requests.Session()
    for cookie in driver.get_cookies():
        print(cookie["name"], cookie["value"])
        if cookie["name"] == "JSESSIONID":
            session.cookies.set(cookie["name"], cookie["value"])
    driver.quit()

    dirs = [
        Dir(name="trainee", id=-1),
        Dir(name="instructor", id=-2),
        Dir(name="classroom", id=-3),
        Dir(name="equipment", id=-4),
        Dir(name="category5", id=-5),
        Dir(name="category6", id=-6),
        Dir(name="category7", id=-7),
        Dir(name="category8", id=-8)
    ]

    if not exists("data"):
        mkdir("data")

    for i in range(0, len(dirs)):
        print(f"Getting {dirs[i].name}")
        if not exists(f"data/{dirs[i].name}"):
            mkdir(f"data/{dirs[i].name}")
        dirs[i].children.extend(copy.deepcopy(
            get_everyone(parent=dirs[i], root_name=dirs[i].name, depth=0, magic_auth_code=magic_auth_code,
                         session=session, request_headers=headers)))
        dirs[i].opened = True
        with open(f"data/{dirs[i].name.replace('/', '_slash_')}.json", "w") as f:
            f.write(jsonpickle.encode(dirs[i]))

    real_name = [
        "Etudiants (groupes)",
        "Enseignants",
        "Salles",
        "Assiduité",
        "Séquences",
        "Categorie6",
        "Categorie7",
        "Categorie8"
    ]
    with open('data/agenda_main.json', 'w') as f:
        final_dirs = []
        for directory in range(len(dirs)):
            print("cleaning", dirs[directory].name)
            final_dirs.append(copy.deepcopy(
                SmallDir().from_dir(dirs[directory])))
            final_dirs[directory].name = real_name[directory]
        print("writing final file : agenda_main.json")
        f.write(jsonpickle.encode(final_dirs, unpicklable=False, make_refs=False))


main()
