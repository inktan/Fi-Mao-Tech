import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler

# 1. 读取SHP文件
factor_gdf = gpd.read_file(r'e:\work\sv_xiufenganning\20250819\街景视觉因子.shp')  # 替换为你的因子文件路径
result_gdf = gpd.read_file(r'e:\work\sv_xiufenganning\20250819\类别情感-逐地点统计.shp')  # 替换为你的结果文件路径

# 2. 数据探索和预处理
print("因子文件信息:")
print(factor_gdf.info())
print("\n结果文件信息:")
print(result_gdf.info())

# 检查并处理缺失值
factor_gdf = factor_gdf.dropna()
result_gdf = result_gdf.dropna()

# 3. 空间连接 - 修正后的版本
# 使用 predicate 参数代替 op
try:
    # 新版本GeoPandas使用 predicate
    joined_gdf = gpd.sjoin(factor_gdf, result_gdf, how='inner', predicate='intersects')
except TypeError:
    try:
        # 如果仍然报错，尝试使用 op（某些中间版本）
        joined_gdf = gpd.sjoin(factor_gdf, result_gdf, how='inner', op='intersects')
    except:
        # 如果都不行，可能版本很旧，使用默认参数
        joined_gdf = gpd.sjoin(factor_gdf, result_gdf, how='inner')
        print("使用默认的空间连接参数")

print(f"空间连接后共有 {len(joined_gdf)} 个要素")

# 4. 提取数值型列进行相关性分析
# 选择数值型列
factor_numeric = factor_gdf.select_dtypes(include=[np.number])
result_numeric = result_gdf.select_dtypes(include=[np.number])

# 5. 计算相关性
if len(factor_numeric.columns) > 0 and len(result_numeric.columns) > 0:
    print("\n因子文件数值列:", factor_numeric.columns.tolist())
    print("结果文件数值列:", result_numeric.columns.tolist())
    
    # 计算所有可能的组合的相关性
    correlations = {}
    for factor_col in factor_numeric.columns:
        for result_col in result_numeric.columns:
            # 确保两个列有相同数量的非空值
            valid_indices = factor_numeric[factor_col].notna() & result_numeric[result_col].notna()
            valid_count = sum(valid_indices)
            
            if valid_count > 10:  # 确保有足够的数据点
                corr = np.corrcoef(factor_numeric[factor_col][valid_indices], 
                                  result_numeric[result_col][valid_indices])[0, 1]
                correlations[f"{factor_col} vs {result_col}"] = {
                    'correlation': corr,
                    'sample_size': valid_count
                }
            else:
                print(f"警告: {factor_col} 和 {result_col} 的有效数据点不足 ({valid_count})")
                
    # 显示相关性结果
    print("\n=== 相关性分析结果 ===")
    for pair, stats in correlations.items():
        print(f"{pair}: 相关系数 = {stats['correlation']:.4f}, 样本数 = {stats['sample_size']}")
        
    # 可视化相关性矩阵
    if len(correlations) > 0:
        # 创建相关性数据框
        corr_data = []
        for pair, stats in correlations.items():
            factor, result = pair.split(' vs ')
            corr_data.append({
                'factor': factor,
                'result': result,
                'correlation': stats['correlation']
            })
        
        corr_df = pd.DataFrame(corr_data)
        
        # 创建热图
        pivot_table = corr_df.pivot(index='factor', columns='result', values='correlation')
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table, annot=True, cmap='coolwarm', center=0, 
                   vmin=-1, vmax=1, fmt='.3f')
        plt.title('因子与结果变量相关性热图')
        plt.tight_layout()
        plt.show()
        
else:
    print("没有找到足够的数值型列进行相关性分析")

# 6. 回归分析示例
if len(factor_numeric.columns) > 0 and len(result_numeric.columns) > 0:
    # 选择第一个数值列进行分析
    factor_col = factor_numeric.columns[0]
    result_col = result_numeric.columns[0]
    
    valid_indices = factor_numeric[factor_col].notna() & result_numeric[result_col].notna()
    x = factor_numeric[factor_col][valid_indices]
    y = result_numeric[result_col][valid_indices]
    
    if len(x) > 10:
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        print(f"\n=== 回归分析: {factor_col} 对 {result_col} ===")
        print(f"R²值: {r_value**2:.4f}")
        print(f"P值: {p_value:.4f}")
        print(f"回归方程: y = {intercept:.4f} + {slope:.4f}x")
        
        # 绘制回归图
        plt.figure(figsize=(10, 6))
        plt.scatter(x, y, alpha=0.6, s=50)
        plt.plot(x, intercept + slope*x, 'r', linewidth=2, 
                label=f'y = {intercept:.2f} + {slope:.2f}x\nR² = {r_value**2:.3f}')
        plt.xlabel(factor_col, fontsize=12)
        plt.ylabel(result_col, fontsize=12)
        plt.title(f'{factor_col} 与 {result_col} 的回归分析', fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.show()
    else:
        print(f"回归分析: 有效数据点不足 ({len(x)})")

# 7. 空间可视化比较
print("\n=== 空间分布可视化 ===")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# 因子分布
if len(factor_numeric.columns) > 0:
    factor_col = factor_numeric.columns[0]
    factor_gdf.plot(column=factor_col, ax=ax1, legend=True, 
                   cmap='viridis', markersize=50 if factor_gdf.geometry.type.iloc[0] == 'Point' else None)
    ax1.set_title(f'因子分布 - {factor_col}', fontsize=12)
else:
    factor_gdf.plot(ax=ax1, color='blue')
    ax1.set_title('因子几何分布', fontsize=12)

# 结果分布
if len(result_numeric.columns) > 0:
    result_col = result_numeric.columns[0]
    result_gdf.plot(column=result_col, ax=ax2, legend=True, 
                   cmap='plasma', markersize=50 if result_gdf.geometry.type.iloc[0] == 'Point' else None)
    ax2.set_title(f'结果分布 - {result_col}', fontsize=12)
else:
    result_gdf.plot(ax=ax2, color='red')
    ax2.set_title('结果几何分布', fontsize=12)

plt.tight_layout()
plt.show()

# 8. 基本统计信息
print("\n=== 基本统计信息 ===")
if len(factor_numeric.columns) > 0:
    print("因子变量统计:")
    print(factor_numeric.describe())
    
if len(result_numeric.columns) > 0:
    print("\n结果变量统计:")
    print(result_numeric.describe())

# 检查坐标系是否一致
print(f"\n坐标系检查:")
print(f"因子文件CRS: {factor_gdf.crs}")
print(f"结果文件CRS: {result_gdf.crs}")
if factor_gdf.crs != result_gdf.crs:
    print("警告: 两个文件的坐标系不一致，可能影响空间分析结果")
else:
    print("坐标系一致")






    