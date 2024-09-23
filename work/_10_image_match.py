# -*- coding: utf-8 -*-

import shutil
from PIL import Image
from image_searcher import Search

# 图片库所在文件夹位置
images_dir_path=r"E:\ai_项目\embedding-test\img04"
searcher = Search(images_dir_path, traverse=True, include_faces=False)# traverse 迭代子文件夹

# 匹配图片方法01：使用关键词

# 被索引描述文字
# prompt = "railing"
# ranked_images = searcher.rank_images(prompt, n= 3)
# for image in ranked_images:
#     print(image.image_path)
#     Image.open(image.image_path).convert('RGB').show()
#     shutil.copy(image.image_path, match_save_dir)


# 匹配图片方法02：使用图片

# 匹配图像储存文件夹位置
match_save_dir = r'E:\ai_项目\embedding-test\img_results08'
# 被索引图像
image_path = r'e:\ai_项目\embedding-test\test00.jpg'

# ranked_images = searcher.test()
ranked_images = searcher.rank_images_by_image(image_path, n= 25)
for index, image in enumerate(ranked_images):
    print(image.score,image.image_path)
    # Image.open(image.image_path).convert('RGB').show()
    shutil.copy(image.image_path, match_save_dir+'/'+str(index)+'_'+str(image.score)+'.jpg')

    


