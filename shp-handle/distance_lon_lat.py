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

print(haversine_np( 120.0374272	,30.38464026 , 120.0369858,30.3842962 )) 57米
print(haversine_np( 120.0369858	,30.3842962 , 120.0365012,30.38344437)) 105米
print(haversine_np( 120.0365012	,30.38344437 , 120.0359709,30.38288919 )) 79米
                              