// 主程序 - 导航和全局功能
document.addEventListener('DOMContentLoaded', function() {
    // 导航切换功能
    const navButtons = document.querySelectorAll('.nav-btn');
    
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 移除所有按钮的active类
            navButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            
            // 添加当前按钮的active类
            this.classList.add('active');
            
            // 隐藏所有内容区域
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // 显示目标内容区域
            const targetId = this.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
    
    // 全局工具函数
    window.utils = {
        // 防抖函数
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // 生成随机ID
        generateId: function() {
            return '_' + Math.random().toString(36).substr(2, 9);
        },
        
        // 格式化日期
        formatDate: function(date) {
            return new Date(date).toLocaleDateString('zh-CN');
        }
    };
    
    console.log('玉石鉴赏与设计平台已加载');
});