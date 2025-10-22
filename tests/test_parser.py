"""
表达式解析器测试模块

测试表达式解析器的各种功能和边界情况
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from expression_parser import ExpressionParser, evaluate_expression, Token
from rational import Rational


class TestExpressionParser(unittest.TestCase):
    """表达式解析器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = ExpressionParser()
    
    def test_tokenize_basic(self):
        """测试基本词法分析"""
        # 测试简单表达式
        tokens = self.parser.tokenize("1+2")
        expected = [
            Token('NUMBER', Rational(1)),
            Token('OPERATOR', '+'),
            Token('NUMBER', Rational(2))
        ]
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0].type, 'NUMBER')
        self.assertEqual(tokens[0].value, Rational(1))
        self.assertEqual(tokens[1].type, 'OPERATOR')
        self.assertEqual(tokens[1].value, '+')
        self.assertEqual(tokens[2].type, 'NUMBER')
        self.assertEqual(tokens[2].value, Rational(2))
    
    def test_tokenize_fractions(self):
        """测试分数词法分析"""
        tokens = self.parser.tokenize("1/2+3/4")
        self.assertEqual(len(tokens), 3)  # 1/2, +, 3/4
        self.assertEqual(tokens[0].value, Rational(1, 2))
        self.assertEqual(tokens[1].value, '+')
        self.assertEqual(tokens[2].value, Rational(3, 4))
    
    def test_tokenize_negative_numbers(self):
        """测试负数词法分析"""
        tokens = self.parser.tokenize("-1+2")
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0].value, Rational(-1))
        self.assertEqual(tokens[2].value, Rational(2))
    
    def test_tokenize_with_parentheses(self):
        """测试带括号的词法分析"""
        tokens = self.parser.tokenize("(1+2)*3")
        self.assertEqual(len(tokens), 7)
        self.assertEqual(tokens[0].type, 'PARENTHESIS')
        self.assertEqual(tokens[0].value, '(')
        self.assertEqual(tokens[4].type, 'PARENTHESIS')
        self.assertEqual(tokens[4].value, ')')
    
    def test_invalid_characters(self):
        """测试无效字符"""
        with self.assertRaises(ValueError):
            self.parser.tokenize("1+a")
        
        with self.assertRaises(ValueError):
            self.parser.tokenize("1@2")
    
    def test_invalid_fraction_format(self):
        """测试无效分数格式"""
        with self.assertRaises(ValueError):
            self.parser.tokenize("1/")
        
        with self.assertRaises(ValueError):
            self.parser.tokenize("/2")
    
    def test_infix_to_postfix_basic(self):
        """测试基本中缀转后缀"""
        tokens = [
            Token('NUMBER', Rational(1)),
            Token('OPERATOR', '+'),
            Token('NUMBER', Rational(2))
        ]
        postfix = self.parser.infix_to_postfix(tokens)
        
        expected_types = ['NUMBER', 'NUMBER', 'OPERATOR']
        actual_types = [token.type for token in postfix]
        self.assertEqual(actual_types, expected_types)
    
    def test_infix_to_postfix_precedence(self):
        """测试运算符优先级"""
        tokens = [
            Token('NUMBER', Rational(1)),
            Token('OPERATOR', '+'),
            Token('NUMBER', Rational(2)),
            Token('OPERATOR', '*'),
            Token('NUMBER', Rational(3))
        ]
        postfix = self.parser.infix_to_postfix(tokens)
        
        # 应该是 1 2 3 * + 的顺序
        expected_values = [Rational(1), Rational(2), Rational(3), '*', '+']
        actual_values = [token.value for token in postfix]
        self.assertEqual(actual_values, expected_values)
    
    def test_infix_to_postfix_parentheses(self):
        """测试括号优先级"""
        tokens = [
            Token('PARENTHESIS', '('),
            Token('NUMBER', Rational(1)),
            Token('OPERATOR', '+'),
            Token('NUMBER', Rational(2)),
            Token('PARENTHESIS', ')'),
            Token('OPERATOR', '*'),
            Token('NUMBER', Rational(3))
        ]
        postfix = self.parser.infix_to_postfix(tokens)
        
        # 应该是 1 2 + 3 * 的顺序
        expected_values = [Rational(1), Rational(2), '+', Rational(3), '*']
        actual_values = [token.value for token in postfix]
        self.assertEqual(actual_values, expected_values)
    
    def test_mismatched_parentheses(self):
        """测试括号不匹配"""
        tokens = [
            Token('PARENTHESIS', '('),
            Token('NUMBER', Rational(1)),
            Token('OPERATOR', '+'),
            Token('NUMBER', Rational(2))
        ]
        
        with self.assertRaises(ValueError):
            self.parser.infix_to_postfix(tokens)
    
    def test_evaluate_postfix_basic(self):
        """测试基本后缀表达式计算"""
        tokens = [
            Token('NUMBER', Rational(1)),
            Token('NUMBER', Rational(2)),
            Token('OPERATOR', '+')
        ]
        result = self.parser.evaluate_postfix(tokens)
        self.assertEqual(result, Rational(3))
    
    def test_evaluate_postfix_fractions(self):
        """测试分数计算"""
        tokens = [
            Token('NUMBER', Rational(1, 2)),
            Token('NUMBER', Rational(1, 3)),
            Token('OPERATOR', '+')
        ]
        result = self.parser.evaluate_postfix(tokens)
        self.assertEqual(result, Rational(5, 6))
    
    def test_evaluate_postfix_division(self):
        """测试除法计算"""
        tokens = [
            Token('NUMBER', Rational(6)),
            Token('NUMBER', Rational(2)),
            Token('OPERATOR', '/')
        ]
        result = self.parser.evaluate_postfix(tokens)
        self.assertEqual(result, Rational(3))
    
    def test_evaluate_postfix_division_by_zero(self):
        """测试除零异常"""
        tokens = [
            Token('NUMBER', Rational(1)),
            Token('NUMBER', Rational(0)),
            Token('OPERATOR', '/')
        ]
        
        with self.assertRaises(ZeroDivisionError):
            self.parser.evaluate_postfix(tokens)
    
    def test_evaluate_postfix_insufficient_operands(self):
        """测试操作数不足"""
        tokens = [
            Token('NUMBER', Rational(1)),
            Token('OPERATOR', '+')
        ]
        
        with self.assertRaises(ValueError):
            self.parser.evaluate_postfix(tokens)
    
    def test_parse_simple_expressions(self):
        """测试简单表达式解析"""
        # 基本运算
        self.assertEqual(self.parser.parse("1+2"), Rational(3))
        self.assertEqual(self.parser.parse("3-1"), Rational(2))
        self.assertEqual(self.parser.parse("2*3"), Rational(6))
        self.assertEqual(self.parser.parse("6/2"), Rational(3))
    
    def test_parse_fraction_expressions(self):
        """测试分数表达式解析"""
        # 分数运算
        self.assertEqual(self.parser.parse("1/2+1/3"), Rational(5, 6))
        self.assertEqual(self.parser.parse("1/2-1/3"), Rational(1, 6))
        self.assertEqual(self.parser.parse("1/2*2/3"), Rational(1, 3))
        self.assertEqual(self.parser.parse("1/2/1/3"), Rational(3, 2))
    
    def test_parse_precedence(self):
        """测试运算符优先级"""
        # 乘法优先级高于加法
        self.assertEqual(self.parser.parse("1+2*3"), Rational(7))
        self.assertEqual(self.parser.parse("2*3+1"), Rational(7))
        
        # 除法优先级高于减法
        self.assertEqual(self.parser.parse("6-6/2"), Rational(3))
        self.assertEqual(self.parser.parse("6/2-1"), Rational(2))
    
    def test_parse_parentheses(self):
        """测试括号优先级"""
        # 括号改变优先级
        self.assertEqual(self.parser.parse("(1+2)*3"), Rational(9))
        self.assertEqual(self.parser.parse("1*(2+3)"), Rational(5))
        self.assertEqual(self.parser.parse("(6-3)/3"), Rational(1))
    
    def test_parse_complex_expressions(self):
        """测试复杂表达式"""
        # 复杂表达式
        self.assertEqual(self.parser.parse("1+2*3-4"), Rational(3))
        self.assertEqual(self.parser.parse("(1+2)*(3-1)"), Rational(6))
        self.assertEqual(self.parser.parse("1/2+1/3-1/6"), Rational(2, 3))
        self.assertEqual(self.parser.parse("(1/2+1/3)*2"), Rational(5, 3))
    
    def test_parse_negative_numbers(self):
        """测试负数表达式"""
        self.assertEqual(self.parser.parse("-1+2"), Rational(1))
        self.assertEqual(self.parser.parse("1+-2"), Rational(-1))
        self.assertEqual(self.parser.parse("-1*-2"), Rational(2))
        self.assertEqual(self.parser.parse("(-1+2)*3"), Rational(3))
    
    def test_parse_edge_cases(self):
        """测试边界情况"""
        # 单个数字
        self.assertEqual(self.parser.parse("5"), Rational(5))
        self.assertEqual(self.parser.parse("1/2"), Rational(1, 2))
        
        # 嵌套括号
        self.assertEqual(self.parser.parse("((1+2)*3)"), Rational(9))
        self.assertEqual(self.parser.parse("(1+(2*3))"), Rational(7))
    
    def test_parse_invalid_expressions(self):
        """测试无效表达式"""
        # 空表达式
        with self.assertRaises(ValueError):
            self.parser.parse("")
        
        with self.assertRaises(ValueError):
            self.parser.parse("   ")
        
        # 括号不匹配
        with self.assertRaises(ValueError):
            self.parser.parse("(1+2")
        
        with self.assertRaises(ValueError):
            self.parser.parse("1+2)")
        
        # 无效字符
        with self.assertRaises(ValueError):
            self.parser.parse("1+a")
        
        # 除零（在词法分析阶段就会被捕获）
        with self.assertRaises(ValueError):
            self.parser.parse("1/0")
        
        # 操作符错误
        with self.assertRaises(ValueError):
            self.parser.parse("1++2")
        
        with self.assertRaises(ValueError):
            self.parser.parse("1+")
    
    def test_evaluate_expression_function(self):
        """测试便捷函数"""
        self.assertEqual(evaluate_expression("1+2"), Rational(3))
        self.assertEqual(evaluate_expression("1/2+1/3"), Rational(5, 6))
        self.assertEqual(evaluate_expression("(1+2)*3"), Rational(9))


class TestExpressionParserIntegration(unittest.TestCase):
    """表达式解析器集成测试"""
    
    def test_complex_mathematical_expressions(self):
        """测试复杂数学表达式"""
        parser = ExpressionParser()
        
        # 测试用例：小学数学常见表达式
        test_cases = [
            ("1+2+3", Rational(6)),
            ("1*2*3", Rational(6)),
            ("1+2*3+4", Rational(11)),
            ("(1+2)*(3+4)", Rational(21)),
            ("1/2+1/4+1/8", Rational(7, 8)),
            ("(1/2+1/3)*6", Rational(5)),
            ("2+3*4-5", Rational(9)),
            ("(2+3)*(4-1)", Rational(15)),
            ("1-1/2+1/4", Rational(3, 4)),
            ("(1-1/2)/(1/4)", Rational(2))
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = parser.parse(expression)
                self.assertEqual(result, expected, 
                               f"表达式 {expression} 计算结果错误")
    
    def test_expression_with_spaces(self):
        """测试带空格的表达式"""
        parser = ExpressionParser()
        
        # 应该能正确处理空格
        self.assertEqual(parser.parse("1 + 2"), Rational(3))
        self.assertEqual(parser.parse(" 1 + 2 "), Rational(3))
        self.assertEqual(parser.parse("1 + 2 * 3"), Rational(7))
        self.assertEqual(parser.parse("( 1 + 2 ) * 3"), Rational(9))


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
