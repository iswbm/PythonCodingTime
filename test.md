前段时间，有朋友在我的读者群里问了几个关于单例模式的问题。

为了回答他的问题，我整理了单例模式的知识点，正好我也在写设计模式的系列。

上一篇是讲「[策略模式](http://mp.weixin.qq.com/s?__biz=MzU4OTUwMDE1Mw==&mid=2247484565&idx=1&sn=5e39c83a1b5db7065a99b22fddb617d5&chksm=fdcddf03caba5615bdf26038d428ec1fbb2b600070186e33f975d0235c57c7a167a15a5efcc7&scene=21#wechat_redirect)」，若你还未阅读，可以点击这里查看：

[商场促销活动背后的代码哲学](https://mp.weixin.qq.com/s?__biz=MzU4OTUwMDE1Mw==&mid=2247484565&idx=1&sn=5e39c83a1b5db7065a99b22fddb617d5&scene=21#wechat_redirect)

本篇做为「设计模式系列」的第二篇，来一起看看「单例模式」。

之前在另一篇公众号文章看到一个挺搞笑的例子：

大意是讲，老婆在中国其实就是一个很形象的单例，你要娶一个老婆需要去民政局注册登记（要对类进行实例化），当你想再娶一个老婆时，这时民政局会说，不行，你已经有一个老婆了，并且它还会告诉你的老婆是谁。

玩笑之后，再回到我们的话题，先举几类我们经常见到的例子：

***1、***大家在解释单例模式时，经常要提到的一个例子是 Windows 的任务管理器。如果我们打开多个任务管理器窗口。显示的内容完全一致，如果在内部是两个一模一样的对象，那就是重复对象，就造成了内存的浪费；相反，如果两个窗口的内容不一致，那就会至少有一个窗口展示的内容是错误的，会给用户造成误解，到底哪个才是当前真实的状态呢？

***2、***一个项目中多个地方需要读取同一份配置文件，如果每次使用都是导入重新创建实例，读取文件，用完后再销毁，这样做的话，就造成不必要的IO浪费，可以使用单例模式只生成一份配置在内存中。

***3、***还有一个常见的例子是，一个网站的访问量、在线人数，在项目中是全局唯一（不考虑分布式），在这种情况下，使用单例模式是一种很好的方式。

从上面看来，在系统中确保某个对象的唯一性即一个类只能有一个实例有时是非常重要的。

按照惯例，我们先来用代码实践一下，看看如何用 Python 写单例模式。



这里介绍了三个较为常用的。

- 使用 \_\_new__

```python
class User:
	_instance = None
	def __new__(cls, *args, **kwargs):
		print('===== 1 ====')
		if not cls._instance:
			print("===== 2 ====")
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self, name):
		print('===== 3 ====')
		self.name = name
```

验证结果

![](http://image.python-online.cn/20190512113846.png)

- 使用装饰器

```python
instances = {}

def singleton(cls):
	def get_instance(*args, **kw):
		cls_name = cls.__name__
		print('===== 1 ====')
		if not cls_name in instances:
			print('===== 2 ====')
			instance = cls(*args, **kw)
			instances[cls_name] = instance
		return instances[cls_name]
	return get_instance

@singleton
class User:
	_instance = None

	def __init__(self, name):
		print('===== 3 ====')
		self.name = name
```

验证结果

![](http://image.python-online.cn/20190512113917.png)

- 使用元类

```python
class MetaSingleton(type):
	def __call__(cls, *args, **kwargs):
		print("cls:{}".format(cls.__name__))
		print("====1====")
		if not hasattr(cls, "_instance"):
			print("====2====")
			cls._instance = type.__call__(cls, *args, **kwargs)
		return cls._instance

class User(metaclass=MetaSingleton):
	def __init__(self, *args, **kw):
		print("====3====")
		for k,v in kw:
			setattr(self, k, v)
```

验证结果

![](http://image.python-online.cn/20190512114028.png)

以上的代码，一般情况下没有问题，但在并发场景中，就会出现线程安全的问题。

如下这段代码我开启10个线程来模拟

```python
import time
import threading

class User:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            time.sleep(1)
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name):
        self.name = name

def task():
    u = User("wangbm")
    print(u)

for i in range(10):
    t = threading.Thread(target=task)
    t.start()
```

从结果来观察，很容易就发现，单例模式失效了，在10个线程下，并发创建实例，并不能保证一个类只有一个实例。

```python
<__main__.User object at 0x1050563c8>
<__main__.User object at 0x10551a208>
<__main__.User object at 0x1050563c8>
<__main__.User object at 0x1055a93c8>
<__main__.User object at 0x1050563c8>
<__main__.User object at 0x105527160>
<__main__.User object at 0x1055f4e48>
<__main__.User object at 0x1055e6c88>
<__main__.User object at 0x1055afcf8>
<__main__.User object at 0x105605940>
```

这在 Java 中，是可以使用饿汉模式来避免这个问题，在 Python 中我想到的办法是**加锁**。

首先实现一个给函数加锁的装饰器

```python
import threading

def synchronized(func):

    func.__lock__ = threading.Lock()

    def lock_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)
    return lock_func
```

然后在实例化对象的函数上，使用这个装饰函数。

```python
import time
import threading

class User:
    _instance = None

    @synchronized
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            time.sleep(1)
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name):
        self.name = name

def task():
    u = User("wangbm")
    print(u)

for i in range(10):
    t = threading.Thread(target=task)
    t.start()
```

结果如下，如预期只生成了一个实例。

```python
<__main__.User object at 0x10ff503c8>
<__main__.User object at 0x10ff503c8>
<__main__.User object at 0x10ff503c8>
<__main__.User object at 0x10ff503c8>
<__main__.User object at 0x10ff503c8>
<__main__.User object at 0x10ff503c8>
<__main__.User object at 0x10ff503c8>
<__main__.User object at 0x10ff503c8>
<__main__.User object at 0x10ff503c8>
<__main__.User object at 0x10ff503c8>
```

学会写只是第一步，还有一点，相当重要，要知道为何会有这个设计模式，它有什么优势，有什么局限性？

总结一下，单例模式有如下优点：

1. 全局只有一个接入点，可以更好地进行数据同步控制，避免多重占用；
2. 由于单例模式要求在全局内只有一个实例，因而可以节省比较多的内存空间；
3. 单例可长驻内存，减少系统开销。

和其他设计模式一样，单例模式有一定的适用场景，但同时它也会给我们带来一些问题。

1. 由于单例对象是全局共享，所以其状态维护需要特别小心。一处修改，全局都会受到影响。
2. 单例对象没有抽象层，扩展不便。
3. 赋于了单例以太多的职责，某种程度上违反单一职责原则（六大原则后面会讲到）;
4. 单例模式是并发协作软件模块中需要最先完成的，因而其不利于测试；
5. 单例模式在某种情况下会导致“资源瓶颈”。

------

参考文章

- [Python与设计模式--单例模式](https://yq.aliyun.com/articles/70418?utm_content=m_14908#comment)
- [Python线程安全的单例模式](https://blog.csdn.net/lucky404/article/details/79668131)

