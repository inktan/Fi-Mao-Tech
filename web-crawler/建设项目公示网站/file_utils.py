import os
import re

PageCount =1
# keywords.py
PROJECT_KEYWORDS =  ['公示已到期',
                    '加装电梯',
                    '增设电梯',
                    '轨道交通',
                    '采购意向',
                    '集中反馈',
                    '道路工程',
                    '公园绿地',
                    '道路新建',
                    '基础设施',
                    '河道工程',
                    '立面改造',
                    '选址公示',
                    '停车场',
                    '车间',
                    '制造',
                    '年产',
                    '扩建',
                    '经营',
                    '建议',
                    '报告',
                    '反馈',
                    '年度',
                    '通知',
                    '商请',
                    '说明',
                    '批复',
                    '请示',
                    '目录',
                    '清单',
                    '计划',
                    '民生实事']

def get_deepest_dirs(root_dir):
    """获取所有嵌套最底层的文件夹路径（没有子文件夹的文件夹）"""
    deepest_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if not dirnames:  # 如果没有子文件夹，说明是底层文件夹
            dir_name = os.path.basename(dirpath)  # 获取文件夹名（不含路径）
            deepest_dirs.add(dir_name)

    return deepest_dirs

def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{project_name}_{publish_date[:10]}"  # 只取日期部分
    return dirname[:180]  # 限制长度防止路径过长