// 玉石设计功能
document.addEventListener('DOMContentLoaded', function() {
    // 设计选项数据
    const designOptions = {
        materials: [
            { 
                id: 'white-jade', 
                name: '羊脂白玉', 
                color: '#f5f1e6',
                texture: 'linear-gradient(135deg, #f5f1e6 0%, #e8e0d0 50%, #f5f1e6 100%)',
                opacity: 0.9,
                gloss: 0.7
            },
            { 
                id: 'green-jade', 
                name: '青玉', 
                color: '#7a9c8c',
                texture: 'linear-gradient(135deg, #7a9c8c 0%, #5e8c7a 50%, #7a9c8c 100%)',
                opacity: 0.85,
                gloss: 0.6
            },
            { 
                id: 'mutton-fat', 
                name: '和田玉', 
                color: '#f8f4e8',
                texture: 'radial-gradient(circle at 30% 30%, #f8f4e8 0%, #e8e0d0 40%, #f8f4e8 100%)',
                opacity: 0.95,
                gloss: 0.8
            },
            { 
                id: 'jadeite', 
                name: '翡翠', 
                color: '#3a8c6e',
                texture: 'linear-gradient(45deg, #2a7c5e 0%, #3a8c6e 25%, #4a9c7e 50%, #3a8c6e 75%, #2a7c5e 100%)',
                opacity: 0.8,
                gloss: 0.9
            },
            { 
                id: 'lavender-jade', 
                name: '紫罗兰', 
                color: '#b8a9c9',
                texture: 'linear-gradient(135deg, #c8b9d9 0%, #b8a9c9 50%, #a899b9 100%)',
                opacity: 0.75,
                gloss: 0.7
            },
            { 
                id: 'yellow-jade', 
                name: '黄玉', 
                color: '#e8d494',
                texture: 'radial-gradient(circle at 70% 30%, #f8e4a4 0%, #e8d494 40%, #d8c484 100%)',
                opacity: 0.85,
                gloss: 0.65
            }
        ],
        decorations: [
            { 
                id: 'dragon', 
                name: '龙纹', 
                symbol: 'dragon',
                pattern: 'dragon-pattern',
                complexity: 'high',
                svg: `<svg viewBox="0 0 100 100">
                    <path d="M20,50 Q40,30 60,50 Q80,70 60,90 Q40,70 20,50" fill="none" stroke="#d4af37" stroke-width="2"/>
                    <path d="M30,45 Q45,35 60,45" fill="none" stroke="#d4af37" stroke-width="1.5"/>
                </svg>`
            },
            { 
                id: 'phoenix', 
                name: '凤纹', 
                symbol: 'phoenix',
                pattern: 'phoenix-pattern',
                complexity: 'high',
                svg: `<svg viewBox="0 0 100 100">
                    <path d="M30,40 Q50,20 70,40 Q65,60 50,70 Q35,60 30,40" fill="none" stroke="#d4af37" stroke-width="2"/>
                    <path d="M40,35 L45,25 M50,33 L55,23 M60,35 L65,25" stroke="#d4af37" stroke-width="1"/>
                </svg>`
            },
            { 
                id: 'cloud', 
                name: '云纹', 
                symbol: 'cloud',
                pattern: 'cloud-pattern',
                complexity: 'medium',
                svg: `<svg viewBox="0 0 100 100">
                    <path d="M25,50 Q30,40 40,45 Q45,35 55,40 Q60,30 70,35 Q75,45 65,50 Q70,60 60,55 Q55,65 45,60 Q40,70 30,65 Q25,55 25,50" 
                          fill="none" stroke="#d4af37" stroke-width="2"/>
                </svg>`
            },
            { 
                id: 'lotus', 
                name: '莲花', 
                symbol: 'lotus',
                pattern: 'lotus-pattern',
                complexity: 'medium',
                svg: `<svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="15" fill="none" stroke="#d4af37" stroke-width="2"/>
                    <path d="M35,50 Q30,35 40,30 Q50,25 60,30 Q70,35 65,50 Q70,65 60,70 Q50,75 40,70 Q30,65 35,50" 
                          fill="none" stroke="#d4af37" stroke-width="1.5"/>
                </svg>`
            },
            { 
                id: 'blessing', 
                name: '福字纹', 
                symbol: '福',
                pattern: 'blessing-pattern',
                complexity: 'low',
                svg: `<svg viewBox="0 0 100 100">
                    <text x="50" y="60" text-anchor="middle" font-family="SimSun, serif" font-size="40" fill="#d4af37">福</text>
                </svg>`
            },
            { 
                id: 'longevity', 
                name: '寿字纹', 
                symbol: '寿',
                pattern: 'longevity-pattern',
                complexity: 'low',
                svg: `<svg viewBox="0 0 100 100">
                    <text x="50" y="60" text-anchor="middle" font-family="SimSun, serif" font-size="40" fill="#d4af37">寿</text>
                </svg>`
            },
            { 
                id: 'bats', 
                name: '蝙蝠纹', 
                symbol: 'bats',
                pattern: 'bats-pattern',
                complexity: 'medium',
                svg: `<svg viewBox="0 0 100 100">
                    <path d="M40,40 Q50,30 60,40 Q70,50 60,60 Q50,70 40,60 Q30,50 40,40" fill="none" stroke="#d4af37" stroke-width="2"/>
                    <path d="M35,45 L25,35 M45,35 L35,25 M55,35 L65,25 M65,45 L75,35" stroke="#d4af37" stroke-width="1.5"/>
                </svg>`
            },
            { 
                id: 'fishes', 
                name: '双鱼纹', 
                symbol: 'fishes',
                pattern: 'fishes-pattern',
                complexity: 'medium',
                svg: `<svg viewBox="0 0 100 100">
                    <path d="M30,50 Q40,40 50,50 Q60,60 50,70 Q40,80 30,70 Q20,60 30,50" fill="none" stroke="#d4af37" stroke-width="2"/>
                    <path d="M70,50 Q60,40 50,50 Q40,60 50,70 Q60,80 70,70 Q80,60 70,50" fill="none" stroke="#d4af37" stroke-width="2"/>
                </svg>`
            },
            { 
                id: 'thunder', 
                name: '雷纹', 
                symbol: 'thunder',
                pattern: 'thunder-pattern',
                complexity: 'medium',
                svg: `<svg viewBox="0 0 100 100">
                    <path d="M30,30 L45,45 L35,55 L50,70 L40,80 L25,65 L35,55 L20,40 Z" fill="none" stroke="#d4af37" stroke-width="2"/>
                </svg>`
            },
            { 
                id: 'taotie', 
                name: '饕餮纹', 
                symbol: 'taotie',
                pattern: 'taotie-pattern',
                complexity: 'high',
                svg: `<svg viewBox="0 0 100 100">
                    <path d="M30,40 Q40,30 50,40 Q60,30 70,40 Q75,50 70,60 Q60,70 50,60 Q40,70 30,60 Q25,50 30,40" 
                          fill="none" stroke="#d4af37" stroke-width="2"/>
                    <circle cx="40" cy="45" r="3" fill="#d4af37"/>
                    <circle cx="60" cy="45" r="3" fill="#d4af37"/>
                    <path d="M45,55 Q50,60 55,55" fill="none" stroke="#d4af37" stroke-width="1.5"/>
                </svg>`
            }
        ],
        shapes: [
            { 
                id: 'bi', 
                name: '玉璧', 
                type: 'disc',
                description: '圆形中间有孔的礼器'
            },
            { 
                id: 'cong', 
                name: '玉琮', 
                type: 'tube',
                description: '外方内圆的礼器'
            },
            { 
                id: 'pendant', 
                name: '玉佩', 
                type: 'pendant',
                description: '悬挂佩戴的装饰玉器'
            },
            { 
                id: 'bracelet', 
                name: '玉镯', 
                type: 'bracelet',
                description: '圆形手镯'
            },
            { 
                id: 'vase', 
                name: '玉瓶', 
                type: 'vase',
                description: '瓶状玉器'
            },
            { 
                id: 'animal', 
                name: '玉兽', 
                type: 'animal',
                description: '动物形状玉雕'
            },
            { 
                id: 'ruyi', 
                name: '玉如意', 
                type: 'ruyi',
                description: '如意形状吉祥物'
            },
            { 
                id: 'seal', 
                name: '玉玺', 
                type: 'seal',
                description: '印章形状玉器'
            }
        ],
        sizes: [
            { id: 'small', name: '小型', scale: 0.7 },
            { id: 'medium', name: '中型', scale: 1.0 },
            { id: 'large', name: '大型', scale: 1.3 }
        ]
    };
    
    // 当前设计状态
    let currentDesign = {
        material: designOptions.materials[0],
        decoration: designOptions.decorations[0],
        shape: designOptions.shapes[0],
        size: designOptions.sizes[1],
        rotation: 0,
        // 新增装饰元素控制属性
        decorationSize: 1.0,  // 默认大小比例
        decorationX: 0,       // X轴位置偏移
        decorationY: 0        // Y轴位置偏移
    };
    
    const designCanvas = document.getElementById('design-canvas');
    
    // 初始化选项
    function initializeOptions() {
        // 材质选项
        const materialContainer = document.getElementById('material-options');
        designOptions.materials.forEach(material => {
            const item = createOptionItem('material', material);
            materialContainer.appendChild(item);
        });
        
        // 装饰选项
        const decorationContainer = document.getElementById('decoration-options');
        designOptions.decorations.forEach(decoration => {
            const item = createOptionItem('decoration', decoration);
            decorationContainer.appendChild(item);
        });
        
        // 形状选项
        const shapeContainer = document.getElementById('shape-options');
        designOptions.shapes.forEach(shape => {
            const item = createOptionItem('shape', shape);
            shapeContainer.appendChild(item);
        });
        
        // 大小选项
        const sizeContainer = document.getElementById('size-options');
        if (sizeContainer) {
            designOptions.sizes.forEach(size => {
                const item = createOptionItem('size', size);
                sizeContainer.appendChild(item);
            });
        }
        
        // 初始化材质属性控制
        initializeMaterialControls();
    }
    
    // 创建设计选项元素
    function createOptionItem(type, option) {
        const item = document.createElement('div');
        item.className = 'option-item';
        item.setAttribute('data-type', type);
        item.setAttribute('data-value', option.id);

        // 根据类型创建不同的内容
        if (type === 'material') {
            item.innerHTML = `
                <div class="material-sample" style="background: ${option.texture}"></div>
                <span class="option-name">${option.name}</span>
            `;
        } else if (type === 'decoration') {
            item.innerHTML = `
                <div class="decoration-sample">
                    ${option.svg}
                </div>
                <span class="option-name">${option.name}</span>
            `;
        } else if (type === 'shape') {
            item.innerHTML = `
                <div class="shape-sample ${option.type}"></div>
                <span class="option-name">${option.name}</span>
            `;
        } else if (type === 'size') {
            item.innerHTML = `
                <div class="size-sample ${option.id}"></div>
                <span class="option-name">${option.name}</span>
            `;
        }

        // 设置默认选中状态
        if ((type === 'material' && option.id === 'white-jade') || 
            (type === 'decoration' && option.id === 'dragon') ||
            (type === 'shape' && option.id === 'bi') ||
            (type === 'size' && option.id === 'medium')) {
            item.classList.add('active');
        }

        item.addEventListener('click', function() {
            // 移除同类型选项的active类
            document.querySelectorAll(`.option-item[data-type="${type}"]`).forEach(opt => {
                opt.classList.remove('active');
            });

            // 添加当前选项的active类
            this.classList.add('active');

            // 更新当前设计状态
            if (type === 'material') {
                currentDesign.material = option;
                updateMaterialControls();
            } else if (type === 'decoration') {
                currentDesign.decoration = option;
            } else if (type === 'shape') {
                currentDesign.shape = option;
            } else if (type === 'size') {
                currentDesign.size = option;
            }

            // 更新设计画布
            updateDesignCanvas();
        });

        return item;
    }
    
    // 初始化材质属性控制
    function initializeMaterialControls() {
        const controlsContainer = document.getElementById('material-controls');
        if (!controlsContainer) return;
        
        controlsContainer.innerHTML = `
            <h3>材质属性</h3>
            <div class="control-group">
                <label for="opacity-control">透明度</label>
                <input type="range" id="opacity-control" min="0.5" max="1" step="0.05" value="${currentDesign.material.opacity}">
                <span id="opacity-value">${currentDesign.material.opacity}</span>
            </div>
            <div class="control-group">
                <label for="gloss-control">光泽度</label>
                <input type="range" id="gloss-control" min="0.3" max="1" step="0.05" value="${currentDesign.material.gloss}">
                <span id="gloss-value">${currentDesign.material.gloss}</span>
            </div>
            <div class="control-group">
                <label for="rotation-control">旋转角度</label>
                <input type="range" id="rotation-control" min="0" max="360" step="15" value="${currentDesign.rotation}">
                <span id="rotation-value">${currentDesign.rotation}°</span>
            </div>
            
            <!-- 新增装饰元素控制 -->
            <h3>装饰元素控制</h3>
            <div class="control-group">
                <label for="decoration-size-control">装饰大小</label>
                <input type="range" id="decoration-size-control" min="0.5" max="2" step="0.1" value="${currentDesign.decorationSize}">
                <span id="decoration-size-value">${currentDesign.decorationSize}</span>
            </div>
            <div class="control-group">
                <label for="decoration-x-control">水平位置</label>
                <input type="range" id="decoration-x-control" min="-50" max="50" step="5" value="${currentDesign.decorationX}">
                <span id="decoration-x-value">${currentDesign.decorationX}%</span>
            </div>
            <div class="control-group">
                <label for="decoration-y-control">垂直位置</label>
                <input type="range" id="decoration-y-control" min="-50" max="50" step="5" value="${currentDesign.decorationY}">
                <span id="decoration-y-value">${currentDesign.decorationY}%</span>
            </div>
        `;
        
        // 添加事件监听 - 原有控制
        document.getElementById('opacity-control').addEventListener('input', function() {
            currentDesign.material.opacity = parseFloat(this.value);
            document.getElementById('opacity-value').textContent = this.value;
            updateDesignCanvas();
        });
        
        document.getElementById('gloss-control').addEventListener('input', function() {
            currentDesign.material.gloss = parseFloat(this.value);
            document.getElementById('gloss-value').textContent = this.value;
            updateDesignCanvas();
        });
        
        document.getElementById('rotation-control').addEventListener('input', function() {
            currentDesign.rotation = parseInt(this.value);
            document.getElementById('rotation-value').textContent = this.value + '°';
            updateDesignCanvas();
        });
        
        // 新增装饰控制事件监听
        document.getElementById('decoration-size-control').addEventListener('input', function() {
            currentDesign.decorationSize = parseFloat(this.value);
            document.getElementById('decoration-size-value').textContent = this.value;
            updateDesignCanvas();
        });
        
        document.getElementById('decoration-x-control').addEventListener('input', function() {
            currentDesign.decorationX = parseInt(this.value);
            document.getElementById('decoration-x-value').textContent = this.value + '%';
            updateDesignCanvas();
        });
        
        document.getElementById('decoration-y-control').addEventListener('input', function() {
            currentDesign.decorationY = parseInt(this.value);
            document.getElementById('decoration-y-value').textContent = this.value + '%';
            updateDesignCanvas();
        });
    }
    
    // 更新材质控制
    function updateMaterialControls() {
        const opacityControl = document.getElementById('opacity-control');
        const glossControl = document.getElementById('gloss-control');
        
        if (opacityControl) {
            opacityControl.value = currentDesign.material.opacity;
            document.getElementById('opacity-value').textContent = currentDesign.material.opacity;
        }
        
        if (glossControl) {
            glossControl.value = currentDesign.material.gloss;
            document.getElementById('gloss-value').textContent = currentDesign.material.gloss;
        }
        
        updateDesignCanvas();
    }
    
    // 更新设计画布
    function updateDesignCanvas() {
        // 清空画布
        designCanvas.innerHTML = '';

        // 创建3D效果容器
        const scene = document.createElement('div');
        scene.className = 'jade-scene';
        scene.style.transform = `rotate(${currentDesign.rotation}deg) scale(${currentDesign.size.scale})`;

        // 创建基础玉石材质
        const materialDiv = document.createElement('div');
        materialDiv.className = 'design-material';
        materialDiv.style.cssText = `
            background: ${currentDesign.material.texture};
            opacity: ${currentDesign.material.opacity};
            filter: brightness(${0.8 + currentDesign.material.gloss * 0.4});
        `;

        // 根据形状设置样式
        applyShapeStyle(materialDiv, currentDesign.shape.type);

        // 添加内部纹理效果
        const innerTexture = document.createElement('div');
        innerTexture.className = 'inner-texture';
        materialDiv.appendChild(innerTexture);

        // 添加装饰元素 - 使用SVG
        if (currentDesign.decoration) {
            const decorationDiv = document.createElement('div');
            decorationDiv.className = `design-decoration ${currentDesign.decoration.pattern}`;
            decorationDiv.innerHTML = currentDesign.decoration.svg;
            
            // 应用装饰元素自定义设置
            decorationDiv.style.transform = `scale(${currentDesign.decorationSize}) translate(${currentDesign.decorationX}%, ${currentDesign.decorationY}%)`;
            
            materialDiv.appendChild(decorationDiv);
        }

        // 添加高光效果
        const highlight = document.createElement('div');
        highlight.className = 'material-highlight';
        materialDiv.appendChild(highlight);

        scene.appendChild(materialDiv);
        designCanvas.appendChild(scene);

        // 添加阴影效果
        const shadow = document.createElement('div');
        shadow.className = 'jade-shadow';
        designCanvas.appendChild(shadow);
    }
    
    // 应用形状样式
    function applyShapeStyle(element, shapeType) {
        switch(shapeType) {
            case 'disc': // 玉璧
                element.style.borderRadius = '50%';
                element.style.width = '70%';
                element.style.height = '70%';
                element.style.position = 'relative';
                // 添加中心孔
                element.innerHTML += '<div class="bi-hole"></div>';
                break;
            case 'tube': // 玉琮
                element.style.borderRadius = '10%';
                element.style.width = '50%';
                element.style.height = '70%';
                element.style.position = 'relative';
                // 添加中心孔
                element.innerHTML += '<div class="cong-hole"></div>';
                break;
            case 'pendant': // 玉佩
                element.style.borderRadius = '40% 40% 50% 50%';
                element.style.width = '50%';
                element.style.height = '70%';
                element.style.clipPath = 'polygon(0% 0%, 100% 0%, 80% 100%, 20% 100%)';
                break;
            case 'bracelet': // 玉镯
                element.style.borderRadius = '50%';
                element.style.width = '70%';
                element.style.height = '70%';
                element.style.position = 'relative';
                // 添加中心孔
                element.innerHTML += '<div class="bracelet-hole"></div>';
                break;
            case 'vase': // 玉瓶
                element.style.borderRadius = '40% 40% 30% 30%';
                element.style.width = '40%';
                element.style.height = '80%';
                element.style.clipPath = 'polygon(30% 0%, 70% 0%, 85% 100%, 15% 100%)';
                break;
            case 'animal': // 玉兽
                element.style.borderRadius = '30%';
                element.style.width = '60%';
                element.style.height = '50%';
                break;
            case 'ruyi': // 玉如意
                element.style.borderRadius = '40% 10% 40% 10%';
                element.style.width = '80%';
                element.style.height = '40%';
                element.style.clipPath = 'polygon(0% 20%, 20% 0%, 80% 0%, 100% 20%, 80% 40%, 20% 40%)';
                break;
            case 'seal': // 玉玺
                element.style.borderRadius = '10%';
                element.style.width = '50%';
                element.style.height = '60%';
                break;
        }
    }
    
    // 设计控制按钮
    document.getElementById('save-design').addEventListener('click', function() {
        // 原有的保存设计功能
        const designId = window.utils.generateId();
        const designs = JSON.parse(localStorage.getItem('jadeDesigns') || '[]');

        designs.push({
            id: designId,
            design: currentDesign,
            timestamp: new Date().toISOString()
        });

        localStorage.setItem('jadeDesigns', JSON.stringify(designs));

        // 显示保存成功消息
        showNotification(`设计已保存！ID: ${designId}`, 'success');
    });

    
    document.getElementById('reset-design').addEventListener('click', function() {
        if (confirm('确定要重置当前设计吗？')) {
            currentDesign = {
                material: designOptions.materials[0],
                decoration: designOptions.decorations[0],
                shape: designOptions.shapes[0],
                size: designOptions.sizes[1],
                rotation: 0,
                decorationSize: 1.0,
                decorationX: 0,
                decorationY: 0
            };
            
            // 重置选项状态
            document.querySelectorAll('.option-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // 设置默认选项
            document.querySelector('.option-item[data-type="material"][data-value="white-jade"]').classList.add('active');
            document.querySelector('.option-item[data-type="decoration"][data-value="dragon"]').classList.add('active');
            document.querySelector('.option-item[data-type="shape"][data-value="bi"]').classList.add('active');
            document.querySelector('.option-item[data-type="size"][data-value="medium"]').classList.add('active');
            
            updateMaterialControls();
            updateDesignCanvas();
        }
    });
    
    // 显示通知
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // 初始化
    initializeOptions();
    updateDesignCanvas();
    
    console.log('增强版玉石设计模块已加载');
});