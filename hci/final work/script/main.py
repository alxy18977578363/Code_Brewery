"""
Chennai Restaurant Dataset - Exploratory Data Analysis (EDA)
钦奈餐厅数据集 - 探索性数据分析

主程序：协调所有模块，执行完整的EDA流程

使用方法:
    python src/main.py (从项目根目录)
    或
    python run_eda.py (从项目根目录)
"""

import warnings
import pandas as pd
from pathlib import Path

# 导入配置和工具
from config import configure_matplotlib, PALETTE
warnings.filterwarnings("ignore")

# 导入数据加载模块
from data_loader import load_datasets, check_data_integrity

# 导入数据处理模块
from data_processor import (
    preprocess_dataframe,
    create_long_format_data,
    get_quality_metrics,
    get_attribute_summary,
)

# 导入分析模块
from analysis import RestaurantAnalyzer, generate_eda_report

# 导入可视化模块
from visualizations import (
    plot_scorecard,
    plot_segment_analysis,
    plot_rating_ridgelines,
    plot_cuisine_and_dishes,
    plot_feature_heatmap,
    plot_area_analysis,
    plot_spatial_distribution,
    plot_chain_footprints,
)


def main():
    """
    主程序 - 执行完整EDA流程
    """
    
    # 设置输出目录
    project_root = Path(__file__).parent.parent
    charts_dir = project_root / "outputs" / "charts"
    data_dir = project_root / "outputs" / "data"
    reports_dir = project_root / "outputs" / "reports"
    
    charts_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 80)
    print("🍽️  钦奈餐厅数据集 - 探索性数据分析 (EDA)")
    print("=" * 80)
    
    # ========================================================================
    # 1. 配置
    # ========================================================================
    print("\n[1/8] 配置matplotlib视觉样式...")
    configure_matplotlib()
    print("✓ 美食主题调色板已加载")
    
    # ========================================================================
    # 2. 数据加载
    # ========================================================================
    print("\n[2/8] 加载数据集...")
    raw, segmented = load_datasets()
    
    # ========================================================================
    # 3. 数据质量检查
    # ========================================================================
    print("\n[3/8] 检查数据完整性...")
    health = check_data_integrity(raw, segmented)
    print("✓ 数据完整性检查完成")
    print(health['integrity'])
    
    # ========================================================================
    # 4. 数据预处理
    # ========================================================================
    print("\n[4/8] 数据预处理和规范化...")
    df = preprocess_dataframe(raw)
    print(f"✓ 已处理 {len(df):,} 行餐厅数据")
    print("\n关键质量指标:")
    metrics = get_quality_metrics(df)
    print(metrics)
    
    # ========================================================================
    # 5. 多值属性展开
    # ========================================================================
    print("\n[5/8] 展开多值属性 (菜系、特色、菜品)...")
    long_format_data = create_long_format_data(df)
    attr_summary = get_attribute_summary(long_format_data)
    print("✓ 属性展开完成")
    print(attr_summary)
    
    # ========================================================================
    # 6. 数据分析
    # ========================================================================
    print("\n[6/8] 执行多维度分析...")
    analyzer = RestaurantAnalyzer(df, long_format_data)
    report = generate_eda_report(analyzer)
    print("✓ 分析完成，生成了以下报告:")
    print(f"  - 市场细分分析: {len(report['segment_analysis'])} 个细分市场")
    print(f"  - 地区分析: {len(report['area_analysis'])} 个地区")
    print(f"  - 菜系分析: {len(report['cuisine_analysis'])} 种菜系")
    print(f"  - 品牌足迹: {len(report['chain_analysis'])} 个多出口品牌")
    
    # ========================================================================
    # 7. 可视化生成
    # ========================================================================
    print("\n[7/8] 生成可视化图表...")
    
    # 7.1 评分卡
    print("  - 生成前厅服务评分卡...")
    fig1 = plot_scorecard(df, long_format_data)
    fig1.savefig(str(charts_dir / "01_scorecard.png"), dpi=150, bbox_inches="tight")
    print("    ✓ 已保存: outputs/charts/01_scorecard.png")
    
    # 7.2 市场细分
    print("  - 生成市场细分分析图...")
    fig2 = plot_segment_analysis(analyzer)
    fig2.savefig(str(charts_dir / "02_segment_analysis.png"), dpi=150, bbox_inches="tight")
    print("    ✓ 已保存: outputs/charts/02_segment_analysis.png")
    
    # 7.3 评分脊线
    print("  - 生成评分脊线图...")
    fig3 = plot_rating_ridgelines(analyzer)
    fig3.savefig(str(charts_dir / "03_rating_ridgelines.png"), dpi=150, bbox_inches="tight")
    print("    ✓ 已保存: outputs/charts/03_rating_ridgelines.png")
    
    # 7.4 菜系和菜品
    print("  - 生成菜系和菜品分析图...")
    fig4 = plot_cuisine_and_dishes(analyzer)
    fig4.savefig(str(charts_dir / "04_cuisine_and_dishes.png"), dpi=150, bbox_inches="tight")
    print("    ✓ 已保存: outputs/charts/04_cuisine_and_dishes.png")
    
    # 7.5 特色热力图
    print("  - 生成服务特色热力图...")
    fig5 = plot_feature_heatmap(analyzer)
    fig5.savefig(str(charts_dir / "05_feature_heatmap.png"), dpi=150, bbox_inches="tight")
    print("    ✓ 已保存: outputs/charts/05_feature_heatmap.png")
    
    # 7.6 地区分析
    print("  - 生成地区分析图...")
    fig6 = plot_area_analysis(analyzer)
    fig6.savefig(str(charts_dir / "06_area_analysis.png"), dpi=150, bbox_inches="tight")
    print("    ✓ 已保存: outputs/charts/06_area_analysis.png")
    
    # 7.7 空间分布
    print("  - 生成地理空间分布图...")
    fig7 = plot_spatial_distribution(analyzer)
    fig7.savefig(str(charts_dir / "07_spatial_distribution.png"), dpi=150, bbox_inches="tight")
    print("    ✓ 已保存: outputs/charts/07_spatial_distribution.png")
    
    # 7.8 品牌足迹
    print("  - 生成品牌足迹分析图...")
    fig8 = plot_chain_footprints(analyzer)
    fig8.savefig(str(charts_dir / "08_chain_footprints.png"), dpi=150, bbox_inches="tight")
    print("    ✓ 已保存: outputs/charts/08_chain_footprints.png")
    
    # ========================================================================
    # 8. 关键洞察总结
    # ========================================================================
    print("\n[8/8] 生成EDA洞察总结...")
    
    insights = report["insights"]
    top_segment = insights["top_segment"]
    best_segment = insights["best_segment"]
    top_area = insights["top_area"]
    top_cuisine = insights["top_cuisine"]
    top_feature = insights["top_feature"]
    top_dish = insights["top_dish"]
    
    notes = f"""
# Chennai Restaurant Dataset - EDA 关键洞察

## 📊 数据概览
- **总餐厅数**: {insights['total_restaurants']:,} 家餐厅，覆盖 **{insights['total_areas']}** 个地区
- **市场细分**: **{insights['total_segments']}** 种业态类型
- **评分分布**: 均值 **{insights['mean_rating']:.2f}**，中位数 **{insights['median_rating']:.1f}**

## 🏪 市场细分洞察
- **规模最大**: **{top_segment}** 细分，拥有 **{insights['top_segment_outlets']:,.0f}** 家出口
- **质量最高**: **{best_segment}** 细分，平均评分 **{insights['best_segment_rating']:.2f}**

## 📍 地区洞察
- **最高密度**: **{top_area}** 拥有 **{insights['top_area_outlets']:,.0f}** 家餐厅
- 这表明该地区市场高度饱和，竞争激烈

## 🍜 菜系洞察
- **最常见菜系**: **{top_cuisine}**
- 多标签菜系体系反映了钦奈餐饮的多样性和融合特征

## 🎁 服务特色洞察
- **最常见特色**: **{top_feature}**
- 表明外卖/配送服务在城市餐饮中的主导地位

## 🍽️ 菜品洞察
- **最常见菜品**: **{top_dish}**
- 菜品词汇高度本地化，反映了钦奈的饮食文化特色

## 💡 建模建议
推荐的特征工程方向：
1. **地理特征**: 细分市场、地区、多样性指数、坐标聚类
2. **品牌特征**: 同名出口、品牌足迹、连锁程度
3. **文本特征**: 菜系标签、服务特色、菜品词汇
4. **交互特征**: 地区×细分市场、菜系×评分等

## 📈 后续步骤
1. 特征工程与预处理
2. 构建评分预测模型
3. 开发推荐引擎
4. 餐厅定位优化分析
"""
    
    print("\n" + "=" * 80)
    print("✓ EDA分析完成!")
    print("=" * 80)
    print("\n" + notes)
    
    # 保存洞察到文件
    insights_file = reports_dir / "EDA_INSIGHTS.md"
    with open(insights_file, "w", encoding="utf-8") as f:
        f.write(notes)
    print("\n✓ 洞察已保存到: outputs/reports/EDA_INSIGHTS.md")
    
    # 保存详细报告到CSV
    print("\n保存详细分析报告...")
    report["segment_analysis"].to_csv(str(data_dir / "segment_analysis.csv"), index=False)
    report["area_analysis"].to_csv(str(data_dir / "area_analysis.csv"), index=False)
    report["cuisine_analysis"].to_csv(str(data_dir / "cuisine_analysis.csv"), index=False)
    report["chain_analysis"].to_csv(str(data_dir / "chain_analysis.csv"), index=False)
    print("✓ 所有CSV文件已保存到 outputs/data/")
    
    print("\n" + "=" * 80)
    print("📁 生成的文件:")
    print("  图表 (outputs/charts/):")
    print("    - 01_scorecard.png")
    print("    - 02_segment_analysis.png")
    print("    - 03_rating_ridgelines.png")
    print("    - 04_cuisine_and_dishes.png")
    print("    - 05_feature_heatmap.png")
    print("    - 06_area_analysis.png")
    print("    - 07_spatial_distribution.png")
    print("    - 08_chain_footprints.png")
    print("  数据 (outputs/data/):")
    print("    - segment_analysis.csv")
    print("    - area_analysis.csv")
    print("    - cuisine_analysis.csv")
    print("    - chain_analysis.csv")
    print("  报告 (outputs/reports/):")
    print("    - EDA_INSIGHTS.md")
    print("=" * 80)


if __name__ == "__main__":
    main()
