# -*- coding: utf-8 -*-
import shapefile
import sys
import os

#常用方法
def folder_exists(folderPath):
    if os.path.exists(folderPath) == False:
        os.mkdir(folderPath)
        print("The folder was created successfully ==>" + folderPath)
    else:
        print('The folder already exists ==>' + folderPath)

#删除一个文件夹下的所有所有文件
def del_files(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):#如果是文件夹那么递归调用一下
            del_files(c_path)
        else:                    #如果是一个文件那么直接删除
            os.remove(c_path)
    print ('All files in the folder have been emptied')

def get_shp_field_list(path):
    try:
        try:
            file = shapefile.Reader(path,encoding='utf-8')
        except UnicodeDecodeError:
            file = shapefile.Reader(path, encoding="gbk")

        shp_geometry = []
        shp_datas = []

        fields = file.fields
        shp_fields = []
        for field in fields:
            shp_fields.append(field[0])

        shape_records = file.shapeRecords()
        for shape_record in shape_records:
            shp_type = shape_record.shape.shapeType
            if shp_type == 1:
                points = shape_record.shape.points
                points_order = []
                points_order.append(len(points))
                for point in points:
                    points_order.append(point[0])
                    points_order.append(point[1])
                shp_geometry.append(['point',points_order])
                shp_datas.append(shape_record.record)

            elif shp_type == 3:
                points = shape_record.shape.points
                parts = shape_record.shape.parts
                polyline_record = []
                for idx in range(0,len(parts)-1):
                    polyline_record_part = points[parts[idx]:parts[idx+1]]
                    polyline_record.append(polyline_record_part)
                polyline_record_part = points[parts[-1]:]
                polyline_record.append(polyline_record_part)

                # 可为一个线圈，可为多个线圈
                shp_geometry.append(['polyline',polyline_record])
                shp_datas.append(shape_record.record)

            elif shp_type == 5:
                points = shape_record.shape.points
                parts = shape_record.shape.parts
                polygon_record = []
                for idx in range(0,len(parts)-1):
                    polygon_record_part = points[parts[idx]:parts[idx+1]]
                    polygon_record.append(polygon_record_part)
                polygon_record_part = points[parts[-1]:]
                polygon_record.append(polygon_record_part)
                shp_geometry.append(['polygon',polygon_record])
                shp_datas.append(shape_record.record)
                #print(shape_record.record)

        return shp_geometry, shp_datas, shp_fields
    
    except shapefile.ShapefileException as e:
        print(e)
        print(repr(e))
        return repr(e)
