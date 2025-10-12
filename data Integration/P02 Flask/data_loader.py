import os

def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"文件{file_path}不存在")
        return []


    """读取book.txt文件并返回结构化的书籍数据"""
    books = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        # 跳过表头和空行
        for line in lines[1:]:  # 从第2行开始（跳过表头）
            
            line = line.strip()
            columns = line.split()
            
            if len(columns) >= 3:
                # 提取序号
                index = columns[0]
                # 提取分类（最后一个元素）
                category = columns[-1]
                # 提取书名（中间部分）
                book_name = ' '.join(columns[1:-1])
                
                books.append({
                    'index': index,
                    'name': book_name,
                    'category': category
                })

    return books


if __name__ == '__main__':
    file_path = 'book.txt'
    books = load_data(file_path)
    print(books)