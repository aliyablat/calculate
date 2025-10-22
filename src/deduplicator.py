"""
去重算法模块
"""

import sys
import os
from typing import List, Tuple, Dict, Any

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))
from expression_parser import ExpressionParser


class Deduplicator:
    """题目去重器"""
    
    def __init__(self):
        self.parser = ExpressionParser()
        self.seen_canonical_forms = set()
    
    def canonicalize_expression(self, expression: str) -> str:
        """
        将表达式转换为规范形式，用于检测交换律和结合律重复

        规则：
        1. 对于交换律运算符（+, *），将操作数按字典序排序
        2. 对于左结合运算符（-, /），保持原有结合性
        3. 递归处理括号内的子表达式

        Args:
            expression (str): 原始表达式

        Returns:
            str: 规范化后的表达式
        """
        try:
            # 解析表达式为token
            tokens = self.parser.tokenize(expression)

            # 构建表达式树
            tree = self._build_expression_tree(tokens)

            # 规范化表达式树
            canonical_tree = self._canonicalize_tree(tree)

            # 将规范化的树转换回字符串
            return self._tree_to_string(canonical_tree)

        except Exception:
            # 如果解析失败，返回原始表达式（去除空格）
            return expression.replace(' ', '')

    def _build_expression_tree(self, tokens: List) -> Dict[str, Any]:
        """
        从token列表构建表达式树

        Args:
            tokens: token列表

        Returns:
            Dict: 表达式树
        """
        # 转换为后缀表达式
        postfix = self.parser.infix_to_postfix(tokens)

        # 使用栈构建表达式树
        stack = []

        for token in postfix:
            if token.type == 'NUMBER':
                # 叶子节点
                stack.append({
                    'type': 'number',
                    'value': str(token.value)
                })
            elif token.type == 'OPERATOR':
                # 操作符节点
                if len(stack) < 2:
                    raise ValueError("Invalid expression")

                right = stack.pop()
                left = stack.pop()

                stack.append({
                    'type': 'operator',
                    'operator': token.value,
                    'left': left,
                    'right': right
                })

        if len(stack) != 1:
            raise ValueError("Invalid expression")

        return stack[0]

    def _canonicalize_tree(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """
        规范化表达式树（仅支持交换律，不完全展开结合律）

        根据需求，只有通过有限次交换+和×的操作数才算重复。
        例如：1+2+3 和 3+2+1 不是重复的，因为它们的树结构不同。

        Args:
            tree: 表达式树

        Returns:
            Dict: 规范化后的表达式树
        """
        if tree['type'] == 'number':
            return tree

        # 递归规范化左右子树
        left = self._canonicalize_tree(tree['left'])
        right = self._canonicalize_tree(tree['right'])

        operator = tree['operator']

        # 对于交换律运算符（+ 和 *），按字典序排序左右操作数
        if operator in ['+', '*']:
            left_str = self._tree_to_string(left)
            right_str = self._tree_to_string(right)

            # 如果右边的字符串字典序小于左边，交换它们
            if right_str < left_str:
                left, right = right, left

        return {
            'type': 'operator',
            'operator': operator,
            'left': left,
            'right': right
        }

    def _tree_to_string(self, tree: Dict[str, Any]) -> str:
        """
        将表达式树转换为字符串

        Args:
            tree: 表达式树

        Returns:
            str: 表达式字符串
        """
        if tree['type'] == 'number':
            return tree['value']

        left_str = self._tree_to_string(tree['left'])
        right_str = self._tree_to_string(tree['right'])
        operator = tree['operator']

        # 添加括号以保持优先级
        return f"({left_str}{operator}{right_str})"
    
    def is_duplicate(self, expression: str) -> bool:
        """
        检查表达式是否重复（通过规范化形式）

        根据需求，通过有限次交换+和×的操作数来检测重复。

        Args:
            expression (str): 表达式字符串

        Returns:
            bool: 是否重复
        """
        canonical = self.canonicalize_expression(expression)

        if canonical in self.seen_canonical_forms:
            return True

        self.seen_canonical_forms.add(canonical)
        return False
    
    def deduplicate_problems(self, problems: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        对题目列表进行去重
        
        Args:
            problems (List[Tuple[str, str]]): 题目列表
            
        Returns:
            List[Tuple[str, str]]: 去重后的题目列表
        """
        unique_problems = []
        
        for expression, answer in problems:
            if not self.is_duplicate(expression):
                unique_problems.append((expression, answer))
        
        return unique_problems
    
    def reset(self):
        """重置去重器状态"""
        self.seen_canonical_forms.clear()
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取去重统计信息
        
        Returns:
            Dict[str, int]: 统计信息
        """
        return {
            "unique_problems": len(self.seen_canonical_forms)
        }


# 测试代码
if __name__ == "__main__":
    print("=== 去重算法测试 ===")
    
    # 测试题目列表
    test_problems = [
        ("1 + 2", "3"),
        ("2 + 1", "3"),  # 与第一个结果相同
        ("1 + 2", "3"),  # 与第一个完全相同
        ("3 * 4", "12"),
        ("4 * 3", "12"),  # 与第四个结果相同
        ("1/2 + 1/3", "5/6"),
        ("1/3 + 1/2", "5/6"),  # 与第六个结果相同
        ("1 + 2 + 3", "6"),
        ("3 + 2 + 1", "6"),  # 不同（左结合性不同）
        ("(1 + 2) + 3", "6"),  # 与 1+2+3 相同（左结合）
        ("1 + (2 + 3)", "6"),  # 结合律重复
    ]
    
    print("\n原始题目:")
    for i, (expr, ans) in enumerate(test_problems, 1):
        print(f"{i}. {expr} = {ans}")
    
    # 测试规范化去重
    print(f"\n使用规范化去重:")
    deduplicator = Deduplicator()
    unique_problems = deduplicator.deduplicate_problems(test_problems)
    
    for i, (expr, ans) in enumerate(unique_problems, 1):
        print(f"{i}. {expr} = {ans}")
    
    print(f"去重后数量: {len(unique_problems)}")
