import json


def svp2json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        # 读取并替换JSON布尔值
        content = f.read().replace("true", "True").replace("false", "False")

    try:
        # 使用`eval`解析Python字典格式
        data = eval(content)
        formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
        # 写入格式化后的JSON数据到文件
        with open(file_path.replace(".svp", ".json"), "w", encoding="utf-8") as f:
            f.write(formatted_data)
    except Exception as e:
        print(f"解析文件时出错: {e}")

    try:
        data = eval(content[:-1])
        formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
        with open(file_path.replace(".svp", ".json"), "w", encoding="utf-8") as f:
            f.write(formatted_data)
    except Exception as e:
        print(f"解析文件时出错: {e}")


if __name__ == "__main__":
    svp2json(r".\test.svp")
