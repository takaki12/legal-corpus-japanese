import pickle

with open("./output/civil_code_dict.pkl", 'rb') as fp:
    civil_code_dict = pickle.load(fp)

with open("./output/civil_code_dict_withKou.pkl", 'rb') as fp:
    civil_code_dict_withKou = pickle.load(fp)

# 第95条を調べる
query = "95"
print("query:", query)
print('\n'.join(civil_code_dict[query]))

# 第95条の2項を調べる
query = "95_2"
print("query:", query)
print('\n'.join(civil_code_dict_withKou[query]))
