"""
表达式解析器模块

支持四则运算和括号优先级的数学表达式解析和求值
"""

import re
import sys
import os
from typing import List, Union, Tuple

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))
from rational import Rational


class Token:
    """词法单元类"""
    
    def __init__(self, type_: str, value: Union[str, Rational]):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class ExpressionParser:
    """表达式解析器"""
    
    def __init__(self):
        # 运算符优先级
        self.precedence = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            '(': 0,
            ')': 0
        }
    
    def tokenize(self, expression: str) -> List[Token]:
        """
        词法分析：将表达式字符串分解为词法单元
        
        Args:
            expression (str): 数学表达式字符串
            
        Returns:
            List[Token]: 词法单元列表
        """
        # 移除所有空白字符
        expression = re.sub(r'\s+', '', expression)
        
        tokens = []
        i = 0
        
        while i < len(expression):
            char = expression[i]
            
            # 处理数字（包括分数）
            if char.isdigit():
                # 收集数字部分
                number_str = ''
                
                # 收集整数部分
                while i < len(expression) and expression[i].isdigit():
                    number_str += expression[i]
                    i += 1
                
                # 检查是否有分数部分
                if i < len(expression) and expression[i] == '/':
                    number_str += '/'
                    i += 1
                    
                    # 收集分母
                    while i < len(expression) and expression[i].isdigit():
                        number_str += expression[i]
                        i += 1
                
                # 创建有理数
                try:
                    if '/' in number_str:
                        parts = number_str.split('/')
                        if len(parts) != 2 or not parts[0] or not parts[1]:
                            raise ValueError("无效的分数格式")
                        numerator = int(parts[0])
                        denominator = int(parts[1])
                        rational = Rational(numerator, denominator)
                    else:
                        rational = Rational(int(number_str))
                    
                    tokens.append(Token('NUMBER', rational))
                except ValueError as e:
                    raise ValueError(f"无效的数字格式: {number_str}") from e
            
            # 处理负号（可能是负数或减法运算符）
            elif char == '-':
                # 检查是否为负数（前面是运算符、括号或开头）
                is_negative = (i == 0 or expression[i-1] in '+-*/(')
                
                if is_negative:
                    i += 1
                    if i >= len(expression) or not expression[i].isdigit():
                        # 如果负号后面没有数字，则作为运算符处理
                        tokens.append(Token('OPERATOR', '-'))
                        continue
                    
                    # 收集负数部分
                    number_str = '-'
                    
                    # 收集整数部分
                    while i < len(expression) and expression[i].isdigit():
                        number_str += expression[i]
                        i += 1
                    
                    # 检查是否有分数部分
                    if i < len(expression) and expression[i] == '/':
                        number_str += '/'
                        i += 1
                        
                        # 收集分母
                        while i < len(expression) and expression[i].isdigit():
                            number_str += expression[i]
                            i += 1
                    
                    # 创建有理数
                    try:
                        if '/' in number_str:
                            parts = number_str.split('/')
                            if len(parts) != 2 or not parts[0] or not parts[1]:
                                raise ValueError("无效的分数格式")
                            numerator = int(parts[0])
                            denominator = int(parts[1])
                            rational = Rational(numerator, denominator)
                        else:
                            rational = Rational(int(number_str))
                        
                        tokens.append(Token('NUMBER', rational))
                    except ValueError as e:
                        raise ValueError(f"无效的数字格式: {number_str}") from e
                else:
                    # 作为减法运算符处理
                    tokens.append(Token('OPERATOR', '-'))
                    i += 1
            
            # 处理其他运算符
            elif char in '+*/':
                # 检查是否为无效的分数格式（以/开头）
                if char == '/' and (i == 0 or expression[i-1] in '+-*/('):
                    raise ValueError("无效的分数格式：不能以/开头")
                tokens.append(Token('OPERATOR', char))
                i += 1
            
            # 处理括号
            elif char in '()':
                tokens.append(Token('PARENTHESIS', char))
                i += 1
            
            else:
                raise ValueError(f"无效的字符: {char}")
        
        return tokens
    
    def infix_to_postfix(self, tokens: List[Token]) -> List[Token]:
        """
        中缀表达式转后缀表达式（逆波兰表示法）
        
        Args:
            tokens (List[Token]): 中缀表达式的词法单元列表
            
        Returns:
            List[Token]: 后缀表达式的词法单元列表
        """
        output = []
        operator_stack = []
        
        for token in tokens:
            if token.type == 'NUMBER':
                output.append(token)
            
            elif token.type == 'OPERATOR':
                # 处理运算符优先级
                while (operator_stack and 
                       operator_stack[-1].type == 'OPERATOR' and
                       self.precedence[operator_stack[-1].value] >= 
                       self.precedence[token.value]):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            
            elif token.type == 'PARENTHESIS' and token.value == '(':
                operator_stack.append(token)
            
            elif token.type == 'PARENTHESIS' and token.value == ')':
                # 处理括号内的运算符
                while (operator_stack and 
                       operator_stack[-1].value != '('):
                    output.append(operator_stack.pop())
                
                if not operator_stack:
                    raise ValueError("括号不匹配")
                operator_stack.pop()  # 移除 '('
        
        # 处理剩余的运算符
        while operator_stack:
            if operator_stack[-1].value in '()':
                raise ValueError("括号不匹配")
            output.append(operator_stack.pop())
        
        return output
    
    def evaluate_postfix(self, tokens: List[Token]) -> Rational:
        """
        计算后缀表达式
        
        Args:
            tokens (List[Token]): 后缀表达式的词法单元列表
            
        Returns:
            Rational: 计算结果
        """
        stack = []
        
        for token in tokens:
            if token.type == 'NUMBER':
                stack.append(token.value)
            
            elif token.type == 'OPERATOR':
                if len(stack) < 2:
                    raise ValueError("表达式格式错误：运算符缺少操作数")
                
                right = stack.pop()
                left = stack.pop()
                
                if token.value == '+':
                    result = left + right
                elif token.value == '-':
                    result = left - right
                elif token.value == '*':
                    result = left * right
                elif token.value == '/':
                    if right.is_zero():
                        raise ZeroDivisionError("除数不能为零")
                    result = left / right
                else:
                    raise ValueError(f"未知的运算符: {token.value}")
                
                stack.append(result)
        
        if len(stack) != 1:
            raise ValueError("表达式格式错误：操作数过多")
        
        return stack[0]
    
    def parse(self, expression: str) -> Rational:
        """
        解析并计算数学表达式
        
        Args:
            expression (str): 数学表达式字符串
            
        Returns:
            Rational: 计算结果
        """
        if not expression.strip():
            raise ValueError("表达式不能为空")
        
        try:
            # 词法分析
            tokens = self.tokenize(expression)
            
            if not tokens:
                raise ValueError("表达式为空")
            
            # 转换为后缀表达式
            postfix_tokens = self.infix_to_postfix(tokens)
            
            # 计算后缀表达式
            result = self.evaluate_postfix(postfix_tokens)
            
            return result
            
        except Exception as e:
            raise ValueError(f"表达式解析错误: {e}") from e


# 便捷函数
def evaluate_expression(expression: str) -> Rational:
    """
    计算数学表达式的便捷函数
    
    Args:
        expression (str): 数学表达式字符串
        
    Returns:
        Rational: 计算结果
    """
    parser = ExpressionParser()
    return parser.parse(expression)


# 测试代码
if __name__ == "__main__":
    parser = ExpressionParser()
    
    # 测试用例
    test_expressions = [
        "1 + 2",
        "3 * 4",
        "1/2 + 1/3",
        "(1 + 2) * 3",
        "1 + 2 * 3",
        "1/2 * 2/3",
        "1 - 1/2",
        "(1/2 + 1/3) / (1/4)",
        "2 + 3 * 4 - 1",
        "1/2 + 1/3 - 1/6"
    ]
    
    print("=== 表达式解析器测试 ===")
    for expr in test_expressions:
        try:
            result = parser.parse(expr)
            print(f"{expr} = {result}")
        except Exception as e:
            print(f"{expr} = 错误: {e}")
