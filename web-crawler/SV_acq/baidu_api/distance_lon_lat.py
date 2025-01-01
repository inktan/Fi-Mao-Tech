import numpy as np

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees), returns an array.
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = np.radians([lon1, lat1, lon2, lat2])
    
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    return c * r * 1000

# 113.8589482167923 ,22.803826593859252,113.85933773518845, 22.803833870788875,113.8597272535846 ,22.8038411477185,

print(haversine_np(113.8589482167923 ,22.803826593859252,113.85933773518845, 22.803833870788875))