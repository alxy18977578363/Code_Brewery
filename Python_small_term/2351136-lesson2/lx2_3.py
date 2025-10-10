import lx2_1
import lx2_2
"""   编写内容简介：
- query_by_no(studenet_no)函数,要求使用自己的学号，返回结果要求构造为字典格式。
"""

def query_by_no(student_no):
    title1, list_1 = lx2_1.read_xls(0)
    title2, list_2 = lx2_1.read_xls(1)    # 读取数据

    my_data=lx2_2.table_merge(list_1,list_2)    #拼接数据
    merge_data=title2+title1[1:]

    for row in my_data:
        if student_no==row[0]:
           result={
               merge_data[0]: row[0],
               merge_data[1]: row[1],
               merge_data[2]: row[2],
               merge_data[3]: row[3],
               merge_data[4]: row[4],
               merge_data[5]: row[5],
               merge_data[6]: row[6],
               merge_data[7]: row[7],
               merge_data[8]: row[8],
               merge_data[9]: row[9]
           }
           break

    return result       # 返回列表

if __name__=='__main__':
    student_no=str(input('student_no='))
    my_result=query_by_no(student_no)

    print(my_result)

