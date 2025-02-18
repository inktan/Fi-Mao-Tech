# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="sk-8f022fdb45524520aff4667d2c7b6c17", base_url="https://api.deepseek.com")


question = r'请使用简短的建筑设计专业语言，总结下面的文字内容。\n'
question += r'''
ArchDaily 
项目 
工厂 
中国 
梁溪医疗器械产业园 / UDG有关工作室
•
无锡, 中国
建筑师: UDG有关工作室
面积: 
62500 m²
项目年份: 
2024
摄影师:Mlee
主创设计: 陈伟鹏
总包团队: 李笑强、肖泰、赵志龙、张小庆、李晓锋、邓龙君、朱时忠、李志良
项目管理: 联创设计 城市更新设计研究院
管理团队: 宣磊、汤彬彬、郭李婵
EPC 总包及施工图设计: 中建二局第二建筑工程有限公司
设计咨询: 中国建筑上海设计研究院有限公司
咨询团队: 李东辉、周靖、吕罡、江娟、宋罕宇、吴学义、彭磊、龚旭东、游杰、曹佳伟、张庆男、赖菲、王晓椰、钟璐
幕墙深化设计施工: 江苏恒尚节能科技股份有限公司 朱占中
委托方: 无锡市梁溪产业发展集团有限公司
City: 无锡

1、项目背景

梁溪医疗产业园位于京杭大运河畔，定位为集制造、加工、研发、展示于一体的综合性医疗器械产业园区，建成后将推动相关产业集群发展成型，助力无锡市锻造“工业都芯”及高质量发展。作为产业片区首个工业上楼项目，设计师希望新的建筑在满足基本功能的同时，也能呈现出时代风貌，促进片区提质升级。
2、模式创新

秉承“高效开发，模式创新”的理念，项目对交通动线组织方式进行了创新。在狭长的基地中规划了两座厂房，分别用于生产制造和配套研发，两者通过外墙联系在一起，呈现出富有机械感的整体形态。厂房两侧设计有单上单下的旋转坡道，可供中型货车直接运货至各层，与传统的仅通过货梯进行垂直运输的方式相比，提升了每层的可达性，规避高楼层带来的价值缺失。小客车也利用该坡道在屋面停车，减少地下室开挖，加快施工进度。
3、工业之美

建筑希望体现工业特有的美感，呈现出干净通透的现代气质。设计采用几何对比及材料对比，追求结构、构造的真实表达。坡道随时间光线变化，形成丰富光影。运河之窗采用T型精制钢立柱，横向不设梁，凸显通透敞亮的效果。园区不设置围墙，面向城市设置休闲大台阶，为片区提供良好的公共空间。屋面停车场和活动平台，可远眺运河景观，为使用人员创造一个轻松愉悦的露天场所。夜景结合吊顶设置“第六立面”，彰显了科技感和未来感。各层的吊装平台结合立面景框设置。货运通道以不同颜色粉刷，有效提升了可识别性。

于2025年二月, 07
引用: "梁溪医疗器械产业园 / UDG有关工作室" [Liangxi Medical Equipment Industrial Park / UDG About Studio] 07 2月 2025. ArchDaily. Accesed 10 2月 2025. <https://www.archdaily.cn/cn/1026143/liang-xi-yi-liao-qi-jie-chan-ye-yuan-udgyou-guan-gong-zuo-shi>
'''

# print(question)
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        # {"role": "user", "content": "Hello"},
        {"role": "user", "content": question},
    ],
    stream=False
    # stream=True
)

print(response.choices[0].message.content)

# for chunk in response:
#     print(chunk.choices[0].delta.content)

