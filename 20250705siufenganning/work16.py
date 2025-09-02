import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW
from mgwr.utils import compare_surfaces
import libpysal as ps

# 读取shp文件
gdf = gpd.read_file(r'e:\work\sv_xiufenganning\20250819\街景视觉-类别情感.shp')

# 定义变量
factor_columns = ['Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 'ID_Vis', 'PubArt_Vis', 
                  'Arch_Vis', 'Histor_Vis', 'Faccon_Vis', 'Block_Vis', 'FacCol_Vis']
result_columns = ['文化感', '自然感', '娱乐感', '现代化', '人际情', '科教感']

# 数据预处理
def prepare_gwr_data(gdf, factors, result):
    """
    准备GWR分析数据
    """
    # 移除缺失值
    data = gdf.dropna(subset=factors + [result])
    
    # 获取坐标
    coords = list(zip(data.geometry.x, data.geometry.y))
    
    # 准备自变量和因变量
    X = data[factors].values
    y = data[result].values.reshape(-1, 1)
    
    return X, y, coords, data

# 执行GWR分析
def run_gwr_analysis(X, y, coords):
    """
    执行GWR分析并返回结果
    """
    # 选择最佳带宽
    selector = Sel_BW(coords, y, X)
    bw = selector.search()
    print(f"最佳带宽: {bw}")
    
    # 运行GWR模型
    gwr_model = GWR(coords, y, X, bw)
    gwr_results = gwr_model.fit()
    
    return gwr_results

# 可视化结果
def visualize_gwr_results(gdf, gwr_results, result_column):
    """
    可视化GWR分析结果
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    # 绘制R平方
    gdf.plot(column=gwr_results.localR2, ax=axes[0], 
             legend=True, cmap='viridis')
    axes[0].set_title(f'Local R² - {result_column}')
    
    # 绘制截距
    gdf.plot(column=gwr_results.params[:, 0], ax=axes[1], 
             legend=True, cmap='coolwarm')
    axes[1].set_title('Intercept')
    
    # 绘制系数（示例：第一个自变量）
    if gwr_results.params.shape[1] > 1:
        gdf.plot(column=gwr_results.params[:, 1], ax=axes[2], 
                 legend=True, cmap='RdYlBu_r')
        axes[2].set_title(f'Coefficient - {factor_columns[0]}')
    
    # 绘制t值
    gdf.plot(column=gwr_results.tvalues[:, 0], ax=axes[3], 
             legend=True, cmap='RdBu_r')
    axes[3].set_title('t-values (Intercept)')
    
    # 绘制残差
    gdf.plot(column=gwr_results.resid_response, ax=axes[4], 
             legend=True, cmap='RdYlBu_r')
    axes[4].set_title('Residuals')
    
    # 绘制预测值
    gdf.plot(column=gwr_results.predy, ax=axes[5], 
             legend=True, cmap='viridis')
    axes[5].set_title('Predicted Values')
    
    plt.tight_layout()
    plt.show()

# 主分析函数
def main_analysis():
    """
    主分析函数
    """
    results_summary = {}
    
    for result_col in result_columns:
        print(f"\n=== 正在分析: {result_col} ===")
        
        try:
            # 准备数据
            X, y, coords, valid_data = prepare_gwr_data(gdf, factor_columns, result_col)
            
            if len(valid_data) < 10:  # 确保有足够的数据点
                print(f"数据点不足 ({len(valid_data)})，跳过 {result_col}")
                continue
                
            # 运行GWR分析
            gwr_results = run_gwr_analysis(X, y, coords)
            
            # 保存结果到原始gdf
            result_gdf = gdf.copy()
            result_indices = valid_data.index
            result_gdf.loc[result_indices, f'{result_col}_pred'] = gwr_results.predy.flatten()
            result_gdf.loc[result_indices, f'{result_col}_resid'] = gwr_results.resid_response
            result_gdf.loc[result_indices, f'{result_col}_localR2'] = gwr_results.localR2
            
            # 存储结果
            results_summary[result_col] = {
                'results': gwr_results,
                'data': result_gdf,
                'bandwidth': gwr_results.bw,
                'R2_global': gwr_results.R2
            }
            
            # 打印摘要统计
            print(f"全局R²: {gwr_results.R2:.3f}")
            print(f"AICc: {gwr_results.aicc:.3f}")
            print(f"参数估计数量: {gwr_results.tr_S}")
            
            # 可视化结果
            visualize_gwr_results(result_gdf.loc[result_indices], gwr_results, result_col)
            
        except Exception as e:
            print(f"分析 {result_col} 时出错: {str(e)}")
            continue
    
    return results_summary

# 执行分析
if __name__ == "__main__":
    # 首先检查数据
    print("数据基本信息:")
    print(gdf.info())
    print("\n数据描述统计:")
    print(gdf[factor_columns + result_columns].describe())
    
    # 检查缺失值
    print("\n缺失值统计:")
    print(gdf[factor_columns + result_columns].isnull().sum())
    
    # 运行GWR分析
    all_results = main_analysis()
    
    # 输出总体结果摘要
    print("\n=== 总体分析结果摘要 ===")
    for result_col, summary in all_results.items():
        print(f"{result_col}: R²={summary['R2_global']:.3f}, "
              f"带宽={summary['bandwidth']:.3f}")