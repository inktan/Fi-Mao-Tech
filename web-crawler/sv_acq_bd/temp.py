import os
import pandas as pd
from coordinate_converter import transCoordinateSystem, transBmap
import math


# 使用示例
if __name__ == "__main__":
    

    pointx,pointy = transBmap.lnglattopoint(120.0995150000,30.2664680000)
    pixelx = int(pointx * 2 ** (17 - 18) )
    pixely = int(pointy * 2 ** (17 - 18) )

    print(pixelx)
    print(pixely)

    # print(transBmap.lnglattotile(120.0995150000, 30.2664680000,17))
    # print(transBmap.lnglattopixel(120.0995150000, 30.2664680000,17))
