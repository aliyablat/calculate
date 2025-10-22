"""
有理数类型模块

支持自然数、真分数、带分数的统一运算
"""

import math
from typing import Union, Tuple


class Rational:
    """
    有理数类，支持自然数、真分数、带分数的运算
    
    内部统一用分数表示：
    - 自然数：分子为数值，分母为1
    - 真分数：分子小于分母
    - 带分数：转换为假分数表示
    
    Attributes:
        numerator (int): 分子
        denominator (int): 分母
    """
    
    def __init__(self, numerator: int, denominator: int = 1):
        """
        初始化有理数
        
        Args:
            numerator (int): 分子
            denominator (int): 分母，默认为1（自然数）
            
        Raises:
            ValueError: 分母为0时抛出异常
        """
        if denominator == 0:
            raise ValueError("分母不能为0")
        
        # 处理负数情况
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator
        
        self.numerator = numerator
        self.denominator = denominator
        
        # 自动约分
        self.simplify()
    
    @classmethod
    def from_string(cls, s: str) -> 'Rational':
        """
        从字符串创建有理数
        
        支持的格式：
        - "3" -> 自然数3
        - "3/5" -> 真分数3/5
        - "1'3/5" -> 带分数1又3/5
        
        Args:
            s (str): 字符串格式的有理数
            
        Returns:
            Rational: 有理数对象
        """
        s = s.strip()
        
        # 处理带分数格式 "1'3/5" 或 "-1'3/5"
        if "'" in s:
            parts = s.split("'")
            if len(parts) != 2:
                raise ValueError(f"无效的带分数格式: {s}")
            
            whole_part = int(parts[0])
            fraction_part = parts[1]
            
            if "/" not in fraction_part:
                raise ValueError(f"无效的带分数格式: {s}")
            
            frac_parts = fraction_part.split("/")
            if len(frac_parts) != 2:
                raise ValueError(f"无效的带分数格式: {s}")
            
            numerator = int(frac_parts[0])
            denominator = int(frac_parts[1])
            
            # 转换为假分数
            # 如果整数部分是负数，需要正确处理
            if whole_part < 0:
                numerator = whole_part * denominator - numerator
            else:
                numerator = whole_part * denominator + numerator
            return cls(numerator, denominator)
        
        # 处理分数格式 "3/5"
        elif "/" in s:
            parts = s.split("/")
            if len(parts) != 2:
                raise ValueError(f"无效的分数格式: {s}")
            
            numerator = int(parts[0])
            denominator = int(parts[1])
            return cls(numerator, denominator)
        
        # 处理自然数格式 "3"
        else:
            return cls(int(s))
    
    def simplify(self) -> None:
        """约分处理"""
        if self.numerator == 0:
            self.denominator = 1
            return
        
        gcd_val = math.gcd(abs(self.numerator), self.denominator)
        self.numerator //= gcd_val
        self.denominator //= gcd_val
    
    def to_string(self) -> str:
        """
        转换为字符串格式
        
        Returns:
            str: 格式化的字符串
            - 自然数：直接返回数字
            - 真分数：返回 "分子/分母"
            - 带分数：返回 "整数'分子/分母"
        """
        if self.denominator == 1:
            return str(self.numerator)
        
        # 检查是否为带分数
        if abs(self.numerator) > self.denominator:
            # 处理负数带分数的特殊情况
            if self.numerator < 0:
                # 对于负数，我们需要特殊处理
                # 例如：-8/5 = -1'3/5，而不是 -2'2/5
                abs_numerator = abs(self.numerator)
                whole_part = abs_numerator // self.denominator
                remainder = abs_numerator % self.denominator
                
                if remainder == 0:
                    return str(-whole_part)
                else:
                    return f"-{whole_part}'{remainder}/{self.denominator}"
            else:
                whole_part = self.numerator // self.denominator
                remainder = self.numerator % self.denominator
                
                if remainder == 0:
                    return str(whole_part)
                else:
                    return f"{whole_part}'{remainder}/{self.denominator}"
        
        # 真分数
        return f"{self.numerator}/{self.denominator}"
    
    def __add__(self, other: 'Rational') -> 'Rational':
        """加法运算"""
        if not isinstance(other, Rational):
            other = Rational(other)
        
        new_numerator = (self.numerator * other.denominator + 
                       other.numerator * self.denominator)
        new_denominator = self.denominator * other.denominator
        
        return Rational(new_numerator, new_denominator)
    
    def __sub__(self, other: 'Rational') -> 'Rational':
        """减法运算"""
        if not isinstance(other, Rational):
            other = Rational(other)
        
        new_numerator = (self.numerator * other.denominator - 
                       other.numerator * self.denominator)
        new_denominator = self.denominator * other.denominator
        
        return Rational(new_numerator, new_denominator)
    
    def __mul__(self, other: 'Rational') -> 'Rational':
        """乘法运算"""
        if not isinstance(other, Rational):
            other = Rational(other)
        
        new_numerator = self.numerator * other.numerator
        new_denominator = self.denominator * other.denominator
        
        return Rational(new_numerator, new_denominator)
    
    def __truediv__(self, other: 'Rational') -> 'Rational':
        """除法运算"""
        if not isinstance(other, Rational):
            other = Rational(other)
        
        if other.numerator == 0:
            raise ZeroDivisionError("除数不能为0")
        
        new_numerator = self.numerator * other.denominator
        new_denominator = self.denominator * other.numerator
        
        return Rational(new_numerator, new_denominator)
    
    def __eq__(self, other: 'Rational') -> bool:
        """相等比较"""
        if not isinstance(other, Rational):
            other = Rational(other)
        
        return (self.numerator == other.numerator and 
                self.denominator == other.denominator)
    
    def __lt__(self, other: 'Rational') -> bool:
        """小于比较"""
        if not isinstance(other, Rational):
            other = Rational(other)
        
        return (self.numerator * other.denominator < 
                other.numerator * self.denominator)
    
    def __le__(self, other: 'Rational') -> bool:
        """小于等于比较"""
        return self < other or self == other
    
    def __gt__(self, other: 'Rational') -> bool:
        """大于比较"""
        return not self <= other
    
    def __ge__(self, other: 'Rational') -> bool:
        """大于等于比较"""
        return not self < other
    
    def __neg__(self) -> 'Rational':
        """取负"""
        return Rational(-self.numerator, self.denominator)
    
    def __abs__(self) -> 'Rational':
        """取绝对值"""
        return Rational(abs(self.numerator), self.denominator)
    
    def __str__(self) -> str:
        """字符串表示"""
        return self.to_string()
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"Rational({self.numerator}, {self.denominator})"
    
    def is_positive(self) -> bool:
        """判断是否为正数"""
        return self.numerator > 0
    
    def is_negative(self) -> bool:
        """判断是否为负数"""
        return self.numerator < 0
    
    def is_zero(self) -> bool:
        """判断是否为零"""
        return self.numerator == 0
    
    def is_integer(self) -> bool:
        """判断是否为整数"""
        return self.denominator == 1
    
    def is_proper_fraction(self) -> bool:
        """判断是否为真分数"""
        return abs(self.numerator) < self.denominator and self.denominator > 1
    
    def is_improper_fraction(self) -> bool:
        """判断是否为假分数"""
        return abs(self.numerator) >= self.denominator and self.denominator > 1
    
    def to_float(self) -> float:
        """转换为浮点数"""
        return self.numerator / self.denominator
    
    def reciprocal(self) -> 'Rational':
        """求倒数"""
        if self.numerator == 0:
            raise ZeroDivisionError("0没有倒数")
        return Rational(self.denominator, self.numerator)


# 便捷函数
def create_rational(value: Union[int, str, Tuple[int, int]]) -> Rational:
    """
    创建有理数的便捷函数
    
    Args:
        value: 可以是整数、字符串或(分子,分母)元组
        
    Returns:
        Rational: 有理数对象
    """
    if isinstance(value, int):
        return Rational(value)
    elif isinstance(value, str):
        return Rational.from_string(value)
    elif isinstance(value, tuple) and len(value) == 2:
        return Rational(value[0], value[1])
    else:
        raise ValueError(f"不支持的类型: {type(value)}")


# 测试代码
if __name__ == "__main__":
    # 测试自然数
    r1 = Rational(3)
    print(f"自然数3: {r1}")
    
    # 测试真分数
    r2 = Rational(3, 5)
    print(f"真分数3/5: {r2}")
    
    # 测试带分数
    r3 = Rational(7, 5)  # 1'2/5
    print(f"带分数7/5: {r3}")
    
    # 测试字符串创建
    r4 = Rational.from_string("1'3/5")
    print(f"从字符串创建: {r4}")
    
    # 测试运算
    print(f"3/5 + 1/3 = {r2 + Rational(1, 3)}")
    print(f"3/5 - 1/3 = {r2 - Rational(1, 3)}")
    print(f"3/5 × 1/3 = {r2 * Rational(1, 3)}")
    print(f"3/5 ÷ 1/3 = {r2 / Rational(1, 3)}")
    
    # 测试比较
    print(f"3/5 > 1/3: {r2 > Rational(1, 3)}")
    print(f"3/5 == 6/10: {r2 == Rational(6, 10)}")
