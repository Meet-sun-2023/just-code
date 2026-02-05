"""
斐波那契数列计算函数
斐波那契数列：0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...
每个数字是前两个数字之和
"""


def fibonacci_iterative(n):
    """
    迭代方式计算第 n 个斐波那契数
    时间复杂度：O(n)
    空间复杂度：O(1)
    
    Args:
        n: 要计算的斐波那契数的索引（从0开始）
    
    Returns:
        第 n 个斐波那契数
    """
    if n < 0:
        raise ValueError("n 必须是非负整数")
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_recursive(n):
    """
    递归方式计算第 n 个斐波那契数
    时间复杂度：O(2^n) - 效率较低
    空间复杂度：O(n)
    
    Args:
        n: 要计算的斐波那契数的索引（从0开始）
    
    Returns:
        第 n 个斐波那契数
    """
    if n < 0:
        raise ValueError("n 必须是非负整数")
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fibonacci_memo(n, memo=None):
    """
    使用记忆化（缓存）的递归方式计算第 n 个斐波那契数
    时间复杂度：O(n)
    空间复杂度：O(n)
    
    Args:
        n: 要计算的斐波那契数的索引（从0开始）
        memo: 缓存字典（内部使用）
    
    Returns:
        第 n 个斐波那契数
    """
    if n < 0:
        raise ValueError("n 必须是非负整数")
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
    return memo[n]


def fibonacci_sequence(n):
    """
    生成前 n 个斐波那契数（返回列表）
    
    Args:
        n: 要生成的斐波那契数的数量
    
    Returns:
        包含前 n 个斐波那契数的列表
    """
    if n < 0:
        raise ValueError("n 必须是非负整数")
    if n == 0:
        return []
    if n == 1:
        return [0]
    
    sequence = [0, 1]
    for _ in range(2, n):
        sequence.append(sequence[-1] + sequence[-2])
    return sequence


def fibonacci_generator():
    """
    斐波那契数列生成器
    可以无限生成斐波那契数
    
    Yields:
        斐波那契数列中的每个数
    """
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# 示例使用
if __name__ == "__main__":
    # 测试各种实现方式
    n = 10
    
    print(f"计算第 {n} 个斐波那契数：")
    print(f"迭代方式: {fibonacci_iterative(n)}")
    print(f"递归方式: {fibonacci_recursive(n)}")
    print(f"记忆化递归: {fibonacci_memo(n)}")
    
    print(f"\n前 {n} 个斐波那契数:")
    print(fibonacci_sequence(n))
    
    print("\n使用生成器获取前 10 个斐波那契数:")
    gen = fibonacci_generator()
    for i, fib in enumerate(gen):
        if i >= 10:
            break
        print(fib, end=" ")
    print()
    
    # 性能对比
    import time
    
    print("\n性能对比（计算第 35 个斐波那契数）:")
    
    # 迭代方式
    start = time.time()
    result = fibonacci_iterative(35)
    end = time.time()
    print(f"迭代方式: {result}, 耗时: {(end-start)*1000:.4f}ms")
    
    # 记忆化递归
    start = time.time()
    result = fibonacci_memo(35)
    end = time.time()
    print(f"记忆化递归: {result}, 耗时: {(end-start)*1000:.4f}ms")
    
    # 普通递归（较慢）
    start = time.time()
    result = fibonacci_recursive(35)
    end = time.time()
    print(f"普通递归: {result}, 耗时: {(end-start)*1000:.4f}ms")
