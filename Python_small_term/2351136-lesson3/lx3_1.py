import xlrd
import json

workbook = xlrd.open_workbook('score.xls')

def read_xls(sh):
    sheet = workbook.sheet_by_index(sh)
    title = sheet.row_values(0)
    data = [sheet.row_values(i) for i in range(1, sheet.nrows)]
    return title, data

def merge_score_dict(student_no, list_1, title1):
    """
       :param student_no: 输入一个学生的学号
       :return: 返回这个学生的成绩，且剔除不存在的成绩
       """

    score_list = []
    for row in list_1:
        if student_no == row[0]:
            score_dict = {}
            for idx, value in enumerate(row):
                if value != '':
                    score_dict[title1[idx]] = value
            score_list.append(score_dict)
    return score_list

def merge_data_list(list_1, title1, list_2, title2):
    """
        这个函数是将所有数据拼接到一个list下
        :return: data_list
        """

    data_list = []
    for row in list_2:
        data_dict = {}
        for idx, value in enumerate(row):
            if value != '':
                data_dict[title2[idx]] = value
        student_no = row[0]
        data_dict['score'] = merge_score_dict(student_no, list_1, title1)
        data_list.append(data_dict)
    return data_list

if __name__ == '__main__':
    title1, list_1 = read_xls(0)
    title2, list_2 = read_xls(1)

    data_list = merge_data_list(list_1, title1, list_2, title2)

    with open('course.txt', 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)