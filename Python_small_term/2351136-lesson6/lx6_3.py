import pandas as pd

class st_lesson:
    def __init__(self):
        # 从用户输入获取学号、姓名和其他信息
        self.st_no = input("请输入学号: ")
        self.st_name = input("请输入姓名: ")
        self.st_py = input("请输入拼音姓名: ")
        self.st_sex = input("请输入性别: ")
        self.st_schedule_df = None
        self._read_schedule_from_excel()

    def _read_schedule_from_excel(self):
        file_path = 'xuanke.xls'  # Excel 文件路径
        try:
            # 读取 Excel 文件中的课表数据
            self.st_schedule_df = pd.read_excel(file_path, sheet_name='上课时间')  # 根据实际表单名称修改
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return

    def display_schedule(self):
        if self.st_schedule_df is None:
            print("没有加载到课表数据。")
            return

        # 定义列宽
        col_width = 20
        header = ["上课时间", "周一", "周二", "周三", "周四", "周五"]

        # 打印学号和姓名
        print(f"学号：{self.st_no} 姓名：{self.st_name} 的课表")
        # 打印横线
        line_length = len(header) * col_width
        print("-" * line_length)
        header_str = "".join(f"{h:<{col_width}}" for h in header)
        print(header_str)

        # 打印课表内容
        for index, row in self.st_schedule_df.iterrows():
            row_str = f"{row.iloc[0]:<{col_width}}"  # 打印时间段
            row_str += "".join(
                f"{str(item).strip() if pd.notna(item) else '':<{col_width}}" for item in row[1:])  # 打印课程信息
            print(row_str)

    def check_conflict(self):
        if self.st_schedule_df is None:
            print("没有加载到课表数据。")
            return

        # 收集时间段冲突
        conflicts = []

        # 假设第一列是时间段，后面是周一到周五
        for index, row in self.st_schedule_df.iterrows():
            time_slot = row.iloc[0]  # 使用 iloc 访问时间段
            for day in range(1, len(row)):
                if pd.notna(row.iloc[day]):  # 使用 iloc 访问其他列
                    courses = row.iloc[day].split(',')  # 假设课程之间用逗号分隔
                    if len(courses) > 1:
                        day_name = ["周一", "周二", "周三", "周四", "周五"][day - 1]
                        conflict_str = f"{day_name}{time_slot}{courses}"
                        conflicts.append(conflict_str)

        # 打印冲突情况
        if conflicts:
            # 用 '][' 连接每个冲突项
            conflicts_str = ']['.join(conflicts)
            # 添加开头的 【 和结尾的 】
            print(f"选课冲突有：[ {conflicts_str} ]")
        else:
            print(f"{self.st_name} 没有选课冲突。")

# Example usage
if __name__ == "__main__":
    student = st_lesson()
    student.display_schedule()
    student.check_conflict()
