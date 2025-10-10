import lx3_1
import lx3_2
import json

def load_data_from_file(filename):
    """
    读取 course.txt 文件并将其解析为 Python 对象
    :param filename:文件名称
    :return:Python对象
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    return data_list

def search_by_keyword(data_list, keyword):
    matching_data = []
    for data in data_list:
        if any(isinstance(value, str) and keyword in value for value in data.values()):
            matching_data.append(data)

    return matching_data

if __name__ == '__main__':
    data_list = load_data_from_file('course.txt')

    keyword = input("请输入要搜索的关键字：")

    results = search_by_keyword(data_list, keyword)

    print(f"共找到{len(results)}条数据：")
    for result in results:
        print(result)