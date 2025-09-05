import geopandas as gpd
import pandas as pd
import numpy as np
from mgwr.sel_bw import Sel_BW
from mgwr.gwr import GWR
from libpysal.weights import distance
import matplotlib.pyplot as plt
import warnings
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

# 设置中文显示
def set_chinese_font():
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 多个备选字体
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['text.usetex'] = False

set_chinese_font()

# 1. 数据加载和预处理
def load_and_preprocess_data(shp_path):
    """加载并预处理数据"""
    gdf = gpd.read_file(shp_path)
    
    # 确保坐标系是WGS84或其他投影坐标系
    if gdf.crs is None:
        gdf = gdf.set_crs('EPSG:4326')
    
    # 提取坐标
    coords = np.array([(geom.x, geom.y) for geom in gdf.geometry])
    
    # 定义自变量和因变量
    factor_columns = ['Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 'ID_Vis', 
                     'PubArt_Vis', 'Arch_Vis','Histor_Vis','Faccon_Vis','Block_Vis','FacCol_Vis']
    result_columns = ['文化感', '自然感', '娱乐感', '现代化', '人际情', '科教感']
    
    # 检查列是否存在
    missing_factors = [col for col in factor_columns if col not in gdf.columns]
    missing_results = [col for col in result_columns if col not in gdf.columns]
    
    if missing_factors:
        print(f"警告: 缺少以下自变量列: {missing_factors}")
        factor_columns = [col for col in factor_columns if col in gdf.columns]
    
    if missing_results:
        raise ValueError(f"缺少以下因变量列: {missing_results}")
    
    # 移除缺失值
    gdf = gdf.dropna(subset=factor_columns + result_columns)
    
    # 数据标准化（可选，但推荐）
    scaler = StandardScaler()
    for col in factor_columns:
        if col in gdf.columns:
            gdf[col] = scaler.fit_transform(gdf[[col]])
    
    for col in result_columns:
        if col in gdf.columns:
            gdf[col] = scaler.fit_transform(gdf[[col]])
    
    return gdf, coords, factor_columns, result_columns

# 2. GWR模型构建和拟合
def run_gwr_analysis(gdf, coords, factor_columns, result_columns):
    """执行GWR分析"""
    results = {}
    
    for target in result_columns:
        print(f"\n正在分析因变量: {target}")
        
        try:
            # 准备数据
            available_columns = [col for col in factor_columns if col in gdf.columns]
            if len(available_columns) != len(factor_columns):
                print(f"警告: 原始factor_columns中有 {len(factor_columns)} 列，但数据中只有 {len(available_columns)} 列可用")
                factor_columns = available_columns

            X = gdf[factor_columns].values.astype(float)
            y = gdf[target].values.astype(float).reshape(-1, 1)

            # 检查数据有效性
            if np.any(np.isnan(X)) or np.any(np.isnan(y)):
                print("警告: 数据中存在NaN值，正在处理...")
                valid_indices = ~(np.isnan(X).any(axis=1) | np.isnan(y).flatten())
                X = X[valid_indices]
                y = y[valid_indices]
                coords_subset = coords[valid_indices]
            else:
                coords_subset = coords

            if X.shape[1] == len(available_columns) + 1:
                print("检测到截距项，自动移除最后一列")
                X = X[:, :-1]  # 移除最后一列（截距项）

            # 选择带宽
            print("正在选择最优带宽...")
            
            # 手动处理维度问题：确保X不包含截距项
            # MGWR会自动添加截距，所以不需要在X中包含常数项
            selector = Sel_BW(coords_subset, y, X, fixed=False, kernel='gaussian')
            bw = selector.search(verbose=True)
            print(f"最优带宽: {bw:.4f}")
            
            # 拟合GWR模型
            print("正在拟合GWR模型...")
            model = GWR(coords_subset, y, X, bw, kernel='gaussian', fixed=False)
            gwr_results = model.fit()
            
            # 存储结果
            results[target] = {
                'model': model,
                'results': gwr_results,
                'bw': bw,
                'params': gwr_results.params,
                'tvalues': gwr_results.tvalues,
                'localR2': gwr_results.localR2,
                'coords': coords_subset,
                'valid_indices': valid_indices if 'valid_indices' in locals() else None
            }
            
            print(f"{target}分析完成 - 样本数: {len(y)}")
            
        except Exception as e:
            print(f"分析{target}时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    return results

# 3. 结果处理和可视化
def process_and_visualize_results(gdf, results, factor_columns):
    """处理并可视化结果"""
    gdf_with_results = gdf.copy()
    
    for target, res in results.items():
        try:
            # 处理有效索引（如果有数据清理）
            if res['valid_indices'] is not None:
                # 创建新的列并初始化为NaN
                gdf_with_results[f'{target}_localR2'] = np.nan
                gdf_with_results.loc[res['valid_indices'], f'{target}_localR2'] = res['localR2']
                
                # 为每个自变量添加系数
                for i, factor in enumerate(factor_columns):
                    coef_col = f'{target}_{factor}_coef'
                    tval_col = f'{target}_{factor}_tval'
                    gdf_with_results[coef_col] = np.nan
                    gdf_with_results[tval_col] = np.nan
                    gdf_with_results.loc[res['valid_indices'], coef_col] = res['params'][:, i]
                    gdf_with_results.loc[res['valid_indices'], tval_col] = res['tvalues'][:, i]
            else:
                # 所有数据都有效的情况
                gdf_with_results[f'{target}_localR2'] = res['localR2']
                for i, factor in enumerate(factor_columns):
                    gdf_with_results[f'{target}_{factor}_coef'] = res['params'][:, i]
                    gdf_with_results[f'{target}_{factor}_tval'] = res['tvalues'][:, i]
            
            # 可视化局部R²
            # fig, ax = plt.subplots(figsize=(12, 10))
            # plot_data = gdf_with_results.dropna(subset=[f'{target}_localR2'])
            # if not plot_data.empty:
            #     plot_data.plot(column=f'{target}_localR2', 
            #                 legend=True, 
            #                 cmap='RdYlBu_r',
            #                 scheme='quantiles',
            #                 k=5,
            #                 ax=ax,
            #                 legend_kwds={'loc': 'lower right'})
            #     ax.set_title(f'{target} - 局部R²分布', fontsize=16)
            #     ax.set_axis_off()
            #     plt.tight_layout()
            #     plt.savefig(f'{target}_localR2.png', dpi=300, bbox_inches='tight')
            #     plt.close()
            
            # 打印摘要统计
            print(f"\n{target} - GWR结果摘要:")
            print(f"平均局部R²: {np.nanmean(res['localR2']):.4f}")
            print(f"局部R²范围: {np.nanmin(res['localR2']):.4f} - {np.nanmax(res['localR2']):.4f}")
            print(f"带宽: {res['bw']:.4f}")
            
            # 打印系数统计
            print("\n系数统计:")
            coef_df = pd.DataFrame(res['params'][:-1], columns=['Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 'ID_Vis', 
                     'PubArt_Vis', 'Arch_Vis','Histor_Vis','Faccon_Vis','Block_Vis','FacCol_Vis','_Vis'])
            print(coef_df.describe())
            
        except Exception as e:
            print(f"处理{target}结果时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    return gdf_with_results

# 4. 主函数
def main():
    # 文件路径
    shp_path = r'e:\work\sv_xiufenganning\20250819\街景视觉-类别情感.shp'
    
    try:
        # 加载和预处理数据
        gdf, coords, factor_columns, result_columns = load_and_preprocess_data(shp_path)
        print(f"数据加载成功，共{len(gdf)}个观测点")
        print(f"自变量: {factor_columns}")
        print(f"因变量: {result_columns}")
        
        # 运行GWR分析
        results = run_gwr_analysis(gdf, coords, factor_columns, result_columns)
        
        if not results:
            print("没有成功完成任何GWR分析")
            return
        
        # 处理和可视化结果
        gdf_with_results = process_and_visualize_results(gdf, results, factor_columns)
        
        # 保存结果
        output_path = r'e:\work\sv_xiufenganning\20250819\街景视觉-类别情感_GWR结果.shp'
        gdf_with_results.to_file(output_path, encoding='utf-8')
        print(f"\n结果已保存到: {output_path}")
        
        # 保存系数统计摘要
        summary_data = []
        for target, res in results.items():
            coef_df = pd.DataFrame(res['params'], columns=factor_columns)
            stats = coef_df.describe()
            stats['target'] = target
            stats['bandwidth'] = res['bw']
            stats['mean_localR2'] = np.mean(res['localR2'])
            summary_data.append(stats)
        
        summary_df = pd.concat(summary_data)
        summary_df.to_excel(r'e:\work\sv_xiufenganning\20250819\GWR_系数统计.xlsx')
        print("系数统计已保存到Excel文件")
        
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()