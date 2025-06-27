import geopandas as gpd
def classify_street(functions):
    """
    根据街道两侧功能分布确定街道类型
    
    参数:
        functions: list - 包含功能类型字符串的列表
        
    返回:
        str - 街道分类结果
    """
    # 定义功能权重 (基于对街道特征的影响程度)
    WEIGHTS = {
        'Public service': 1.3,  # 公共服务设施对街道影响较大
        'Residence': 1.0,       # 基准权重
        'Business': 1.6,       # 商业活动对街道活力影响显著
        'Office': 1.4,
        'Industry': 0.7,       # 工业功能对街道品质影响相对较小
        'Other': 0.5           # 其他功能影响较小
    }
    
    # 处理空列表情况
    if not functions:
        return 'Traffic'
    
    # 统计各功能出现次数
    from collections import defaultdict
    func_counts = defaultdict(int)
    for func in functions:
        func_counts[func] += 1
    
    # 计算加权得分
    weighted_scores = {}
    total_score = 0
    for func, count in func_counts.items():
        weight = WEIGHTS.get(func, 0.5)  # 默认权重0.5
        weighted_scores[func] = count * weight
        total_score += count * weight
    
    # 如果总得分为0(理论上不应发生)，返回交通型
    if total_score == 0:
        return 'Traffic'
    
    # 找出主导功能
    dominant_func, dominant_score = max(weighted_scores.items(), key=lambda x: x[1])
    dominant_ratio = dominant_score / total_score
    
    # 确定街道类型
    if dominant_ratio >= 0.5:
        # 单一主导功能型
        return dominant_func
    elif dominant_ratio >= 0.3:
        # 主导功能明显的混合型
        # return f'Mixed-{dominant_func}'
        return f'Mixed'
    else:
        # 均衡混合型
        return 'Mixed'
    
# for address in ['拉萨', '山南', '林芝']:
for address in ['山南', '林芝']:
        
    polygons_gdf = gpd.read_file(r"f:\立方数据\2024年我国多属性建筑矢量数据（免费获取）\合并后的数据（一个省份合并为一个shp文件）\西藏自治区\西藏自治区.shp")
    lines_gdf = gpd.read_file(f'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines01\{address}市.shp')

    polygons_gdf = polygons_gdf.to_crs(epsg=32633)  # 使用适合你区域的UTM EPSG代码
    lines_gdf = lines_gdf.to_crs(epsg=32633)  # 使用适合你区域的UTM EPSG代码

    # 检查 "Function" 列是否存在
    if "Function" in polygons_gdf.columns:
        # 获取 "Function" 列的唯一值
        unique_functions = polygons_gdf["Function"].unique()
        print(f"Function 列中的唯一值数量: {(unique_functions)}")
        # ['Public service' 'Residence' 'Other' 'Business' 'Office' 'Industry']

    function_lists = []
    for idx, line in lines_gdf.iterrows():
        # Get the geometry from the row
        line_geom = lines_gdf.geometry.iloc[idx]
        
        # 4. 创建100米的缓冲区
        buffer_distance = 30  # 单位是米（因为使用了投影坐标系）
        line_buffer = line_geom.buffer(buffer_distance)
        nearby_polygons = polygons_gdf[polygons_gdf.intersects(line_buffer)]
        
        function_list = nearby_polygons['Function'].tolist()
        
        # 计算并输出线要素长度
        line_length = line_geom.length
        # print(f"Line {idx} 长度: {line_length:.2f} 米")  # 保留两位小数
        # print(len(function_list))
        
        result = classify_street(function_list)
        # print(result)
        if  len(function_list)/line_length< 0.001:
            result = 'Traffic'

        function_lists.append(result)

    # 将function列表添加到lines_gdf中
    lines_gdf['Function'] = function_lists

    lines_gdf = lines_gdf.to_crs(epsg=4326)  # 使用适合你区域的UTM EPSG代码
    lines_gdf.to_file(f'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines01\{address}市_Function.shp') 


