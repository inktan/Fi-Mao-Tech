# lst=[]
# all_0 = all(x == 0 for x in lst)  
# print(all_0)
# if all_0:
#     print('qwe')
        
# lst = []  
# result = len(set(lst)) == 1 and list(set(lst))[0] == 0  
# print(result)  # 输出: True
import pandas as pd  

df = pd.read_csv(r'e:\work\sv_chenlong20240907\RoadPoints_50m_unique.csv')

filtered_df = df.loc[df['PointID'] == 9]  
print(filtered_df.iloc[0,0])
print(filtered_df.iloc[0,1])
print(filtered_df.iloc[0,2])
print(filtered_df.iloc[0,3])

