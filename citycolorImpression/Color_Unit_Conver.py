# %%
import colorsys
import numpy as np

# %%
# 十六进制值为 6 位数字 （rrggbb）
# RGB 值在 0-255 的范围内
# HSV 值在 Hue：0 范围内。359°， 饱和度：100%，值：100%
# HSL 值在色相：0 范围内。359°， 饱和度：100%， 亮度：100%

# %%
def hsv_to_rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

def hls_to_rgb(h, s, l):
    return tuple(round(i * 255) for i in colorsys.hls_to_rgb(h, s, l))

def rgb_to_hsv(r, g, b):
    '''百分比-百分比-百分比'''
    # 将RGB值转换为0到1的范围
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # 使用colorsys模块转换到HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    # 返回HSV值
    return h, s, v

def rgb_to_hsv_(r, g, b):
    '''度-百分比-百分比'''
    # 将RGB值转换为0到1的范围
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # 使用colorsys模块转换到HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    # 返回HSV值
    return h*360, s, v
def rgb_to_hls(r, g, b):
    '''百分比-百分比-百分比'''
    # 将RGB值转换为0到1的范围
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # 使用colorsys模块转换到HSL
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    # 返回HSL值
    return h, l, s 

def rgb_to_hls_(r, g, b):
    '''度-百分比-百分比'''
    # 将RGB值转换为0到1的范围
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # 使用colorsys模块转换到HSL
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    # 返回HSL值
    return h*360, s, l

# %%
def rgb_to_xyz(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    if r > 0.04045:
        r = ((r + 0.055) / 1.055) ** 2.4
    else:
        r = r / 12.92
    if g > 0.04045:
        g = ((g + 0.055) / 1.055) ** 2.4
    else:
        g = g / 12.92
    if b > 0.04045:
        b = ((b + 0.055) / 1.055) ** 2.4
    else:
        b = b / 12.92

    r *= 100
    g *= 100
    b *= 100

    x = 0.412453 * r + 0.357580 * g + 0.180423 * b
    y = 0.212671 * r + 0.715160 * g + 0.072169 * b
    z = 0.019334 * r + 0.119193 * g + 0.950227 * b

    return x, y, z

def xyz_to_lab(x, y, z):
    ref_x, ref_y, ref_z = 95.047, 100.0, 108.883
    x /= ref_x
    y /= ref_y
    z /= ref_z

    if x > 0.008856:
        x = x ** (1/3)
    else:
        x = (7.787 * x) + (16 / 116)
    if y > 0.008856:
        y = y ** (1/3)
    else:
        y = (7.787 * y) + (16 / 116)
    if z > 0.008856:
        z = z ** (1/3)
    else:
        z = (7.787 * z) + (16 / 116)

    l = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)

    return l, a, b

def rgb_to_lab(r, g, b):
    x, y, z = rgb_to_xyz(r, g, b)
    l, a, b = xyz_to_lab(x, y, z)
    return l, a, b

# %%
def lab_to_xyz(l, a, b):
    y = (l + 16) / 116
    x = a / 500 + y
    z = y - b / 200

    if y**3 > 0.008856:
        y = y**3
    else:
        y = (y - 16 / 116) / 7.787
    if x**3 > 0.008856:
        x = x**3
    else:
        x = (x - 16 / 116) / 7.787
    if z**3 > 0.008856:
        z = z**3
    else:
        z = (z - 16 / 116) / 7.787

    ref_x, ref_y, ref_z = 95.047, 100.0, 108.883
    x = x * ref_x
    y = y * ref_y
    z = z * ref_z

    return x, y, z

def xyz_to_rgb(x, y, z):
    x /= 100
    y /= 100
    z /= 100

    r = 3.2406 * x - 1.5372 * y - 0.4986 * z
    g = -0.9689 * x + 1.8758 * y + 0.0415 * z
    b = 0.0557 * x - 0.204 * y + 1.057 * z

    if r > 0.0031308:
        r = 1.055 * (r ** (1 / 2.4)) - 0.055
    else:
        r *= 12.92
    if g > 0.0031308:
        g = 1.055 * (g ** (1 / 2.4)) - 0.055
    else:
        g *= 12.92
    if b > 0.0031308:
        b = 1.055 * (b ** (1 / 2.4)) - 0.055
    else:
        b *= 12.92

    r, g, b = np.clip([r, g, b], 0, 1) * 255
    return int(r), int(g), int(b)

def lab_to_rgb(l, a, b):
    x, y, z = lab_to_xyz(l, a, b)
    return xyz_to_rgb(x, y, z)

# %%
def hsv_to_lab(h,s,v):
    r,g,b = hsv_to_rgb(h,s,v)
    return rgb_to_lab(r,g,b)

# %%
import pandas as pd
csv_path = r'f:\color_daidonggua\color_cal_.csv'
df = pd.read_csv(csv_path)

# %%
df.head(2)

# %%
column_order = ['File_Name', 'Percentage_1', 'Color_tone_1', 'Percentage_2', 'Color_tone_2', 'Percentage_3', 'Color_tone_3']
# 重排DataFrame的列
df_01 = df[column_order]
# 打印重排后的DataFrame
df_01.head(2)


# %%
df_01['Color_1_H'] = df_01['Color_tone_1'].str.split('(', expand=True)[1].str.split(',', expand=True)[0]
df_01['Color_1_S'] = df_01['Color_tone_1'].str.split('(', expand=True)[1].str.split(',', expand=True)[1]
df_01['Color_1_V'] = df_01['Color_tone_1'].str.split('(', expand=True)[1].str.split(',', expand=True)[2].str.split(')', expand=True)[0]

df_01['Color_2_H'] = df_01['Color_tone_2'].str.split('(', expand=True)[1].str.split(',', expand=True)[0]
df_01['Color_2_S'] = df_01['Color_tone_2'].str.split('(', expand=True)[1].str.split(',', expand=True)[1]
df_01['Color_2_V'] = df_01['Color_tone_2'].str.split('(', expand=True)[1].str.split(',', expand=True)[2].str.split(')', expand=True)[0]

df_01['Color_3_H'] = df_01['Color_tone_3'].str.split('(', expand=True)[1].str.split(',', expand=True)[0]
df_01['Color_3_S'] = df_01['Color_tone_3'].str.split('(', expand=True)[1].str.split(',', expand=True)[1]
df_01['Color_3_V'] = df_01['Color_tone_3'].str.split('(', expand=True)[1].str.split(',', expand=True)[2].str.split(')', expand=True)[0]
# 打印DataFrame以查看结果
df_01.head(2)

# %%
# 应用函数并拆分结果为三列
df_01[['Color_1_L', 'Color_1_A', 'Color_1_B']] = df_01.apply(
    lambda row: pd.Series(hsv_to_lab(float(row['Color_1_H'])/360, float(row['Color_1_S']), float(row['Color_1_V']))), axis=1
)

df_01[['Color_2_L', 'Color_2_A', 'Color_2_B']] = df_01.apply(
    lambda row: pd.Series(hsv_to_lab(float(row['Color_2_H'])/360, float(row['Color_2_S']), float(row['Color_2_V']))), axis=1
)

df_01[['Color_3_L', 'Color_3_A', 'Color_3_B']] = df_01.apply(
    lambda row: pd.Series(hsv_to_lab(float(row['Color_3_H'])/360, float(row['Color_3_S']), float(row['Color_3_V']))), axis=1
)

df_01.head()


# %%
columns_to_save = ['File_Name','Percentage_1','Color_1_H','Color_1_S','Color_1_V','Color_1_L','Color_1_A','Color_1_B',
'Percentage_2','Color_2_H','Color_2_S','Color_2_V','Color_2_L','Color_2_A','Color_2_B',
'Percentage_3','Color_3_H','Color_3_S','Color_3_V','Color_3_L','Color_3_A','Color_3_B']

df_02 = df_01[columns_to_save]

# 指定保存的文件名
output_file = r'F:\color_daidonggua/extracted_colors.csv'

# 将选择的列保存到CSV文件中
df_02.to_csv(output_file, index=False)

df_02.head()
df_02.shape



