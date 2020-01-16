import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor as RFR
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
import seaborn as sns

df_origin = pd.read_csv('../processing_nerima.csv', index_col=0)

df = df_origin.copy()
Y = df['家賃'].copy()
name = df['マンション名']
X = df.drop(['家賃', 'マンション名', '住所', '詳細ページ'], axis=1).copy()

X_train, X_test, y_train, y_test = train_test_split(X, Y, random_state=0, test_size=0.2)

# ランダムフォレストの作成
forest = RFR(n_jobs=1, random_state=2525)
forest.fit(X_train, y_train)
predY = forest.predict(X_train)

# 評価
print('Train score: {}'.format(forest.score(X_train, y_train)))
print('Test score: {}'.format(forest.score(X_test, y_test)))

pred = pd.DataFrame(predY, columns=["適正価格(予想)"])
y_train_ = pd.concat([y_train, df_origin['マンション名'], df['詳細ページ']], axis=1, join="inner").reset_index(drop=True)
pred_ = pd.concat([round(pred, 1), y_train_], axis=1)
diff = pd.DataFrame(pred_['家賃'] - pred_['適正価格(予想)'], columns=['差分'])
pred_ = pd.concat([round(diff, 1), pred_], axis=1)
pred_.to_csv('./pred_nerima.csv')

