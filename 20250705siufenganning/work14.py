
# 因子数据
# columns_to_keep = ['地点', '地址', 'Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 'ID_Vis', 'PubArt_Vis','Arch_Vis']

# 结果数据
# 历史 艺术_文 建筑 跨文化 人工景 自然景 动物 活动 设施_场 饮食 技术 商业 友谊 爱情 亲子 高校 知识与 文化感 自然感 娱乐感 现代化 人际情 科教感

# 因子数据
# columns_to_keep = ['地点', '地址', 'Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 'ID_Vis', 'PubArt_Vis','Arch_Vis']

# 结果数据
# 历史 艺术_文 建筑 跨文化 人工景 自然景 动物 活动 设施_场 饮食 技术 商业 友谊 爱情 亲子 高校 知识与 文化感 自然感 娱乐感 现代化 人际情 科教感

import geopandas as gpd
import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import statsmodels.api as sm

# 1. 读取shp文件
print("正在读取shp文件...")
try:
    gdf = gpd.read_file(r'e:\work\sv_xiufenganning\20250819\街景视觉-类别情感.shp')  # 请将'your_file.shp'替换为实际文件路径
    print("文件读取成功！")
except Exception as e:
    print(f"读取文件时出错: {e}")
    exit()

# 2. 检查所需的列是否存在
factor_columns = ['Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 'ID_Vis', 'PubArt_Vis', 'Arch_Vis','Histor_Vis','Faccon_Vis','Block_Vis','FacCol_Vis']
result_columns = ['文化感', '自然感', '娱乐感', '现代化', '人际情', '科教感']

required_columns = factor_columns + result_columns
missing_columns = [col for col in required_columns if col not in gdf.columns]

if missing_columns:
    print(f"缺少以下列: {missing_columns}")
    print(f"文件中存在的列: {list(gdf.columns)}")
    exit()

# 3. 提取需要的列数据
print("提取数据...")
factors = gdf[factor_columns]
results = gdf[result_columns]

# 4. 数据基本信息
print(f"\n数据基本信息:")
print(f"样本数量: {len(gdf)}")
print(f"\n自变量描述性统计:")
print(factors.describe())
print(f"\n因变量描述性统计:")
print(results.describe())

# 5. 检查缺失值
print(f"\n缺失值检查:")
print("自变量缺失值:")
print(factors.isnull().sum())
print("因变量缺失值:")
print(results.isnull().sum())

# 如果有缺失值，删除含有缺失值的行
if factors.isnull().any().any() or results.isnull().any().any():
    print("存在缺失值，正在删除含有缺失值的行...")
    complete_data = pd.concat([factors, results], axis=1).dropna()
    factors = complete_data[factor_columns]
    results = complete_data[result_columns]
    print(f"删除缺失值后剩余样本数量: {len(complete_data)}")

# 6. 相关性分析
print(f"\n=== 相关性分析 ===")

# 计算皮尔逊相关系数
correlation_matrix = pd.concat([factors, results], axis=1).corr()

# 输出每个因变量与自变量的相关系数
for result_col in result_columns:
    print(f"\n{result_col} 与自变量的皮尔逊相关系数:")
    corr_results = correlation_matrix[result_col].drop(result_columns).sort_values(ascending=False)
    for var, corr in corr_results.items():
        print(f"  {var}: {corr:.4f}")

# 7. 多元线性回归分析
print(f"\n=== 多元线性回归分析 ===")

# 为每个因变量进行回归分析
for result_col in result_columns:
    print(f"\n--- {result_col} 回归分析 ---")
    
    # 准备数据
    X = factors.copy()
    y = results[result_col].copy()
    
    # 添加常数项
    X = sm.add_constant(X)
    
    # 构建模型
    model = sm.OLS(y, X).fit()
    
    # 输出回归结果
    print(model.summary())
    
    # 变量重要性分析
    print(f"\n{result_col} 变量重要性分析:")
    # 计算标准化系数
    std_coef = model.params[1:] * factors.std() / y.std()
    std_coef = std_coef.sort_values(ascending=False)
    
    print("标准化系数（重要性排序）:")
    for var, coef in std_coef.items():
        print(f"  {var}: {coef:.4f}")
    
    print("-" * 50)

# 8. 输出主要结果汇总
print(f"\n=== 主要结果汇总 ===")

# 创建结果汇总表
summary_results = []

for result_col in result_columns:
    # 准备数据
    X = factors.copy()
    y = results[result_col].copy()
    X = sm.add_constant(X)
    
    # 构建模型
    model = sm.OLS(y, X).fit()
    
    # 提取关键指标
    for factor in factor_columns:
        if factor in model.params:
            coef = model.params[factor]
            p_value = model.pvalues[factor]
            significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
            
            summary_results.append({
                '因变量': result_col,
                '自变量': factor,
                '系数': coef,
                'p值': p_value,
                '显著性': significance,
                'R²': model.rsquared
            })

# 转换为DataFrame并输出
summary_df = pd.DataFrame(summary_results)
print("\n回归结果汇总表:")
print(summary_df.to_string(index=False))

# 9. 输出每个因变量的最佳预测变量
print(f"\n=== 各因变量的最佳预测变量 ===")

for result_col in result_columns:
    # 准备数据
    X = factors.copy()
    y = results[result_col].copy()
    X = sm.add_constant(X)
    
    # 构建模型
    model = sm.OLS(y, X).fit()
    
    # 找出最显著的预测变量
    significant_vars = []
    for factor in factor_columns:
        if factor in model.pvalues and model.pvalues[factor] < 0.05:
            significant_vars.append((factor, model.params[factor], model.pvalues[factor]))
    
    # 按系数绝对值排序
    significant_vars.sort(key=lambda x: abs(x[1]), reverse=True)
    
    print(f"\n{result_col} 的显著预测变量 (p < 0.05):")
    if significant_vars:
        for var, coef, p_val in significant_vars:
            print(f"  {var}: 系数={coef:.4f}, p值={p_val:.4f}")
    else:
        print("  无显著预测变量")

print(f"\n分析完成！总共分析了 {len(result_columns)} 个因变量。")