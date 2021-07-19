import seaborn
import matplotlib.pyplot as plt
import pandas as pd

import utils


dictionary = utils.open_json('data.json')['result']
dictionary = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))  # 根据 value 对 dict 进行 sort
dictionary = dict(list(dictionary.items())[:400])
# dictionary = dict(list(dictionary.items())[:500])


df = pd.DataFrame(dictionary.items(), columns=['ApiName', 'Count'])
print(df)

height = 600
width = 30
fig, ax = plt.subplots(figsize=(height, width))
seaborn.barplot(x='ApiName', y='Count', data=df)
plt.show()
