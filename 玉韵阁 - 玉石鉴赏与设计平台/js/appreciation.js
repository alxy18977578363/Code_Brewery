// 玉石鉴赏功能
document.addEventListener('DOMContentLoaded', function() {
    const jadeData = [
        {
            id: 1,
            name: "和田玉",
            description: "和田玉是中国四大名玉之一，产自新疆和田地区，质地细腻温润，颜色丰富，以羊脂白玉最为珍贵。",
            image: "../images/hetianyu.jpg", // 修正：使用 ../ 返回上级目录
            color: "#5e8c7a",
            origin: "新疆和田",
            hardness: "6-6.5"
        },
        {
            id: 2,
            name: "翡翠",
            description: "翡翠主要产自缅甸，硬度较高，颜色鲜艳，以翠绿色最为名贵，有'玉中之王'的美誉。",
            image: "../images/feicui.jpg", // 修正：使用 ../ 返回上级目录
            color: "#3a8c6e",
            origin: "缅甸",
            hardness: "6.5-7"
        },
        {
            id: 3,
            name: "岫岩玉",
            description: "岫岩玉产自辽宁岫岩县，是中国历史上最早被开采和使用的玉种之一，颜色多为淡绿色或黄绿色。",
            image: "../images/xiuyanyu.jpg", // 修正：使用 ../ 返回上级目录
            color: "#7a9c8c",
            origin: "辽宁岫岩",
            hardness: "4.5-5.5"
        },
        {
            id: 4,
            name: "独山玉",
            description: "独山玉产自河南南阳，色彩丰富，质地坚韧，有'南阳翡翠'之称，是中国四大名玉之一。",
            image: "../images/dushanyu.jpg", // 修正：使用 ../ 返回上级目录
            color: "#6a8c7a",
            origin: "河南南阳",
            hardness: "6-7"
        },
        {
            id: 5,
            name: "绿松石",
            description: "绿松石因形似松球色近松绿而得名，是古老宝石之一，有着几千年的灿烂历史。",
            image: "../images/lvsongshi.jpg", // 修正：使用 ../ 返回上级目录
            color: "#5e8c8c",
            origin: "湖北、安徽等地",
            hardness: "5-6"
        },
        {
            id: 6,
            name: "青金石",
            description: "青金石是一种深蓝色宝石，自古以来就被视为珍贵的装饰石材，颜色鲜艳深邃。",
            image: "images/qingjinshi.jpg",
            color: "#2a3c8c",
            origin: "阿富汗、智利",
            hardness: "5-6"
        },
        {
            id: 7,
            name: "玛瑙",
            description: "玛瑙是玉髓类矿物的一种，色彩相当有层次，常见的有红、蓝、绿、黄等颜色。",
            image: "images/manao.jpg",
            color: "#8c5e5e",
            origin: "巴西、印度、中国",
            hardness: "6.5-7"
        },
        {
            id: 8,
            name: "琥珀",
            description: "琥珀是远古松科松属植物的树脂埋藏于地层，经过漫长岁月而形成的化石。",
            image: "images/hupo.jpg",
            color: "#8c7a3a",
            origin: "波罗的海地区",
            hardness: "2-2.5"
        },
        {
            id: 9,
            name: "水晶",
            description: "水晶是稀有矿物，宝石的一种，石英结晶体，在矿物学上属于石英族，纯净时形成无色  透明的晶体。",
            image: "images/shuijing.jpg",
            color: "#8c8c8c",
            origin: "全球多地",
            hardness: "7"
        },
        {
            id: 10,
            name: "紫水晶",
            description: "紫水晶是水晶家族中最为高贵美丽的一员，因含有铁、锰等矿物质而形成漂亮的紫色。  ",
            image: "images/zishuijing.jpg",
            color: "#8c5e8c",
            origin: "巴西、乌拉圭",
            hardness: "7"
        },
        {
            id: 11,
            name: "黄玉",
            description: "黄玉是富含氟的硅酸盐矿物，颜色多样，从无色到黄色、蓝色、粉色等，具有玻璃光    泽。",
            image: "images/huangyu.jpg",
            color: "#8c8c3a",
            origin: "巴西、俄罗斯",
            hardness: "8"
        },
        {
            id: 12,
            name: "孔雀石",
            description: "孔雀石由于颜色酷似孔雀羽毛上斑点的绿色而获得如此美丽的名字，是一种古老的玉    料。",
            image: "images/kongqueshi.jpg",
            color: "#3a8c5e",
            origin: "刚果、俄罗斯",
            hardness: "3.5-4"
        },
        {
            id: 13,
            name: "虎眼石",
            description: "虎眼石因其纹理和颜色象木纹，所以又称为木变石，具有猫眼效应的宝石。",
            image: "images/huyanshi.jpg",
            color: "#8c7a3a",
            origin: "南非、澳大利亚",
            hardness: "7"
        },
        {
            id: 14,
            name: "月光石",
            description: "月光石是长石的一种，具有独特的月光效应，仿佛朦胧的月光笼罩在宝石表面。",
            image: "images/yueguangshi.jpg",
            color: "#8c8c7a",
            origin: "斯里兰卡、印度",
            hardness: "6-6.5"
        },
        {
            id: 15,
            name: "红宝石",
            description: "红宝石是指颜色呈红色的刚玉，它是刚玉的一种，主要成分是氧化铝，红色来自铬元    素。",
            image: "images/hongbaoshi.jpg",
            color: "#8c2a2a",
            origin: "缅甸、泰国",
            hardness: "9"
        },
        {
            id: 16,
            name: "蓝宝石",
            description: "蓝宝石是刚玉宝石中除红宝石之外，其它颜色刚玉宝石的通称，主要成分是氧化铝。",
            image: "images/lanbaoshi.jpg",
            color: "#2a5e8c",
            origin: "克什米尔、斯里兰卡",
            hardness: "9"
        },
        {
            id: 17,
            name: "祖母绿",
            description: "祖母绿被称为绿宝石之王，是相当贵重的宝石，国际珠宝界公认的四大名贵宝石之一。  ",
            image: "images/zumulv.jpg",
            color: "#2a8c5e",
            origin: "哥伦比亚、巴西",
            hardness: "7.5-8"
        },
        {
            id: 18,
            name: "欧泊",
            description: "欧泊的英文为Opal，源于拉丁文Opalus，意思是'集宝石之美于一身’，以其独特的变    彩效应闻名。",
            image: "images/oubo.jpg",
            color: "#8c5e7a",
            origin: "澳大利亚、墨西哥",
            hardness: "5.5-6.5"
        },
        {
            id: 19,
            name: "碧玺",
            description: "碧玺又称为电气石，是一种硼硅酸盐结晶体，可含有铝、铁、镁、钠、锂、钾等元素。  ",
            image: "images/bixi.jpg",
            color: "#8c3a7a",
            origin: "巴西、阿富汗",
            hardness: "7-7.5"
        },
        {
            id: 20,
            name: "石榴石",
            description: "石榴石晶体与石榴籽的形状、颜色十分相似，故名'石榴石’，常见颜色有红、紫红、橙  红等。",
            image: "images/shiliushi.jpg",
            color: "#8c2a3a",
            origin: "印度、巴西",
            hardness: "6.5-7.5"
        }
    ];
    
    let currentJadeIndex = 0;
    const currentJadeElement = document.getElementById('current-jade');
    const jadeNameElement = document.getElementById('jade-name');
    const jadeDescriptionElement = document.getElementById('jade-description');
    
    function updateJadeDisplay() {
        const jade = jadeData[currentJadeIndex];
        
        // 修正：使用本地图片路径，而不是占位图片
        currentJadeElement.src = jade.image; // 直接使用图片路径
        currentJadeElement.alt = jade.name;
        
        jadeNameElement.textContent = jade.name;
        jadeDescriptionElement.innerHTML = `
            ${jade.description}
            <br><small>产地: ${jade.origin} | 硬度: ${jade.hardness}</small>
        `;
    }
    
    // 事件监听
    document.getElementById('prev-jade').addEventListener('click', function() {
        currentJadeIndex = (currentJadeIndex - 1 + jadeData.length) % jadeData.length;
        updateJadeDisplay();
    });
    
    document.getElementById('next-jade').addEventListener('click', function() {
        currentJadeIndex = (currentJadeIndex + 1) % jadeData.length;
        updateJadeDisplay();
    });
    
    // 键盘导航
    document.addEventListener('keydown', function(event) {
        if (document.getElementById('appreciation').classList.contains('active')) {
            if (event.key === 'ArrowLeft') {
                document.getElementById('prev-jade').click();
            } else if (event.key === 'ArrowRight') {
                document.getElementById('next-jade').click();
            }
        }
    });
    
    // 图片加载失败处理
    currentJadeElement.addEventListener('error', function() {
        console.error('图片加载失败:', this.src);
        // 如果图片加载失败，使用占位图片
        const jade = jadeData[currentJadeIndex];
        this.src = `https://via.placeholder.com/800x400/${jade.color.substring(1)}/ffffff?text=${jade.name}`;
    });
    
    // 初始化显示
    updateJadeDisplay();
    
    console.log('玉石鉴赏模块已加载');
});