// 玉器科普功能 - 增强版
document.addEventListener('DOMContentLoaded', function() {
    // 知识卡片数据 - 扩展版
    const knowledgeData = [
        {
            id: 1,
            title: "玉石分类",
            content: "玉石主要分为软玉和硬玉两大类。软玉以和田玉为代表，硬玉以翡翠为代表。中国四大名玉包括新疆和田玉、河南独山玉、辽宁岫岩玉和湖北绿松石。",
            icon: "🔍",
            category: "基础分类",
            color: "#5e8c7a"
        },
        {
            id: 2,
            title: "玉石文化",
            content: "在中国传统文化中，玉被视为美德和权力的象征。'君子比德于玉'体现了玉与道德品质的关联。玉器在古代是祭祀、礼仪和身份的重要标志。",
            icon: "📜",
            category: "文化历史",
            color: "#8c5e7a"
        },
        {
            id: 3,
            title: "玉石鉴别",
            content: "鉴别玉石真伪可通过观察颜色均匀度、检查质地细腻度、听声音清脆度等方法。天然玉石通常有细微的纹理和杂质，而人造玉石往往过于完美。",
            icon: "🔬",
            category: "实用技巧",
            color: "#5e7a8c"
        },
        {
            id: 4,
            title: "玉石保养",
            content: "玉石保养应避免碰撞、高温和化学物质。定期用软布擦拭，保持玉器清洁。长期佩戴可使玉石更加温润，这就是'人养玉，玉养人'的道理。",
            icon: "💎",
            category: "实用技巧",
            color: "#8c7a5e"
        },
        {
            id: 5,
            title: "玉器历史",
            content: "中国玉器文化已有8000多年历史，从新石器时代的红山文化、良渚文化开始，玉器就作为礼器、装饰品和权力象征使用。",
            icon: "⏳",
            category: "文化历史",
            color: "#7a8c5e"
        },
        {
            id: 6,
            title: "玉器工艺",
            content: "传统玉器制作工艺包括选料、设计、切割、琢磨、抛光等步骤。精湛的雕刻技艺能使玉石焕发出独特的艺术魅力。",
            icon: "⚒️",
            category: "工艺技术",
            color: "#8c5e5e"
        },
        {
            id: 7,
            title: "玉器象征",
            content: "不同玉器形状和图案有不同寓意：玉璧象征天，玉琮象征地，玉龙象征权力，玉蝉象征重生，玉如意象征吉祥。",
            icon: "🔄",
            category: "文化历史",
            color: "#5e8c8c"
        },
        {
            id: 8,
            title: "玉器收藏",
            content: "收藏玉器需注重材质、工艺、年代和完整性。古玉收藏要特别注意辨别真伪，新玉收藏则更注重材质和工艺水平。",
            icon: "🏺",
            category: "实用技巧",
            color: "#8c8c5e"
        }
    ];

    // 玉器发展时间线数据
    const timelineData = [
        {
            period: "新石器时代",
            time: "约8000-4000年前",
            content: "红山文化、良渚文化出现最早的玉器，主要用于祭祀和装饰",
            icon: "⛏️"
        },
        {
            period: "夏商周时期",
            time: "约公元前2070-前256年",
            content: "玉器成为礼制和权力的象征，出现玉璧、玉琮等礼器",
            icon: "👑"
        },
        {
            period: "秦汉时期",
            time: "公元前221-公元220年",
            content: "玉器使用更加广泛，出现金缕玉衣等精美葬玉",
            icon: "⚔️"
        },
        {
            period: "唐宋时期",
            time: "公元618-1279年",
            content: "玉器工艺进一步发展，出现更多生活用玉和装饰玉器",
            icon: "🖋️"
        },
        {
            period: "明清时期",
            time: "公元1368-1912年",
            content: "玉器工艺达到巅峰，出现大量精美玉雕作品",
            icon: "🏯"
        },
        {
            period: "现代",
            time: "20世纪至今",
            content: "玉器艺术与现代设计结合，出现更多创新作品",
            icon: "💡"
        }
    ];

    // 趣味知识数据
    const funFactsData = [
        "💎 古人认为玉能通灵，是连接天地的媒介",
        "📿 玉蝉在古代常被放入逝者口中，象征重生",
        "🔮 慈禧太后特别喜爱翡翠，拥有大量翡翠饰品",
        "🏺 和氏璧是中国历史上最著名的玉器之一",
        "🐉 龙纹是玉器上最常见的装饰图案之一",
        "🌿 '人养玉三年，玉养人一生'是民间流传的说法",
        "💰 优质翡翠的价格可以超过同等重量的黄金",
        "🎨 玉雕是中国传统工艺美术的重要门类"
    ];

    // 测验数据 - 扩展版
    const quizData = [
        {
            question: "中国四大名玉不包括以下哪种？",
            options: [
                { text: "和田玉", correct: false },
                { text: "缅甸翡翠", correct: true },
                { text: "独山玉", correct: false },
                { text: "岫岩玉", correct: false }
            ],
            explanation: "中国四大名玉是新疆和田玉、河南独山玉、辽宁岫岩玉和湖北绿松石。"
        },
        {
            question: "以下哪种玉石硬度最高？",
            options: [
                { text: "和田玉", correct: false },
                { text: "翡翠", correct: true },
                { text: "岫岩玉", correct: false },
                { text: "绿松石", correct: false }
            ],
            explanation: "翡翠的硬度为6.5-7，是常见玉石中硬度最高的。"
        },
        {
            question: "'君子比德于玉'出自哪部经典？",
            options: [
                { text: "《论语》", correct: false },
                { text: "《礼记》", correct: true },
                { text: "《诗经》", correct: false },
                { text: "《道德经》", correct: false }
            ],
            explanation: "'君子比德于玉'出自《礼记·聘义》，体现了玉与君子品德的关联。"
        },
        {
            question: "以下哪种玉器在古代用作礼器？",
            options: [
                { text: "玉璧", correct: true },
                { text: "玉簪", correct: false },
                { text: "玉镯", correct: false },
                { text: "玉扳指", correct: false }
            ],
            explanation: "玉璧是古代重要的礼器，用于祭祀和朝聘等场合。"
        },
        {
            question: "红山文化出土的著名玉器是什么？",
            options: [
                { text: "玉龙", correct: true },
                { text: "玉琮", correct: false },
                { text: "玉璧", correct: false },
                { text: "玉衣", correct: false }
            ],
            explanation: "红山文化出土的C形玉龙是中国最早的龙形玉器，被誉为'中华第一龙'。"
        }
    ];

    let currentQuizIndex = 0;
    let score = 0;
    let answeredQuestions = 0;

    // 初始化知识卡片
    function initializeKnowledgeCards() {
        const container = document.getElementById('knowledge-cards');
        container.innerHTML = '';
        
        // 创建分类筛选器
        const categories = [...new Set(knowledgeData.map(item => item.category))];
        const filterContainer = document.createElement('div');
        filterContainer.className = 'category-filters';
        filterContainer.innerHTML = `
            <button class="filter-btn active" data-category="all">全部</button>
            ${categories.map(cat => `<button class="filter-btn" data-category="${cat}">${cat}</button>`).join('')}
        `;
        container.appendChild(filterContainer);
        
        // 创建卡片容器
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'knowledge-cards-container';
        container.appendChild(cardsContainer);
        
        // 渲染卡片
        renderCards(knowledgeData, cardsContainer);
        
        // 添加筛选功能
        filterContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('filter-btn')) {
                // 更新按钮状态
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
                
                // 筛选卡片
                const category = e.target.getAttribute('data-category');
                const filteredData = category === 'all' 
                    ? knowledgeData 
                    : knowledgeData.filter(item => item.category === category);
                
                renderCards(filteredData, cardsContainer);
            }
        });
    }
    
    // 渲染知识卡片
    function renderCards(data, container) {
        container.innerHTML = '';
        
        data.forEach(item => {
            const card = document.createElement('div');
            card.className = 'knowledge-card';
            card.style.borderLeft = `5px solid ${item.color}`;
            card.innerHTML = `
                <div class="card-header">
                    <h3><span style="margin-right:10px;">${item.icon}</span>${item.title}</h3>
                    <span class="card-category" style="background-color:${item.color}">${item.category}</span>
                </div>
                <p>${item.content}</p>
            `;
            container.appendChild(card);
        });
    }
    
    // 初始化时间线
    function initializeTimeline() {
        const timelineContainer = document.createElement('div');
        timelineContainer.className = 'timeline-container';
        timelineContainer.innerHTML = `
            <h2 class="section-title">玉器发展历史</h2>
            <div class="timeline">
                ${timelineData.map((item, index) => `
                    <div class="timeline-item ${index % 2 === 0 ? 'left' : 'right'}">
                        <div class="timeline-content">
                            <div class="timeline-icon">${item.icon}</div>
                            <h3>${item.period}</h3>
                            <span class="timeline-time">${item.time}</span>
                            <p>${item.content}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        document.getElementById('knowledge').appendChild(timelineContainer);
    }
    
    // 初始化趣味知识轮播
    function initializeFunFacts() {
        const factsContainer = document.createElement('div');
        factsContainer.className = 'fun-facts-container';
        factsContainer.innerHTML = `
            <h2 class="section-title">玉器趣味知识</h2>
            <div class="fun-facts-carousel">
                <div class="fun-facts-track" id="fun-facts-track">
                    ${funFactsData.map(fact => `
                        <div class="fun-fact-item">${fact}</div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.getElementById('knowledge').appendChild(factsContainer);
        
        // 实现自动轮播
        let currentFactIndex = 0;
        const track = document.getElementById('fun-facts-track');
        
        setInterval(() => {
            currentFactIndex = (currentFactIndex + 1) % funFactsData.length;
            track.style.transform = `translateX(-${currentFactIndex * 100}%)`;
        }, 4000);
    }
    
    // 初始化测验
    function initializeQuiz() {
        const quizContainer = document.querySelector('.quiz-container');
        quizContainer.innerHTML = `
            <h3>玉器知识小测验</h3>
            <div class="quiz-progress">
                <span id="quiz-progress">${currentQuizIndex + 1}/${quizData.length}</span>
                <span id="quiz-score">得分: ${score}/${answeredQuestions}</span>
            </div>
            <div class="quiz-question" id="quiz-question"></div>
            <div class="quiz-options" id="quiz-options"></div>
            <div class="quiz-result" id="quiz-result"></div>
            <div class="quiz-explanation" id="quiz-explanation"></div>
            <div class="quiz-controls">
                <button class="design-btn" id="next-quiz">下一题</button>
                <button class="design-btn" id="restart-quiz">重新开始</button>
            </div>
        `;

        // 立即更新测验内容
        updateQuiz();

        // 下一题按钮
        document.getElementById('next-quiz').addEventListener('click', nextQuestion);

        // 重新开始按钮
        document.getElementById('restart-quiz').addEventListener('click', restartQuiz);
    }

    // 更新测验内容
    function updateQuiz() {
        const quiz = quizData[currentQuizIndex];
        const questionElement = document.getElementById('quiz-question');
        const optionsContainer = document.getElementById('quiz-options');
        const resultElement = document.getElementById('quiz-result');
        const explanationElement = document.getElementById('quiz-explanation');

        // 清空之前的内容
        questionElement.textContent = quiz.question;
        optionsContainer.innerHTML = '';
        resultElement.textContent = '';
        resultElement.className = 'quiz-result';
        explanationElement.textContent = '';
        explanationElement.style.display = 'none';

        // 更新进度
        document.getElementById('quiz-progress').textContent = `${currentQuizIndex + 1}/${quizData.length}`;
        document.getElementById('quiz-score').textContent = `得分: ${score}/${answeredQuestions}`;

        // 创建选项
        quiz.options.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'quiz-option';
            optionElement.textContent = option.text;
            optionElement.setAttribute('data-correct', option.correct);

            // 重置样式
            optionElement.style.backgroundColor = '';
            optionElement.style.color = '';
            optionElement.style.pointerEvents = 'auto';

            optionElement.addEventListener('click', function() {
                const isCorrect = this.getAttribute('data-correct') === 'true';
                answeredQuestions++;

                if (isCorrect) {
                    score++;
                    resultElement.textContent = '回答正确！';
                    resultElement.className = 'quiz-result correct';
                } else {
                    resultElement.textContent = '回答错误！';
                    resultElement.className = 'quiz-result incorrect';
                }

                // 显示解释
                explanationElement.textContent = quiz.explanation;
                explanationElement.style.display = 'block';

                // 显示所有选项的正确/错误状态
                document.querySelectorAll('.quiz-option').forEach(opt => {
                    if (opt.getAttribute('data-correct') === 'true') {
                        opt.style.backgroundColor = '#3a8c6e';
                        opt.style.color = 'white';
                    } else {
                        opt.style.backgroundColor = '#f8f8f8';
                    }
                    opt.style.pointerEvents = 'none';
                });

                // 更新得分
                document.getElementById('quiz-score').textContent = `得分: ${score}/${answeredQuestions}`;
            });

            optionsContainer.appendChild(optionElement);
        });
    }

    // 下一题
    function nextQuestion() {
        if (currentQuizIndex < quizData.length - 1) {
            currentQuizIndex++;
            updateQuiz();
        } else {
            // 显示最终结果
            const resultElement = document.getElementById('quiz-result');
            resultElement.textContent = `测验完成！最终得分: ${score}/${answeredQuestions}`;
            resultElement.className = 'quiz-result final';

            // 禁用下一题按钮
            document.getElementById('next-quiz').disabled = true;
        }
    }

    // 重新开始测验
    function restartQuiz() {
        currentQuizIndex = 0;
        score = 0;
        answeredQuestions = 0;
        const nextButton = document.getElementById('next-quiz');
        if (nextButton) {
            nextButton.disabled = false;
        }
        updateQuiz();
    }
    
    // 智能提示功能
    function initializeSmartTips() {
        // 随机显示玉器知识提示
        const tips = [
            "💡 你知道吗？玉器在古代是权力和地位的象征。",
            "💡 小知识：和田玉的质地越细腻，价值越高。",
            "💡 提示：翡翠以'浓、阳、正、匀'为佳。",
            "💡 有趣的事实：玉器可以吸收人体油脂，越戴越亮。",
            "💡 你知道吗？中国玉文化已有8000多年历史。",
            "💡 小知识：玉璧在古代是祭天的礼器。"
        ];
        
        setInterval(() => {
            if (document.getElementById('knowledge').classList.contains('active')) {
                const randomTip = tips[Math.floor(Math.random() * tips.length)];
                showFloatingTip(randomTip);
            }
        }, 30000); // 每30秒显示一次提示
    }
    
    // 显示浮动提示
    function showFloatingTip(message) {
        const tip = document.createElement('div');
        tip.textContent = message;
        tip.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--jade-green);
            color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            max-width: 300px;
            animation: slideIn 0.5s ease;
        `;
        
        document.body.appendChild(tip);
        
        setTimeout(() => {
            tip.style.animation = 'slideOut 0.5s ease';
            setTimeout(() => {
                document.body.removeChild(tip);
            }, 500);
        }, 5000);
    }
    
    // 添加动画样式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    // 初始化所有功能
    initializeKnowledgeCards();
    initializeTimeline();
    initializeFunFacts();
    initializeQuiz();
    initializeSmartTips();
    
    console.log('增强版玉器科普模块已加载');
});