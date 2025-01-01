import os  
from PIL import Image  
  
# 设置图片所在的目录  
image_folder = r'F:\build\sv_arch' 

out_folder_path = image_folder.replace('sv_arch','sv_arch_merge')
if not os.path.exists(out_folder_path):
    os.makedirs(out_folder_path) 

for i in range(10000):
    try:
        img01 = os.path.join(image_folder, str(i)+'(90).jpg')
        img02 = os.path.join(image_folder, str(i)+'(180).jpg')
        img03 = os.path.join(image_folder, str(i)+'(270).jpg')
        img04 = os.path.join(image_folder, str(i)+'(-90).jpg')

        # 创建一个空列表来存储Image对象  
        image_group = [ img01,img02,  img03,img04 ]
        images = []  
        
        # 打开每个图片文件，并将其添加到列表中  
        for image_path in image_group:  
            img = Image.open(image_path)  
            images.append(img)  

        # 获取第一个图片的尺寸，以确定合并后图片的宽度  
        width, height = images[0].size  
        
        # 创建一个新的空白图片，宽度是所有图片宽度之和，高度与单个图片相同  
        total_width = width * len(images)  
        merged_image = Image.new('RGB', (total_width, height))  
       
        # 横向合并图片  
        x_offset = 0  
        for img in images:  
            merged_image.paste(img, (x_offset, 0))  
            x_offset += width 
        
        merged_image.save(os.path.join(out_folder_path, str(i)+'.jpg'))  
        print(i)

    except Exception as e :
        print(e)

print('All images merged and saved.')