import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

input_file = r'e:\work\sv_pangpang\CoS_StreetTree_data_for_model.xls'
# df = pd.read_csv(input_file, encoding='GBK')
# df = pd.read_csv(input_file)
df = pd.read_excel(input_file)

print(df.columns)
print(df.head())
print(df.shape)



