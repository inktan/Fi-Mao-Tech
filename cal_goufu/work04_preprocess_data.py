import geopandas as gpd
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# 读取SHP文件
input_path = r'e:\work\sv_goufu\MLP\year21\MLP21_valid_data.shp'
gdf = gpd.read_file(input_path)

# 定义特征列和目标列
feature_cols = ['NEAR_DIST', 'dem', 'density', 'landcover', 'ylight', 'ndvi', 
               'podu', 'population', 'poxiang', 'rain', 'road2', 'temper', 
               'densitywa', 'lengthwa']
target_col = 'Join_Count'

# 1. 对landcover列进行独热编码
print("正在对landcover列进行独热编码...")
landcover_dummies = pd.get_dummies(gdf['landcover'], prefix='landcover')
gdf = pd.concat([gdf.drop(columns=['landcover']), landcover_dummies], axis=1)

# 更新特征列列表（移除landcover，添加新生成的独热编码列）
new_feature_cols = [col for col in feature_cols if col != 'landcover'] + list(landcover_dummies.columns)

# 2. 对其余数值列进行标准化（Z-score Scaling）
print("正在对其他数值列进行标准化...")
scaler = StandardScaler()
numeric_cols = [col for col in new_feature_cols if col.startswith('landcover') == False]
gdf[numeric_cols] = scaler.fit_transform(gdf[numeric_cols])

# 3. 保存预处理后的数据
output_path = input_path.replace('.shp', '_preprocessed.shp')
gdf.to_file(output_path)
print(f"预处理完成！结果已保存到: {output_path}")

# 4. 准备MLP训练数据（可选）
X = gdf[new_feature_cols]
y = gdf[target_col]

# 划分训练集和测试集（可选）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("\n数据已准备好用于MLP训练:")
print(f"- 特征数: {len(new_feature_cols)}")
print(f"- 训练样本数: {len(X_train)}")
print(f"- 测试样本数: {len(X_test)}")