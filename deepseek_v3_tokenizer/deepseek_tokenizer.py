# pip3 install transformers
# python3 deepseek_tokenizer.py
import transformers
import os

# 获取当前代码文件的绝对路径
current_file_path = os.path.abspath(__file__)
print("当前代码文件路径:", current_file_path)

# 获取当前代码所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
print("当前代码所在目录:", current_dir)


chat_tokenizer_dir = "./"
chat_tokenizer_dir = current_dir

tokenizer = transformers.AutoTokenizer.from_pretrained( 
        chat_tokenizer_dir, trust_remote_code=True
        )

result = tokenizer.encode("Hello!")
print(result)
