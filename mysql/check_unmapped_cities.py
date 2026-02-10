import os
import json

# -------------------------- 基础配置（需与你的实际路径一致）--------------------------
ROOT_DIR = r"F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_svinfo_csv"  # 城市文件夹根路径
MAP_JSON_PATH = r"D:\Users\mslne\Documents\GitHub\Fi-Mao-Tech\mysql\PROVINCE_CITY_MAP.json"  # 省份城市映射JSON文件路径
# -------------------------------------------------------------------------------------

def check_unmapped_cities(root_dir: str = ROOT_DIR, json_path: str = MAP_JSON_PATH) -> list:
    """
    检测根路径下未配置省份映射的城市/区域文件夹
    :param root_dir: 存放各城市文件夹的根路径
    :param json_path: 省份-城市映射JSON文件的绝对路径
    :return: 未配置映射的名称列表（方便后续批量补充）
    """
    # 1. 校验JSON文件是否存在
    if not os.path.exists(json_path):
        print(f"❌ 错误：省份映射JSON文件不存在！路径：{json_path}")
        return []
    
    # 2. 读取JSON文件为字典
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            province_city_map = json.load(f)
        print(f"✅ 成功读取省份映射JSON：共配置 {len(province_city_map)} 个城市/区域")
    except json.JSONDecodeError:
        print(f"❌ 错误：JSON文件格式非法！请检查 {json_path} 的语法（如逗号、引号）")
        return []
    except Exception as e:
        print(f"❌ 读取JSON文件失败，错误信息：{e}")
        return []
    
    # 3. 校验城市文件夹根路径是否存在
    if not os.path.exists(root_dir):
        print(f"❌ 错误：城市文件夹根路径不存在！路径：{root_dir}")
        return []
    
    # 4. 获取根路径下所有城市/区域文件夹名（过滤文件，仅保留文件夹）
    city_folders = [
        folder for folder in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, folder))
    ]
    if not city_folders:
        print(f"⚠️  提示：根路径下未发现任何城市/区域文件夹！路径：{root_dir}")
        return []
    print(f"✅ 成功扫描根路径：共发现 {len(city_folders)} 个城市/区域文件夹")
    
    # 5. 筛选未配置映射的名称
    unmapped_list = [name for name in city_folders if name not in province_city_map]
    
    # 6. 美化输出结果
    print("-" * 80)
    if unmapped_list:
        print(f"🔴 发现 {len(unmapped_list)} 个未配置省份映射的名称，需补充到JSON：")
        # 按换行输出，同时生成可直接复制的JSON格式（键值对，值先留空，方便手动补省份）
        for idx, name in enumerate(unmapped_list, 1):
            print(f"  {idx}. {name}")
        print("\n📋 可直接复制的JSON补充模板（请手动修改省份值）：")
        print("  {")
        for name in unmapped_list:
            print(f'    "{name}": "",')
        print("  }")
    else:
        print(f"🟢 所有城市/区域文件夹均已配置省份映射，无需补充！")
    
    return unmapped_list

# 执行检测（直接运行该文件即可触发）
if __name__ == "__main__":
    check_unmapped_cities()
    
    
    