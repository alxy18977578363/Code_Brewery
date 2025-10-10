import xlrd   # xlrd主要是用于读取Excel表格内容

"""   编写内容简介：
- read_xls(sh)函数：约定sh表示sheet，sh=0时读sheet1，sh=1时读sheet2.约定第一行为标题，第一列为学号
"""

# 下面的函数用于将表格的数据读取出来
def read_xls(sh):
    workbook = xlrd.open_workbook('score.xls')   # 打开Excel表格读取数据
    sheet=workbook.sheet_by_index(sh)        # 根据sh选择所需的sheet
    title=sheet.row_values(0)            # 读取第一行标题

    # 读取里面的内容
    data=[]        #定义一个空的list根据表格往里塞数据
    for row in range(1,sheet.nrows):
        data.append(sheet.row_values(row))

    return title,data       # 把title和data的地址返回，以元组形式赋值

# 测试程序
if __name__=='__main__':
    sh=int(input('sh='))
    my_title,my_data=read_xls(sh)

    # 打印表格内容
    print(my_title)
    for e in my_data:     #e作为一个对象，代表了list中的一个元素
        print(e)


