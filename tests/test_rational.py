"""
有理数类型测试模块

测试有理数类的各种功能和边界情况
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rational import Rational, create_rational


class TestRational(unittest.TestCase):
    """有理数类测试"""
    
    def test_initialization(self):
        """测试初始化"""
        # 测试自然数
        r1 = Rational(3)
        self.assertEqual(r1.numerator, 3)
        self.assertEqual(r1.denominator, 1)
        
        # 测试真分数
        r2 = Rational(3, 5)
        self.assertEqual(r2.numerator, 3)
        self.assertEqual(r2.denominator, 5)
        
        # 测试带分数（假分数）
        r3 = Rational(7, 5)
        self.assertEqual(r3.numerator, 7)
        self.assertEqual(r3.denominator, 5)
        
        # 测试负数
        r4 = Rational(-3, 5)
        self.assertEqual(r4.numerator, -3)
        self.assertEqual(r4.denominator, 5)
        
        # 测试分母为负数
        r5 = Rational(3, -5)
        self.assertEqual(r5.numerator, -3)
        self.assertEqual(r5.denominator, 5)
    
    def test_zero_denominator(self):
        """测试分母为0的异常"""
        with self.assertRaises(ValueError):
            Rational(3, 0)
    
    def test_simplification(self):
        """测试约分功能"""
        # 测试自动约分
        r1 = Rational(6, 8)
        self.assertEqual(r1.numerator, 3)
        self.assertEqual(r1.denominator, 4)
        
        # 测试分子为0
        r2 = Rational(0, 5)
        self.assertEqual(r2.numerator, 0)
        self.assertEqual(r2.denominator, 1)
        
        # 测试负数约分
        r3 = Rational(-6, 8)
        self.assertEqual(r3.numerator, -3)
        self.assertEqual(r3.denominator, 4)
    
    def test_from_string(self):
        """测试从字符串创建"""
        # 测试自然数
        r1 = Rational.from_string("3")
        self.assertEqual(r1.numerator, 3)
        self.assertEqual(r1.denominator, 1)
        
        # 测试真分数
        r2 = Rational.from_string("3/5")
        self.assertEqual(r2.numerator, 3)
        self.assertEqual(r2.denominator, 5)
        
        # 测试带分数
        r3 = Rational.from_string("1'3/5")
        self.assertEqual(r3.numerator, 8)  # 1*5 + 3 = 8
        self.assertEqual(r3.denominator, 5)
        
        # 测试负数带分数
        r4 = Rational.from_string("-1'3/5")
        self.assertEqual(r4.numerator, -8)
        self.assertEqual(r4.denominator, 5)
        
        # 测试无效格式
        with self.assertRaises(ValueError):
            Rational.from_string("1'3")
        
        with self.assertRaises(ValueError):
            Rational.from_string("1/2/3")
    
    def test_to_string(self):
        """测试字符串格式化"""
        # 测试自然数
        r1 = Rational(3)
        self.assertEqual(r1.to_string(), "3")
        
        # 测试真分数
        r2 = Rational(3, 5)
        self.assertEqual(r2.to_string(), "3/5")
        
        # 测试带分数
        r3 = Rational(8, 5)
        self.assertEqual(r3.to_string(), "1'3/5")
        
        # 测试负数
        r4 = Rational(-3, 5)
        self.assertEqual(r4.to_string(), "-3/5")
        
        # 测试负数带分数
        r5 = Rational(-8, 5)
        self.assertEqual(r5.to_string(), "-1'3/5")
        
        # 测试零
        r6 = Rational(0)
        self.assertEqual(r6.to_string(), "0")
    
    def test_arithmetic_operations(self):
        """测试算术运算"""
        r1 = Rational(3, 5)  # 3/5
        r2 = Rational(1, 3)  # 1/3
        
        # 测试加法
        result = r1 + r2
        self.assertEqual(result.numerator, 14)  # 3*3 + 1*5 = 14
        self.assertEqual(result.denominator, 15)  # 5*3 = 15
        
        # 测试减法
        result = r1 - r2
        self.assertEqual(result.numerator, 4)  # 3*3 - 1*5 = 4
        self.assertEqual(result.denominator, 15)
        
        # 测试乘法
        result = r1 * r2
        self.assertEqual(result.numerator, 1)  # 3*1 = 3, 约分后为1
        self.assertEqual(result.denominator, 5)  # 5*3 = 15, 约分后为5
        
        # 测试除法
        result = r1 / r2
        self.assertEqual(result.numerator, 9)  # 3*3 = 9
        self.assertEqual(result.denominator, 5)  # 5*1 = 5
    
    def test_arithmetic_with_integers(self):
        """测试与整数的运算"""
        r1 = Rational(3, 5)
        
        # 测试与整数相加
        result = r1 + 2
        self.assertEqual(result.numerator, 13)  # 3 + 2*5 = 13
        self.assertEqual(result.denominator, 5)
        
        # 测试与整数相乘
        result = r1 * 3
        self.assertEqual(result.numerator, 9)  # 3*3 = 9
        self.assertEqual(result.denominator, 5)
    
    def test_division_by_zero(self):
        """测试除零异常"""
        r1 = Rational(3, 5)
        r2 = Rational(0)
        
        with self.assertRaises(ZeroDivisionError):
            r1 / r2
    
    def test_comparison_operations(self):
        """测试比较运算"""
        r1 = Rational(3, 5)  # 0.6
        r2 = Rational(1, 2)  # 0.5
        r3 = Rational(6, 10)  # 0.6
        
        # 测试相等
        self.assertTrue(r1 == r3)
        self.assertFalse(r1 == r2)
        
        # 测试小于
        self.assertTrue(r2 < r1)
        self.assertFalse(r1 < r2)
        
        # 测试大于
        self.assertTrue(r1 > r2)
        self.assertFalse(r2 > r1)
        
        # 测试小于等于
        self.assertTrue(r1 <= r3)
        self.assertTrue(r2 <= r1)
        self.assertFalse(r1 <= r2)
        
        # 测试大于等于
        self.assertTrue(r1 >= r3)
        self.assertTrue(r1 >= r2)
        self.assertFalse(r2 >= r1)
    
    def test_unary_operations(self):
        """测试一元运算"""
        r1 = Rational(3, 5)
        
        # 测试取负
        neg_r1 = -r1
        self.assertEqual(neg_r1.numerator, -3)
        self.assertEqual(neg_r1.denominator, 5)
        
        # 测试取绝对值
        abs_r1 = abs(r1)
        self.assertEqual(abs_r1.numerator, 3)
        self.assertEqual(abs_r1.denominator, 5)
        
        # 测试负数取绝对值
        r2 = Rational(-3, 5)
        abs_r2 = abs(r2)
        self.assertEqual(abs_r2.numerator, 3)
        self.assertEqual(abs_r2.denominator, 5)
    
    def test_type_checking(self):
        """测试类型判断"""
        # 测试正数
        r1 = Rational(3, 5)
        self.assertTrue(r1.is_positive())
        self.assertFalse(r1.is_negative())
        self.assertFalse(r1.is_zero())
        
        # 测试负数
        r2 = Rational(-3, 5)
        self.assertFalse(r2.is_positive())
        self.assertTrue(r2.is_negative())
        self.assertFalse(r2.is_zero())
        
        # 测试零
        r3 = Rational(0)
        self.assertFalse(r3.is_positive())
        self.assertFalse(r3.is_negative())
        self.assertTrue(r3.is_zero())
        
        # 测试整数
        r4 = Rational(3)
        self.assertTrue(r4.is_integer())
        
        r5 = Rational(3, 5)
        self.assertFalse(r5.is_integer())
        
        # 测试真分数
        r6 = Rational(3, 5)
        self.assertTrue(r6.is_proper_fraction())
        self.assertFalse(r6.is_improper_fraction())
        
        # 测试假分数
        r7 = Rational(7, 5)
        self.assertFalse(r7.is_proper_fraction())
        self.assertTrue(r7.is_improper_fraction())
    
    def test_conversion_methods(self):
        """测试转换方法"""
        r1 = Rational(3, 5)
        
        # 测试转换为浮点数
        self.assertAlmostEqual(r1.to_float(), 0.6, places=10)
        
        # 测试求倒数
        reciprocal = r1.reciprocal()
        self.assertEqual(reciprocal.numerator, 5)
        self.assertEqual(reciprocal.denominator, 3)
        
        # 测试零的倒数
        r2 = Rational(0)
        with self.assertRaises(ZeroDivisionError):
            r2.reciprocal()
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试大数
        r1 = Rational(1000000, 999999)
        self.assertEqual(r1.numerator, 1000000)
        self.assertEqual(r1.denominator, 999999)
        
        # 测试最小分数
        r2 = Rational(1, 1000000)
        self.assertEqual(r2.numerator, 1)
        self.assertEqual(r2.denominator, 1000000)
        
        # 测试负零（应该被处理为正零）
        r3 = Rational(0, -1)
        self.assertEqual(r3.numerator, 0)
        self.assertEqual(r3.denominator, 1)
    
    def test_create_rational_function(self):
        """测试便捷创建函数"""
        # 测试整数
        r1 = create_rational(3)
        self.assertEqual(r1.numerator, 3)
        self.assertEqual(r1.denominator, 1)
        
        # 测试字符串
        r2 = create_rational("3/5")
        self.assertEqual(r2.numerator, 3)
        self.assertEqual(r2.denominator, 5)
        
        # 测试元组
        r3 = create_rational((3, 5))
        self.assertEqual(r3.numerator, 3)
        self.assertEqual(r3.denominator, 5)
        
        # 测试无效类型
        with self.assertRaises(ValueError):
            create_rational([3, 5])
    
    def test_string_representation(self):
        """测试字符串表示"""
        r1 = Rational(3, 5)
        
        # 测试__str__
        self.assertEqual(str(r1), "3/5")
        
        # 测试__repr__
        self.assertEqual(repr(r1), "Rational(3, 5)")


class TestRationalIntegration(unittest.TestCase):
    """有理数集成测试"""
    
    def test_complex_calculations(self):
        """测试复杂计算"""
        # 测试复杂表达式：1/2 + 1/3 - 1/6
        r1 = Rational(1, 2)
        r2 = Rational(1, 3)
        r3 = Rational(1, 6)
        
        result = r1 + r2 - r3
        self.assertEqual(result.numerator, 2)  # 3/6 + 2/6 - 1/6 = 4/6 = 2/3
        self.assertEqual(result.denominator, 3)
    
    def test_mixed_fraction_operations(self):
        """测试带分数运算"""
        # 测试：1'1/2 + 2'1/3
        r1 = Rational.from_string("1'1/2")  # 3/2
        r2 = Rational.from_string("2'1/3")  # 7/3
        
        result = r1 + r2
        self.assertEqual(result.numerator, 23)  # 9/6 + 14/6 = 23/6
        self.assertEqual(result.denominator, 6)
        
        # 验证结果格式
        self.assertEqual(result.to_string(), "3'5/6")
    
    def test_chain_operations(self):
        """测试链式运算"""
        # 测试：((1/2 + 1/3) * 2) / (1/4)
        r1 = Rational(1, 2)
        r2 = Rational(1, 3)
        r3 = Rational(2)
        r4 = Rational(1, 4)
        
        result = ((r1 + r2) * r3) / r4
        self.assertEqual(result.numerator, 20)  # (5/6 * 2) / (1/4) = (10/6) / (1/4) = 40/6 = 20/3
        self.assertEqual(result.denominator, 3)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
