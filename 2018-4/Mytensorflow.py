import tensorflow as tf
from numpy.random import RandomState
import numpy as np

def neural_net():
    w1 = tf.Variable(tf.truncated_normal([2,3],seed=1))
    w2 = tf.Variable(tf.truncated_normal([3,1],seed=1))

    x = tf.placeholder(dtype=tf.float32,shape=[None,2])

    y_real = tf.placeholder(dtype=tf.float32,shape=[None,1])

    a = tf.nn.relu(tf.matmul(x,w1)) # 神经元的激活函数为 relu 隐层
    y_pre = tf.nn.relu(tf.matmul(a,w2)) # 输出层

    sample_size = 20000  # 训练样本数量
    rds = RandomState(0) # 随机种子
    X = rds.rand(sample_size,2)
    Y = [[int(20*x1+30*x2)]+rds.rand(1) for (x1,x2) in X]

    MSE = tf.reduce_mean(abs(y_real-y_pre))
    train_step = tf.train.GradientDescentOptimizer(6-3).minimize(MSE) # 6？

    step = 20000 # 训练迭代次数
    batch = 500 # 批大小为500
    start = 0 # 每个batch 的开始和结束指针
    end = batch

    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    for i in range(step):
        sess.run(train_step,feed_dict={x:X[start:end],y_real:Y[start:end]})
        if not i%20:
            H = sess.run(MSE,feed_dict={x:X[start:end],y_real:Y[start:end]})
            print("MSE:",H)
            if H<0.4: # 采用stop early 的方法防止过拟合，节省训练时间。
                break
        start = end if end<sample_size else 0
        end = start+batch
    y1 = sess.run(y_pre,feed_dict={x:X[start:end]})
    y2 = Y[start:end]
    sess.close()

    # 训练结果部分展示
    for i in range(100):
        print(y1[i],y2[i])

def neural_net2():

    # 建立训练用的数据
    def addlayer(inputdata,input_size,out_size,active=None):
        weights=tf.Variable(tf.random_normal([input_size,out_size]))
        bias=tf.Variable(tf.zeros([1,out_size])+0.1)
        wx_plus_b=tf.matmul(inputdata,weights)+bias
        if active==None:
            return wx_plus_b
        else:
            return active(wx_plus_b)

    # 建立训练用的数据
    xdata=np.linspace(-1,1,300)[:,np.newaxis]
    noise=np.random.normal(0,0.05,xdata.shape)
    ydata=np.square(xdata)-0.5+noise

    xinput=tf.placeholder(tf.float32,[None,1])
    youtput=tf.placeholder(tf.float32,[None,1])

    # 构建一个含有单隐层的神经网络
    layer1=addlayer(xinput,1,10,tf.nn.relu)
    output=addlayer(layer1,10,1,active=None)

    # 定义损失函数和训练含义
    loss=tf.reduce_mean(tf.reduce_sum(tf.square(youtput-output),reduction_indices=[1]))
    train=tf.train.GradientDescentOptimizer(0.05).minimize(loss)

    # 定义变量初始化操作
    init=tf.initialize_all_variables()

    with tf.Session() as sess:
        sess.run(init) # 进行初始变量
        for i in range(2000):
            sess.run(train,feed_dict={xinput:xdata,youtput:ydata})
            if i%100==0:
                print (i,sess.run(loss,feed_dict={xinput:xdata,youtput:ydata}))

def neural_net3():

    def addLayer(inputData,inSize,outSize,activity_function = None):
        Weights = tf.Variable(tf.random_normal([inSize,outSize]))
        basis = tf.Variable(tf.zeros([1,outSize])+0.1)
        weights_plus_b = tf.matmul(inputData,Weights)+basis
        if activity_function is None:
            ans = weights_plus_b
        else:
            ans = activity_function(weights_plus_b)
        return ans

    x_data = np.linspace(-1,1,300)[:,np.newaxis] # 转为列向量
    noise = np.random.normal(0,0.05,x_data.shape)
    y_data = np.square(x_data)+0.5+noise


    xs = tf.placeholder(tf.float32,[None,1]) # 样本数未知，特征数为1，占位符最后要以字典形式在运行中填入
    ys = tf.placeholder(tf.float32,[None,1])

    l1 = addLayer(xs,1,10,activity_function=tf.nn.relu) # relu是激励函数的一种
    l2 = addLayer(l1,10,1,activity_function=None)
    loss = tf.reduce_mean(tf.reduce_sum(tf.square((ys-l2)),reduction_indices = [1]))#需要向相加索引号，redeuc执行跨纬度操作

    train =  tf.train.GradientDescentOptimizer(0.1).minimize(loss) # 选择梯度下降法

    init = tf.initialize_all_variables()
    sess = tf.Session()
    sess.run(init)

    for i in range(10000):
        sess.run(train,feed_dict={xs:x_data,ys:y_data})
        if i%50 == 0:
            print (sess.run(loss,feed_dict={xs:x_data,ys:y_data}))

def neural_net_iris():
    from sklearn import datasets

    iris=datasets.load_iris()

    datax=iris.data[:120]
    datay=iris.target[:120]

    testx=iris.data[120:]
    testy=iris.target[120:]

    feature_columns = [tf.contrib.layers.real_valued_column("", dimension=4)]

    classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                              hidden_units=[10, 20, 10],
                                              n_classes=3,
                                              model_dir="/tmp/iris_model")

    classifier.fit(x=datax, y=datay, steps=2000)
    #classifier.fit(x=np.array([[6.4, 3.2, 4.5, 1.5]]),y=np.array([[1]]), steps=2000)

    accuracy_score = classifier.evaluate(x=testx, y=testy)["accuracy"] #评估


    # 分类新样本
    new_samples = np.array(
        [[6.4, 3.2, 4.5, 1.5], [5.8, 3.1, 5.0, 1.7]], dtype=float)
    prediction= list(classifier.predict(new_samples, as_iterable=True))
    print(accuracy_score)
    print('Predictions: {}'.format(str(prediction)))

def xunlian(datas):

    datax=datas[:61700,:-1]
    datay=datas[:61700,-1].astype(np.int32)

    testx=datas[61700:,:-1]
    testy=datas[61700:,-1].astype(np.int32)

    feature_columns = [tf.contrib.layers.real_valued_column("", dimension=18)]

    classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                              hidden_units=[10, 20, 10],
                                              n_classes=2)
                                              #model_dir="/tmp/iris_model")

    classifier.fit(x=datax, y=datay, steps=2000)
    #classifier.fit(x=np.array([[6.4, 3.2, 4.5, 1.5]]),y=np.array([[1]]), steps=2000)

    accuracy_score = classifier.evaluate(x=testx, y=testy)["accuracy"] #评估

    #prediction= list(classifier.predict(new_samples, as_iterable=True))
    print(accuracy_score)
    
    return classifier
    

def main(argv=None,ind=0):
    run_i=ind if ind else 4
    funcs=[neural_net,neural_net2,neural_net3,neural_net_iris]
    funcs[run_i-1]()


if __name__ == '__main__':

    tf.app.run()
