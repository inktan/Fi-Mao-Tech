# from transformers import pipeline

# classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

# sentences = ["I am not having a great day"]
# sentences = ["我爱你"]
# sentences = ["i love u"]

# model_outputs = classifier(sentences)
# print(model_outputs[0])
# for i in model_outputs[0]:
#     print(i)
# produces a list of dicts for each of the labels

# sentences = ["我讨厌你"]
# sentences = ["i hate you"]

# model_outputs = classifier(sentences)
# print(model_outputs[0])
# for i in model_outputs[0]:
#     print(i)
# produces a list of dicts for each of the labels

# https://huggingface.co/SchuylerH/bert-multilingual-go-emtions

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("SchuylerH/bert-multilingual-go-emtions")
model = AutoModelForSequenceClassification.from_pretrained("SchuylerH/bert-multilingual-go-emtions")

nlp = pipeline("sentiment-analysis", model = model, tokenizer = tokenizer)

text = "我后悔了"
print(text)
result = nlp(text)
print(result)

text = "我不同意你的方案"
print(text)
result = nlp(text)
print(result)






