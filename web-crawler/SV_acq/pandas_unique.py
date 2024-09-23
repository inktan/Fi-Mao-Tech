import json
import pandas as pd

df = pd.read_csv(r'c:\Users\wang.tan.GOA\Desktop\id007.csv')
print(df.shape)
print(df.head(5))

df_unique = df.drop_duplicates(subset=['id01', 'id02'])
print(df_unique.shape)
print(df_unique.head(5))

df_unique.to_csv(r'c:\Users\wang.tan.GOA\Desktop\id007_unique.csv', index=False)

