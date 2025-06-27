import os

# 设置目标目录
target_dir = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines"

# 遍历目录下的所有文件
for filename in os.listdir(target_dir):

    os.rename(target_dir + '\\' + filename, target_dir + '\\' + filename.replace('_筛选', ''))


print("所有.shp文件及其关联文件已重命名完成！")