import json

def save(base):
    with open(r"../base/userbase.json", "w") as file:
        json.dump(base, file)

def registrate(base, id, name):
    id = id
    base["id"].append(id)
    base["root"].append(False)
    base["bool_actions"].append([False, False, False, False, False, False, False, False])
    base["spam"]["token"].append([])
    base["spam"]["time"].append(1)
    base["warning"]["token"].append([])
    base["warning"]["limit"].append([])
    if id > 0:
        base["name"].append(name)
    elif id < 0:
        base["name"].append(name)

    print("Successful registration")
    return base



with open(r"../base/userbase.json", "r") as file:
    base = json.load(file)
id_list = [-4118466751, 576978144]
name_list = ["Маркус", "haoking322"]

for i in range(len(id_list)):
    base = registrate(base, id_list[i], name_list[i])
save(base)