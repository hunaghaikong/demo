import h5py
import numpy as np
from sklearn import svm
from sklearn.externals import joblib
import random

h5=h5py.File('dataszt.hdf5')
d3=h5['dataszt'][:]
h5.close()
# d1=d[np.where(d[:,-1]==1)]
# d2=d[np.where(d[:,-1]==0)]
# random.shuffle(d2)
# d3=list(d1)+d2[:120000]
# random.shuffle(d3)

# 支持向量机
svms=svm.SVC()
# svms=svm.SVC(kernel='rbf',C=1,gamma=3)
# svms=svm.SVC(kernel='linear',C=0.1)
d3=np.array(d3)
svms.fit(d3[:,:-1],d3[:,-1])
joblib.dump(svms,'svms.m')

# 决策树
from sklearn import tree
trees=tree.DecisionTreeClassifier()
trees.fit(d3[:,:-1],d3[:,-1])
joblib.dump(trees,'trees.m')

# 朴素贝叶斯
from sklearn.naive_bayes import MultinomialNB
bayes=MultinomialNB()
bayes.fit(d3[:,:-1],d3[:,-1])
joblib.dump(bayes,'bayes.m')

# K最近邻
from sklearn import neighbors
ngbs=neighbors.KNeighborsClassifier(n_neighbors=15,weights='uniform')
ngbs.fit(d3[:,:-1],d3[:,-1])
joblib.dump(ngbs,'ngbs.m')

# 线性回归
from sklearn.linear_model import LinearRegression
lrgs=LinearRegression()
lrgs.fit(d3[:,:-1],d3[:,-1])
joblib.dump(lrgs,'lrgs.m')

# 逻辑回归
from sklearn.linear_model import LogisticRegression
logisRgs=LogisticRegression()
logisRgs.fit(d3[:,:-1],d3[:,-1])
joblib.dump(logisRgs,'logisRgs.m')

# 随机森林
from sklearn.ensemble import RandomForestClassifier
rfcf=RandomForestClassifier(n_estimators=8)
rfcf.fit(d3[:,:-1],d3[:,-1])
joblib.dump(rfcf,'rfcf.m')

# MLP神经网络
from sklearn.neural_network import MLPClassifier
mlpcf=MLPClassifier()
mlpcf.fit(d3[:,:-1],d3[:,-1])
joblib.dump(mlpcf,'mlpcf.m')
