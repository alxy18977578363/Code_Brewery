import lx2_1

"""   编写内容简介：
- table_merge()函数,将sheet1和2合并，只能出现一列学号
"""

# 下面的函数用于将两个表格的数据合并
def table_merge(list_1,list_2):
    merge_data=[]

    for row_2 in list_2:
        xuehao=row_2[0]
        found=False         # 设立一个bool，如果找到相同学号则为true

        for row_1 in list_1:
            if row_1[0] == xuehao:  # 如果找到相同的学号
                # 合并数据，这里假设其他列的数据可以直接相加或者合并
                merged_row = row_2 + row_1[1:]  # 将sheet1和sheet2的数据合并，注意去掉学号列
                merge_data.append(merged_row)
                found = True
                break  # 找到相同学号的记录，跳出循环

    if not found:
        # 如果在sheet1中没有找到相同学号的记录，则直接添加sheet2的数据行到merge_data
        merge_data.append(row_2)

    return merge_data


# 测试程序
if __name__=='__main__':
    title1,list_1=lx2_1.read_xls(0)
    title2,list_2=lx2_1.read_xls(1)

    data=table_merge(list_1,list_2)
    for e in data:
        print(e)

