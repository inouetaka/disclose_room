import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import seaborn as sns

data = pd.read_csv('../processing_ogikubo.csv', index_col=0)

sns.distplot(data['家賃'], kde=False, rug=False, bins=30)
plt.xlabel('家賃')
plt.ylabel('物件数')
plt.savefig("test.png")


plt.figure(figsize=(10, 6))
sns.heatmap(data[['家賃', '築年数', '全層', '階層', '管理費', '敷金', '礼金', '専有面積', '間取り',
                  '間取りDK', '間取りL', '間取りS', '間取りK', '間取りワンルーム','徒歩1', '徒歩2', '徒歩3']].corr(),
                  cmap=sns.color_palette('coolwarm', 10), annot=True, fmt='.2f', vmin=-1, vmax=1)
plt.savefig('heatmap.png')