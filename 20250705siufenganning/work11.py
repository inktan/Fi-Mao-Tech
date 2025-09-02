# 指标汇总

# 指标项 指标选择依据 指标计算
# 环境美学
# 绿色可视率    绿色植物的比例强调绿化的立体视觉效果。
# 天空可视率    天空所占的比例，强调天空可视性的视觉效果。
# 河流可视率    中水体所占的比例，强调水体可视性的视觉效果。
# 裸露土地比例(BLR)     图片中裸地的比例反映了裸地的程度。
# 干扰物可见度(ID)      障碍物、堆积杂物、垃圾、管道、汽车等整体视觉比例的衡量。

# 文化表达
# 公共艺术可见频次      公共艺术装置（装置艺术、雕塑、彩色立面、壁画/涂鸦）
# 历史建筑可视率        文化建筑及相关构筑物（如传统屋顶/飞檐、历史建筑立面等）所占的比例
# 窗框与檐线保留度      检测窗框、檐线等传统构件完整性，对比现存建筑与理想模板的相似度
# 传统纹样出现率        目标检测识别门窗/瓦当等处传统图案的次数占比
# 门榴匾额可见度        OCR+目标检测定位门楣匾额区域并判断文字清晰度，评估历史招牌保存情况
# 多语言标识多样性      OCR识别不同语言文字种类数及其频次的Shannon多样性指数
# 地域特色建材可见度    材质分割识别具有地域标志性的石材、木构件等像素占比

# 视觉品质
# 立面连续性        建筑立面高度/色调/风格的标准差倒数，反映同一街区视觉过渡平滑度
# 街区辨识度        深度特征聚类后同一区域内立面/材质风格的内部相似度
# 立面色彩和谐度    提取街景中建筑立面主色块，计算色相/饱和度标准差，标准差越小表示越和谐
# 现代建筑可视率    肉眼所见现代建筑的比例（玻璃幕墙、金属/铝板外墙、商业综合体、摩天大楼立面）。
# 边界清晰度        边缘检测提取道路、河流、绿带等元素的边缘强度
# 路网引导性        可视体积分析行人视线沿道路移动时的可见障碍率

import geopandas as gpd

def calculate_green_visibility(input_shp, output_shp):
    gdf = gpd.read_file(input_shp)
    
    # 定义要处理的植被相关列（不区分大小写）
    # 计算绿色可视率（所有植被列的和）
    type_vis = 'Green_Vis'
    vegetation_columns = ['grass', 'tree', 'plant;flor', 'flower', 'palm;palm;']
    # type_vis = 'Sky_Vis'
    # vegetation_columns = ['sky']
    # type_vis = 'River_Vis'
    # vegetation_columns = ['river', 'water', 'sea', 'lake', 'waterfall']
    # type_vis = 'BLR_Vis'
    # vegetation_columns = ['earth;grou', 'dirt;track', 'sand', 'field', 'land;groun']
    # type_vis = 'ID_Vis'
    # vegetation_columns = ['box','ashcan;tra','poster;pos','buffet;cou','case;displ','car;auto;a','truck;moto',
    #                       'bus;autobu','boat','van','conveyer;b','minibike;m','railing;ra','fence;fenc','streetligh','pole',
    #                       'plaything;','apparel;we','chair','stool','barrel;cas','bicycle;bi']
    # type_vis = 'PubArt_Vis'
    # vegetation_columns = ['sculpture','painting;p','fountain','vase']
    # type_vis = 'Arch_Vis'
    # vegetation_columns = ['building','skyscraper','windowpane','glass','tower']

    # type_vis = 'FacCol_Vis'
    
    # 查找实际存在于数据中的列（不区分大小写）
    existing_cols = []
    for col in vegetation_columns:
        # 检查原列名（小写）
        if col in gdf.columns.str.lower():
            # 获取实际列名（保持原大小写）
            actual_col = gdf.columns[gdf.columns.str.lower() == col.lower()][0]
            existing_cols.append(actual_col)
        else:
            print(f"警告: 列 '{col}' 不存在于数据中")
    
    if not existing_cols:
        raise ValueError("错误: 数据中未找到任何植被相关列")

    gdf[type_vis] = gdf[existing_cols].sum(axis=1)
    
    # 删除原始植被列
    # gdf = gdf.drop(columns=existing_cols)
    
    # 保存结果到新SHP文件
    gdf.to_file(output_shp, encoding='utf-8')
    
    print(f"处理完成！结果已保存到: {output_shp}")
    print(f"新增的 {type_vis} 列统计信息:")
    print(gdf[type_vis].describe())

# 使用示例
if __name__ == "__main__":
    input_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result.shp"  # 输出文件路径
    input_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_01.shp"  # 输出文件路径
    input_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_02.shp"  # 输出文件路径
    input_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_03.shp"  # 输出文件路径
    input_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_04.shp"  # 输出文件路径
    input_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_05.shp"  # 输出文件路径
    input_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_06.shp"  # 输出文件路径
    input_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_07.shp"  # 输出文件路径
    output_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_08.shp"  # 输出文件路径
    
    calculate_green_visibility(input_file, output_file)

