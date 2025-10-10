import lx3_1
import json

def find_score(student_no, course_name, data_list):
    """
              输入学号和课程名称，返回这个人的成绩
              :param student_no: 学号
              :param course_name: 课程名称
              :param data_list: 数据列表
              :return: 成绩的有效性和结果字典
              """
    valid = False  # 用于判断是否存在
    result = {}
    for student in data_list:
        if student['学号'] == student_no:
            result['学号'] = student['学号']
            result['姓名'] = student['姓名']
            result['英文姓名'] = student['英文姓名']
            result['性别'] = student['性别']
            result['score'] = []
            for score in student['score']:
                if course_name in score:
                    valid = True  # 表示已经找到
                    result['score'].append({
                        '学期': score['学期'],
                        course_name: score[course_name]
                    })

    return valid,result


if __name__ == '__main__':
    title1, list_1 = lx3_1.read_xls(0)
    title2, list_2 = lx3_1.read_xls(1)

    data_list = lx3_1.merge_data_list(list_1, title1, list_2, title2)

    with open('course.txt', 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

    # 输入学号和课程名
    student_no = input("请输入学号：")
    course_name = input("请输入课程名称：")

    # 查找并输出成绩
    valid,result = find_score(student_no, course_name, data_list)

    if valid:
        print(result)
    else:
        print(f"该学号对应的 {course_name} 成绩没找到")