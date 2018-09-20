def selecton_sort(p):
    """ 选择排序
        p: 数字列表 """
    for i in range(len(p) - 1):
        min = i
        for j in range(i + 1, len(p)):
            if p[min] > p[j]:
                min = j
        if min != i:
            p[min], p[i] = p[i], p[min]
    return p


def dubble_sort(p):
    """ 冒泡排序
        p: 数字列表 """
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i] > p[j]:
                p[i], p[j] = p[j], p[i]
    return p


def insertion_sort(p):
    """ 插入排序
        p: 数字列表 """
    for i in range(1, len(p)):
        j = i
        while j > 0 and a[j - 1] > a[i]:
            j -= 1
        p.insert(j, p[i])
        p.pop(i + 1)
    return p


def quick_sort(p, start=None, end=None):
    """ 快速排序
        p: 数字列表
        start: 列表的开始索引
        end: 列表的结尾索引  """
    start = 0 if start is None else start
    end = len(p) - 1 if end is None else end
    if start < end:
        i, j = start, end
        base = p[i]
        while i < j:
            while i < j and p[j] >= base:
                j -= 1
            p[i] = p[j]
            while i < j and p[i] <= base:
                i += 1
            p[j] = p[i]
        p[i] = base
        quick_sort(p, start, i - 1)
        quick_sort(p, j + 1, end)
    return p


from collections import defaultdict


def mysort():
    """
    大量数据排序：
    比如你有100GB的数据需要排序，一次性加载到内存是不行的。
    """
    # 排序磁盘文件，比如磁盘有100000个文件，
    # 每个文件由100个 1--10000 范围内的数字组成

    counter = defaultdict(int)
    for i in range(1, 100000):
        for n in open(f'{i}.txt', 'r'):
            counter[int(n)] += 1
    with open('sort.txt', 'w') as f:
        for i in range(1, 10001):
            count = counter[i]
            if count:
                f.write(f'{i}\n' * count)


if __name__ == '__main__':
    import random
    # 选择排序测试
    a = [random.randint(1, 100) for i in range(10)]
    print(selecton_sort(a))
    # 冒泡排序测试
    a = [random.randint(1, 100) for i in range(10)]
    print(dubble_sort(a))
    # 插入排序测试
    a = [random.randint(1, 100) for i in range(10)]
    print(insertion_sort(a))
    # 快速排序测试
    a = [random.randint(1, 100) for i in range(10)]
    print(quick_sort(a))

