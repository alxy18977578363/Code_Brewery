#!/usr/bin/env python3
"""
合并英文和中文论文PDF
Merge English and Chinese paper PDFs
"""

import os

def merge_pdfs():
    """合并PDF文件"""
    # 尝试导入PyPDF2
    try:
        try:
            from PyPDF2 import PdfMerger
        except ImportError:
            from PyPDF2 import PdfFileMerger as PdfMerger
    except ImportError:
        print("❌ 错误: 未安装PyPDF2")
        print("   安装: pip install PyPDF2")
        print("   或使用: pdfunite paper_template_en.pdf paper_template_cn.pdf paper_combined.pdf")
        return False
    
    en_pdf = "paper_template_en.pdf"
    cn_pdf = "paper_template_cn.pdf"
    output_pdf = "paper_combined.pdf"
    
    # 检查文件
    if not os.path.exists(en_pdf):
        print(f"❌ 找不到: {en_pdf}")
        return False
    if not os.path.exists(cn_pdf):
        print(f"❌ 找不到: {cn_pdf}")
        return False
    
    # 合并
    print("🔄 合并PDF (英文 + 中文)...")
    merger = PdfMerger()
    merger.append(en_pdf)
    merger.append(cn_pdf)
    merger.write(output_pdf)
    merger.close()
    
    print(f"✅ 完成: {output_pdf} ({os.path.getsize(output_pdf)//1024} KB)")
    return True

if __name__ == '__main__':
    merge_pdfs()
