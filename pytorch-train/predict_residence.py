import torch
from tqdm import tqdm

torch.cuda.empty_cache()
import os
import cv2
import pandas as pd
import glob

class Predict:
    def __init__(self, img_folder, img_type='jpg'):

        img_path_lst = glob.glob(img_folder+'*.{}'.format(img_type))
        self.image_name = [os.path.basename(i) for i in img_path_lst]
        images_size = len(img_path_lst)  # 图片的数量

        self.images = torch.zeros(images_size, 3, 250, 250, dtype=torch.uint8)  # 640-->250 创建一个都是0的tensor，后面进行值更新。
        for i, filename in tqdm(enumerate(img_path_lst)):
            # print("loading image",'==>',i)
            # print(file_path)
            img_arr = cv2.imread(filename)
            img_arr = cv2.resize(img_arr, [250, 250])
            img_t = torch.from_numpy(img_arr)  # 将图片转为tensor
            img_t = img_t.permute(2, 0, 1)  # 在原始的图片中是高、宽、通道，这里改为通道、高、宽
            img_t = img_t[:3]  # 这里为了保证只要前3个通道，因为有些可能有alpha通道
            self.images[i] = img_t  # 通过索引操作，将图片值更新至之前的0填充tensor

        self.images = self.images / 255  # 值压缩到[0,1]
        print(f'数据准备完毕!开始执行计算...')

    def predict(self, model_path, out_csv, batch=5):
        model = torch.load(model_path)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        all_images = self.images.to(device)
        model.to(device)
        model.eval()

        n_loop = int(all_images.shape[0] / batch) + 1

        df_list = []
        for n in range(n_loop):
            print(n*batch,(n+1)*batch)
            images = all_images[n*batch:(n+1)*batch]
            out_name = self.image_name[n*batch:(n+1)*batch]

            out = model(images)
            print(images.shape)

            probs, out_label = out.max(axis=1)
            probs = probs.detach().cpu().numpy()
            out_label = out_label.detach().cpu().numpy()

            print(probs)
            label = {
                0: 0,
                1: 1,
            }
            new_label = {v:k for k, v in label.items()}
            out_label = [new_label[i] for i in out_label]

            img_df = pd.DataFrame({'out_name':out_name,'out_label': out_label,})
            df_list.append(img_df)
        result = pd.concat(df_list)
        result.to_csv(out_csv,index=False)

        print(f'预测结束，已结果文件生成文件，地址位{out_csv}')


if __name__ == "__main__":

    model_path = r"D:\BaiduSyncdisk\S01_gsv\sv_result\weight_residence\epoch9.pth"

    for i in range(50):
        if i>0:
            for j in range(50):
                if j>30:
                    image_folder = r"D:\a19-foreignAid\sv_data\zhejiang_buildings\points\point_"+str(i)+"\sv_result_split\\"+str(j)+"\\"
                    if os.path.exists(image_folder) == True:
                        out_csv= r"D:\a19-foreignAid\sv_data\zhejiang_buildings\points\point_"+str(i)+"\sv_result_split\predict_residence_"+str(i)+"_"+str(j)+".csv"
                        predictor = Predict(image_folder,img_type='jpg')
                        predictor.predict(model_path,out_csv)
