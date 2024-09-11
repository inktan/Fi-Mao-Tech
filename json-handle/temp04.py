# lst=[]
# all_0 = all(x == 0 for x in lst)  
# print(all_0)
# if all_0:
#     print('qwe')
        


lst = []  
result = len(set(lst)) == 1 and list(set(lst))[0] == 0  
print(result)  # 输出: True