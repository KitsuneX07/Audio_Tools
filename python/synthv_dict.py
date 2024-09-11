"""
synthesizerV词典相关
"""

import os, json, re


def dump_txt(file_path, data):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if len(line.strip().split(" ")) == 2:
            raw, new = line.strip().split(" ")
            data[raw] = new


def dump_folder(folder_path):
    data = {}
    for file in os.listdir(folder_path):
        if file.endswith(".txt") and file.startswith("japanese"):
            dump_txt(os.path.join(folder_path, file), data)

    with open(os.path.join(folder_path, "sythv_dict.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def trans_dict(svp_path):
    with open(".\\data\\sythv_dict.json", "r", encoding="utf-8") as f:
        dict = json.load(f)
    with open(svp_path, "r", encoding="utf-8") as f:
        content = f.read()
        content = content.encode("utf-8").decode("unicode-escape")
        # print(content)

        for key in dict:
            content = content.replace(key, dict[key])
            print("replace", key, "with", dict[key])
            # print(content)

    with open(svp_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    trans_dict(r"D:\projects\python\diffsinger\sv_datasets\svp\8_だれかの心臓になれたなら.svp")
