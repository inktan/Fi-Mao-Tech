import geopandas as gpd
from pyproj import CRS, Transformer

def calculate_geom_properties(shp_path):
    """
    读取SHP文件，提取第一个面几何，计算面积和边长（米单位）
    
    参数:
        shp_path (str): SHP文件路径
        
    返回:
        dict: 包含面积和周长的字典（单位：平方米和米）
    """
    # 读取SHP文件
    gdf = gpd.read_file(shp_path)
    
    # 检查是否有几何数据
    if len(gdf) == 0:
        raise ValueError("SHP文件中没有几何数据")
    
    # 获取第一个面几何
    first_geom = gdf.geometry.iloc[1]
    
    # 检查是否是面几何
    if not first_geom.geom_type in ['Polygon', 'MultiPolygon']:
        raise ValueError("第一个几何不是面类型")
    
    # 获取原始CRS
    original_crs = gdf.crs
    
    # 如果CRS是地理坐标系（经纬度），需要转换为投影坐标系
    if original_crs is None:
        raise ValueError("SHP文件缺少坐标参考系统(CRS)信息")
    
    if original_crs.is_geographic:
        # 自动确定合适的UTM投影
        centroid = first_geom.centroid
        utm_zone = int((centroid.x + 180) / 6) + 1
        utm_crs = CRS.from_dict({
            'proj': 'utm',
            'zone': utm_zone,
            'ellps': 'WGS84',
            'south': centroid.y < 0,
            'units': 'm'
        })
        
        # 转换到UTM坐标系
        gdf_utm = gdf.to_crs(utm_crs)
        first_geom_utm = gdf_utm.geometry.iloc[0]
        
        # 计算面积和周长
        area = first_geom_utm.area
        perimeter = first_geom_utm.length
    else:
        # 已经是投影坐标系，直接计算
        area = first_geom.area
        perimeter = first_geom.length
        
        # 检查单位是否是米
        if not original_crs.axis_info[0].unit_name.lower().startswith('metre'):
            # 如果不是米，转换为米
            transformer = Transformer.from_crs(original_crs, original_crs, always_xy=True)
            # 对于面积和长度，需要知道转换因子
            # 这里简化处理，实际应根据CRS确定转换因子
            unit = original_crs.axis_info[0].unit_name
            print(f"警告: 原始CRS单位不是米，而是{unit}. 结果可能不准确.")
    
    return {
        'area_sqm': area,
        'perimeter_m': perimeter,
        'crs': str(gdf.crs)
    }

# 示例使用
if __name__ == "__main__":
    shp_file = r"e:\work\sv_shushu\所有指标\six_sv_count_res1001.shp"  # 替换为你的SHP文件路径
    shp_file = r"e:\work\sv_shushu\所有指标\six_sv_count01.shp"  # 替换为你的SHP文件路径
    
    try:
        results = calculate_geom_properties(shp_file)
        print(f"几何属性 (米制单位):")
        print(f"面积: {results['area_sqm']:.2f} 平方米")
        print(f"边长: {results['perimeter_m']:.2f} 米")
        print(f"原始CRS: {results['crs']}")
    except Exception as e:
        print(f"处理SHP文件时出错: {str(e)}")