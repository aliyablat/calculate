"""
题目生成器模块

生成四则运算题目，支持去重和规则验证
"""

import random
import sys
import os
from typing import List, Tuple, Set
from rational import Rational
from expression_parser import ExpressionParser
from deduplicator import Deduplicator

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))


class ProblemGenerator:
    """题目生成器"""
    
    def __init__(self, min_value: int = 1, max_value: int = 10):
        """
        初始化题目生成器
        
        Args:
            min_value (int): 最小数值，默认为1
            max_value (int): 最大数值，默认为10
        """
        self.min_value = min_value
        self.max_value = max_value
        self.parser = ExpressionParser()
        self.deduplicator = Deduplicator()
        
        # 运算符列表
        self.operators = ['+', '-', '*', '/']
        
        # 题目去重集合
        self.generated_problems = set()
    
    def generate_number(self) -> Rational:
        """
        生成随机数（自然数或分数）
        
        Returns:
            Rational: 随机生成的有理数
        """
        # 80%概率生成自然数，20%概率生成分数
        if random.random() < 0.8:
            return Rational(random.randint(self.min_value, self.max_value))
        else:
            # 生成分数
            numerator = random.randint(self.min_value, self.max_value)
            denominator = random.randint(2, self.max_value)
            return Rational(numerator, denominator)
    
    def generate_operator(self) -> str:
        """
        生成随机运算符
        
        Returns:
            str: 随机运算符
        """
        return random.choice(self.operators)
    
    def generate_simple_expression(self) -> str:
        """
        生成简单表达式（两个操作数）
        
        Returns:
            str: 生成的表达式字符串
        """
        num1 = self.generate_number()
        operator = self.generate_operator()
        num2 = self.generate_number()
        
        # 格式化表达式
        expr = f"{num1} {operator} {num2}"
        return expr
    
    def generate_complex_expression(self) -> str:
        """
        生成复杂表达式（三个操作数，带括号）
        
        Returns:
            str: 生成的表达式字符串
        """
        num1 = self.generate_number()
        num2 = self.generate_number()
        num3 = self.generate_number()
        
        op1 = self.generate_operator()
        op2 = self.generate_operator()
        
        # 随机选择括号位置
        patterns = [
            f"({num1} {op1} {num2}) {op2} {num3}",
            f"{num1} {op1} ({num2} {op2} {num3})",
            f"({num1} {op1} {num2} {op2} {num3})"
        ]
        
        return random.choice(patterns)
    
    def generate_expression(self) -> str:
        """
        生成表达式（简单或复杂）
        
        Returns:
            str: 生成的表达式字符串
        """
        # 70%概率生成简单表达式，30%概率生成复杂表达式
        if random.random() < 0.7:
            return self.generate_simple_expression()
        else:
            return self.generate_complex_expression()
    
    def validate_expression(self, expression: str) -> bool:
        """
        验证表达式是否符合规则
        
        Args:
            expression (str): 表达式字符串
            
        Returns:
            bool: 是否符合规则
        """
        try:
            # 解析并计算表达式
            result = self.parser.parse(expression)
            
            # 规则1：结果不能为负数
            if result.is_negative():
                return False
            
            # 规则2：结果不能为0
            if result.is_zero():
                return False
            
            # 规则3：结果必须是真分数或整数（不能是假分数）
            if result.is_improper_fraction():
                return False
            
            # 规则4：检查是否包含分数除法
            if self._contains_fraction_division(expression):
                return False
            
            return True
            
        except Exception:
            # 解析失败，不符合规则
            return False
    
    def _contains_fraction_division(self, expression: str) -> bool:
        """
        检查表达式是否包含分数除法
        
        Args:
            expression (str): 表达式字符串
            
        Returns:
            bool: 是否包含分数除法
        """
        # 简单的启发式检查：如果包含 "/" 且前后都是分数格式
        import re
        pattern = r'\d+/\d+\s*/\s*\d+/\d+'
        return bool(re.search(pattern, expression))
    
    def generate_valid_expression(self, max_attempts: int = 100) -> str:
        """
        生成符合规则的表达式
        
        Args:
            max_attempts (int): 最大尝试次数
            
        Returns:
            str: 符合规则的表达式
        """
        for _ in range(max_attempts):
            expression = self.generate_expression()
            if self.validate_expression(expression):
                return expression
        
        # 如果尝试次数用完，返回一个简单的有效表达式
        return f"{self.min_value} + {self.min_value}"
    
    def generate_problems(self, count: int) -> List[Tuple[str, str]]:
        """
        生成指定数量的题目
        
        Args:
            count (int): 题目数量
            
        Returns:
            List[Tuple[str, str]]: 题目列表，每个元素为(题目, 答案)
        """
        problems = []
        self.generated_problems.clear()
        self.deduplicator.reset()  # 重置去重器
        
        for i in range(count):
            # 生成唯一且有效的表达式
            expression = self.generate_unique_valid_expression()
            
            # 计算答案
            try:
                answer = self.parser.parse(expression)
                answer_str = answer.to_string()
            except Exception:
                # 如果计算失败，使用默认答案
                answer_str = "0"
            
            problems.append((expression, answer_str))
        
        return problems
    
    def generate_unique_valid_expression(self, max_attempts: int = 1000) -> str:
        """
        生成唯一且符合规则的表达式
        
        Args:
            max_attempts (int): 最大尝试次数
            
        Returns:
            str: 唯一且符合规则的表达式
        """
        for _ in range(max_attempts):
            expression = self.generate_valid_expression()
            
            # 使用规范化去重检查（支持交换律）
            if not self.deduplicator.is_duplicate(expression):
                self.generated_problems.add(expression)
                return expression
        
        # 如果无法生成唯一表达式，返回带序号的表达式
        counter = len(self.generated_problems) + 1
        return f"{self.min_value} + {self.min_value + counter}"
    
    def format_problem(self, problem_num: int, expression: str) -> str:
        """
        格式化题目
        
        Args:
            problem_num (int): 题目编号
            expression (str): 表达式
            
        Returns:
            str: 格式化后的题目
        """
        return f"{problem_num}. {expression} ="
    
    def format_answer(self, problem_num: int, answer: str) -> str:
        """
        格式化答案
        
        Args:
            problem_num (int): 题目编号
            answer (str): 答案
            
        Returns:
            str: 格式化后的答案
        """
        return f"{problem_num}. {answer}"


class ProblemValidator:
    """题目验证器"""
    
    def __init__(self):
        self.parser = ExpressionParser()
    
    def validate_problem(self, expression: str) -> Tuple[bool, str]:
        """
        验证单个题目
        
        Args:
            expression (str): 表达式
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            result = self.parser.parse(expression)
            
            # 检查结果是否为负数
            if result.is_negative():
                return False, "结果不能为负数"
            
            # 检查结果是否为0
            if result.is_zero():
                return False, "结果不能为0"
            
            # 检查结果是否为假分数
            if result.is_improper_fraction():
                return False, "结果不能为假分数"
            
            return True, ""
            
        except Exception as e:
            return False, f"表达式解析错误: {e}"
    
    def validate_problems(self, problems: List[Tuple[str, str]]) -> List[Tuple[bool, str]]:
        """
        验证题目列表
        
        Args:
            problems (List[Tuple[str, str]]): 题目列表
            
        Returns:
            List[Tuple[bool, str]]: 验证结果列表
        """
        results = []
        for expression, _ in problems:
            is_valid, error_msg = self.validate_problem(expression)
            results.append((is_valid, error_msg))
        return results


# 便捷函数
def generate_problems(count: int, min_value: int = 1, max_value: int = 10) -> List[Tuple[str, str]]:
    """
    生成题目的便捷函数
    
    Args:
        count (int): 题目数量
        min_value (int): 最小数值
        max_value (int): 最大数值
        
    Returns:
        List[Tuple[str, str]]: 题目列表
    """
    generator = ProblemGenerator(min_value, max_value)
    return generator.generate_problems(count)


# 测试代码
if __name__ == "__main__":
    # 创建题目生成器
    generator = ProblemGenerator(min_value=1, max_value=10)
    
    print("=== 题目生成器测试 ===")
    
    # 生成5个题目
    problems = generator.generate_problems(5)
    
    print("\n生成的题目:")
    for i, (expression, answer) in enumerate(problems, 1):
        print(f"{i}. {expression} = {answer}")
    
    # 验证题目
    validator = ProblemValidator()
    print("\n题目验证:")
    for i, (expression, answer) in enumerate(problems, 1):
        is_valid, error_msg = validator.validate_problem(expression)
        status = "OK" if is_valid else "ERROR"
        print(f"{i}. {status} {expression} = {answer}")
        if not is_valid:
            print(f"   错误: {error_msg}")
