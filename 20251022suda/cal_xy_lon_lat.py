import numpy as np

class CoordinateTransformer:
    def __init__(self):
        # 已知的对应点
        self.lon_lat_points = np.array([
            [121.48601562675833, 31.243482916700415],
            [121.49685342010306, 31.243482916700415],
            [121.48601562675833, 31.23426944792221],
            [121.49685342010306, 31.23426944792221]
        ])
        
        self.xy_points = np.array([
            [27441, 13387],
            [27442, 13387],
            [27441, 13388],
            [27442, 13388]
        ])
        
        # 计算变换参数
        self._calculate_transform()
    
    def _calculate_transform(self):
        """计算经纬度到XY坐标的变换矩阵"""
        # 提取经纬度范围
        lon_min, lat_min = self.lon_lat_points.min(axis=0)
        lon_max, lat_max = self.lon_lat_points.max(axis=0)
        
        # 提取XY范围
        x_min, y_min = self.xy_points.min(axis=0)
        x_max, y_max = self.xy_points.max(axis=0)
        
        # 计算缩放比例
        self.lon_scale = (x_max - x_min) / (lon_max - lon_min)
        self.lat_scale = (y_max - y_min) / (lat_max - lat_min)
        
        # 计算偏移量
        self.x_offset = x_min - lon_min * self.lon_scale
        self.y_offset = y_min - lat_min * self.lat_scale
        
        # print("变换参数:")
        # print(f"经度缩放比例: {self.lon_scale}")
        # print(f"纬度缩放比例: {self.lat_scale}")
        # print(f"X偏移量: {self.x_offset}")
        # print(f"Y偏移量: {self.y_offset}")
    
    def lon_lat_to_xy(self, lon, lat):
        """将经纬度转换为XY坐标"""
        x = lon * self.lon_scale + self.x_offset
        y = lat * self.lat_scale + self.y_offset
        return int(round(x)), int(round(y))
    
    def xy_to_lon_lat(self, x, y):
        """将XY坐标转换为经纬度"""
        lon = (x - self.x_offset) / self.lon_scale
        lat = (y - self.y_offset) / self.lat_scale
        return lon, lat
    
    def test_accuracy(self):
        """测试转换精度"""
        # print("\n精度测试:")
        for i, (lon_lat, xy) in enumerate(zip(self.lon_lat_points, self.xy_points)):
            calculated_xy = self.lon_lat_to_xy(lon_lat[0], lon_lat[1])
            calculated_lon_lat = self.xy_to_lon_lat(xy[0], xy[1])
            
            # print(f"点 {i+1}:")
            # print(f"  原始: lon_lat={lon_lat}, xy={xy}")
            # print(f"  转换: xy={calculated_xy}, lon_lat={calculated_lon_lat}")
            # print(f"  误差: xy_diff={np.array(calculated_xy) - xy}")

# 使用示例
if __name__ == "__main__":
    # 创建转换器
    transformer = CoordinateTransformer()
    
    # 测试已知点
    transformer.test_accuracy()
    
    # 使用新的经纬度获取XY坐标
    print("\n新坐标转换示例:")

    # 最小经度: 121.23556102585027
    # 最小纬度: 30.978088379141937
    # 最大经度: 121.71795193219447
    # 最大纬度: 31.41870901875865

    new_lon_lat2 = [121.23556102585027, 30.978088379141937]
    new_xy2 = transformer.lon_lat_to_xy(new_lon_lat2[0], new_lon_lat2[1])
    print(f"经纬度 {new_lon_lat2} -> XY坐标 {new_xy2}")
    
    # 反向转换验证
    # recovered_lon_lat = transformer.xy_to_lon_lat(new_xy2[0], new_xy2[1])
    # print(f"XY坐标 {new_xy2} -> 经纬度 {recovered_lon_lat}")

    new_lon_lat2 = [121.71795193219447, 31.41870901875865]
    new_xy2 = transformer.lon_lat_to_xy(new_lon_lat2[0], new_lon_lat2[1])
    print(f"经纬度 {new_lon_lat2} -> XY坐标 {new_xy2}")
    
    # 反向转换验证
    # recovered_lon_lat = transformer.xy_to_lon_lat(new_xy2[0], new_xy2[1])
    # print(f"XY坐标 {new_xy2} -> 经纬度 {recovered_lon_lat}")