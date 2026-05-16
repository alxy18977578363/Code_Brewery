#!/bin/bash
# 学术论文编译工具
# Maintainer: zanewang
# Background: M.S. student in Computer Technology, Nanchang University
# Email: zanewang8888@outlook.com

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 论文文件名（撰写过程中保持统一）
PAPER_EN="paper_template_en"
PAPER_CN="paper_template_cn"

# 清理辅助文件
clean_aux_files() {
    local filename=$1
    echo -e "${YELLOW}清理辅助文件...${NC}"
    rm -f "${filename}.aux" "${filename}.log" "${filename}.out" \
          "${filename}.toc" "${filename}.bbl" "${filename}.blg" \
          "${filename}.synctex.gz" 2>/dev/null
}

# 编译英文论文
compile_english() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}开始编译英文论文...${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if [ ! -f "${PAPER_EN}.tex" ]; then
        echo -e "${RED}错误: 找不到 ${PAPER_EN}.tex${NC}"
        return 1
    fi
    
    echo -e "${GREEN}第一次编译...${NC}"
    pdflatex -interaction=nonstopmode "${PAPER_EN}.tex" > /dev/null 2>&1
    
    echo -e "${GREEN}第二次编译（更新引用）...${NC}"
    pdflatex -interaction=nonstopmode "${PAPER_EN}.tex" > /dev/null 2>&1
    
    if [ $? -eq 0 ] && [ -f "${PAPER_EN}.pdf" ]; then
        echo -e "${GREEN}✓ 英文论文编译成功: ${PAPER_EN}.pdf${NC}"
        clean_aux_files "${PAPER_EN}"
        return 0
    else
        echo -e "${RED}✗ 英文论文编译失败${NC}"
        echo -e "${YELLOW}请检查 ${PAPER_EN}.log 文件获取详细错误信息${NC}"
        return 1
    fi
}

# 编译中文论文
compile_chinese() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}开始编译中文论文...${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if [ ! -f "${PAPER_CN}.tex" ]; then
        echo -e "${RED}错误: 找不到 ${PAPER_CN}.tex${NC}"
        return 1
    fi
    
    echo -e "${GREEN}第一次编译...${NC}"
    xelatex -interaction=nonstopmode "${PAPER_CN}.tex" > /dev/null 2>&1
    
    echo -e "${GREEN}第二次编译（更新引用）...${NC}"
    xelatex -interaction=nonstopmode "${PAPER_CN}.tex" > /dev/null 2>&1
    
    if [ $? -eq 0 ] && [ -f "${PAPER_CN}.pdf" ]; then
        echo -e "${GREEN}✓ 中文论文编译成功: ${PAPER_CN}.pdf${NC}"
        clean_aux_files "${PAPER_CN}"
        return 0
    else
        echo -e "${RED}✗ 中文论文编译失败${NC}"
        echo -e "${YELLOW}请检查 ${PAPER_CN}.log 文件获取详细错误信息${NC}"
        return 1
    fi
}

# 合并PDF
merge_pdfs() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}开始合并PDF...${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if [ ! -f "${PAPER_EN}.pdf" ]; then
        echo -e "${RED}错误: 找不到 ${PAPER_EN}.pdf${NC}"
        return 1
    fi
    
    if [ ! -f "${PAPER_CN}.pdf" ]; then
        echo -e "${RED}错误: 找不到 ${PAPER_CN}.pdf${NC}"
        return 1
    fi
    
    # 检查是否安装了pdfunite
    if command -v pdfunite &> /dev/null; then
        pdfunite "${PAPER_EN}.pdf" "${PAPER_CN}.pdf" "paper_combined.pdf"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ PDF合并成功: paper_combined.pdf${NC}"
            echo -e "${YELLOW}  英文在前，中文在后${NC}"
            return 0
        else
            echo -e "${RED}✗ PDF合并失败${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}警告: 未找到 pdfunite 工具${NC}"
        echo -e "${YELLOW}请安装: brew install poppler (macOS)${NC}"
        echo -e "${YELLOW}       或 apt install poppler-utils (Linux)${NC}"
        
        # 尝试使用Python合并
        if command -v python3 &> /dev/null && [ -f "merge_papers.py" ]; then
            echo -e "${YELLOW}尝试使用 Python 脚本合并...${NC}"
            python3 merge_papers.py
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ PDF合并成功: paper_combined.pdf${NC}"
                return 0
            fi
        fi
        
        return 1
    fi
}

# 显示主菜单
show_menu() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    学术论文编译工具 v1.0${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${GREEN}请选择操作：${NC}"
    echo ""
    echo -e "  ${YELLOW}1${NC}) 编译英文论文 (pdflatex)"
    echo -e "  ${YELLOW}2${NC}) 编译中文论文 (xelatex)"
    echo -e "  ${YELLOW}3${NC}) 编译两者"
    echo -e "  ${YELLOW}4${NC}) 合并PDF（英文在前，中文在后）"
    echo -e "  ${YELLOW}5${NC}) 清理所有辅助文件"
    echo -e "  ${YELLOW}0${NC}) 退出"
    echo ""
    echo -ne "${GREEN}请输入选项 [0-5]: ${NC}"
}

# 询问是否合并
ask_merge() {
    echo ""
    echo -ne "${GREEN}是否合并两个PDF? [y/n]: ${NC}"
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# 清理所有辅助文件
clean_all() {
    echo -e "${YELLOW}清理所有辅助文件...${NC}"
    clean_aux_files "${PAPER_EN}"
    clean_aux_files "${PAPER_CN}"
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 主程序
main() {
    # 检查是否在正确的目录
    if [ ! -f "IEEEtran.cls" ]; then
        echo -e "${RED}错误: 请在 paper_example 目录下运行此脚本${NC}"
        exit 1
    fi
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                compile_english
                echo ""
                ;;
            2)
                compile_chinese
                echo ""
                ;;
            3)
                compile_english
                en_status=$?
                echo ""
                compile_chinese
                cn_status=$?
                
                if [ $en_status -eq 0 ] && [ $cn_status -eq 0 ]; then
                    if ask_merge; then
                        echo ""
                        merge_pdfs
                    fi
                fi
                echo ""
                ;;
            4)
                merge_pdfs
                echo ""
                ;;
            5)
                clean_all
                echo ""
                ;;
            0)
                echo -e "${GREEN}再见！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选项，请重新选择${NC}"
                echo ""
                ;;
        esac
        
        # 暂停，等待用户按键继续
        echo -ne "${YELLOW}按 Enter 继续...${NC}"
        read -r
        clear
    done
}

# 运行主程序
main
