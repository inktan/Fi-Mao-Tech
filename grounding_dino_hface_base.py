from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection, infer_device
import torch
import json
from PIL import Image, ImageDraw, ImageFont
import os
from tqdm import tqdm

# model_id = "IDEA-Research/grounding-dino-tiny"
# model_id = "IDEA-Research/grounding-dino-base"
model_id = "v:\Personal\W_王坦\models--IDEA-Research--grounding-dino-tiny"
# model_id = "v:\Personal\W_王坦\models--IDEA-Research--grounding-dino-base"
# device = 'cuda'
device = infer_device()

processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(device)

def grounding_dino(IMAGE_PATH):
    IMAGE_PATH = r"e:\work\sv_pangpang\sv_pano_20251106\sv_google_pano\svi01_temp_work\10_151.2221999_-33.87120784_190.2689056396484_2021_3.jpg"
    image = Image.open(IMAGE_PATH)

    inputs = processor(images=image, text=text_labels, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs)

    results = processor.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        threshold=0.4,
        text_threshold=0.3,
        target_sizes=[image.size[::-1]]
    )

    result = results[0]

    # 准备保存检测结果的图片
    result_image = image.copy()
    draw = ImageDraw.Draw(result_image)

    # 尝试加载字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # 处理检测结果并保存到列表
    detections = []

    for box, score, label_idx in zip(result["boxes"], result["scores"], result["labels"]):
        box = [round(x, 2) for x in box.tolist()]
        score_value = round(score.item(), 3)
        label_text = label_idx
        
        # print(f"Detected {label_text} with confidence {score_value} at location {box}")
        
        # 保存检测信息到列表
        detection_info = {
            "label": label_text,
            "confidence": score_value,
            "bbox": box,
            "label_index": label_idx.item() if torch.is_tensor(label_idx) else label_idx
        }
        detections.append(detection_info)
        
        # 在图片上绘制边界框
        x1, y1, x2, y2 = box
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        
        # 在边界框上方绘制标签和置信度
        label_text = f"{label_text}: {score_value}"
        draw.rectangle([x1, y1-25, x1 + len(label_text)*8, y1], fill="red")
        draw.text((x1, y1-25), label_text, fill="white", font=font)

    # 保存带检测结果的图片
    image_type = IMAGE_PATH.split('.')[-1]
    output_image_path = IMAGE_PATH.replace(source_folder_name, result_folder_name).replace( '.' + image_type , '_detection_results.' + image_type)
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

    result_image.save(output_image_path)
    # print(f"检测结果图片已保存: {output_image_path}")

    # 保存检测结果为JSON文件
    image_type = IMAGE_PATH.split('.')[-1]
    output_json_path = IMAGE_PATH.replace(source_folder_name, result_folder_name).replace( '.' + image_type , '_detection_results.json')
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    json_data = {
        "image_path": IMAGE_PATH,
        "model_used": model_id,
        "detection_threshold": 0.4,
        "text_threshold": 0.3,
        "detections": detections
    }

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    # print(f"检测结果JSON已保存: {output_json_path}")

    # 显示检测统计信息
    print(f"\n检测统计:")
    print(f"总共检测到 {len(detections)} 个对象")
    for label in set([d["label"] for d in detections]):
        count = len([d for d in detections if d["label"] == label])
        print(f"  {label}: {count} 个")

if __name__ == "__main__":
    img_paths = []
    img_names = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")
  
    folder_path = r'E:\work\sv_pangpang\sv_pano_20251106\sv_google_pano\svi01'  
   
    source_folder_name = r'svi01_temp_work'
    result_folder_name = r'svi01_grounding_dino_base_results'

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)

    img_paths=[r"e:\work\sv_pangpang\sv_pano_20251106\sv_google_pano\svi01_temp_work\10_151.2221999_-33.87120784_190.2689056396484_2021_3.jpg"]
    print(len(img_paths))

    text_labels = [["tree"]]
    for IMAGE_PATH in tqdm(img_paths):
        grounding_dino(IMAGE_PATH)
    


