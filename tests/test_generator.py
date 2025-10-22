"""
题目生成器测试模块

测试题目生成器的各种功能和去重算法
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from problem_generator import ProblemGenerator, ProblemValidator, generate_problems
from deduplicator import Deduplicator, AdvancedDeduplicator, DeduplicationStats, deduplicate_problems
from rational import Rational


class TestProblemGenerator(unittest.TestCase):
    """题目生成器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.generator = ProblemGenerator(min_value=1, max_value=10)
        self.validator = ProblemValidator()
    
    def test_initialization(self):
        """测试初始化"""
        generator = ProblemGenerator(min_value=2, max_value=20)
        self.assertEqual(generator.min_value, 2)
        self.assertEqual(generator.max_value, 20)
        self.assertEqual(len(generator.generated_problems), 0)
    
    def test_generate_number(self):
        """测试数字生成"""
        # 测试多次生成，确保在范围内
        for _ in range(100):
            number = self.generator.generate_number()
            self.assertIsInstance(number, Rational)
            self.assertTrue(number.is_positive())
    
    def test_generate_operator(self):
        """测试运算符生成"""
        operators = set()
        for _ in range(100):
            op = self.generator.generate_operator()
            self.assertIn(op, ['+', '-', '*', '/'])
            operators.add(op)
        
        # 确保所有运算符都可能被生成
        self.assertEqual(operators, {'+', '-', '*', '/'})
    
    def test_generate_simple_expression(self):
        """测试简单表达式生成"""
        expression = self.generator.generate_simple_expression()
        self.assertIsInstance(expression, str)
        self.assertIn(' ', expression)  # 应该包含空格
        
        # 检查是否包含运算符
        has_operator = any(op in expression for op in ['+', '-', '*', '/'])
        self.assertTrue(has_operator)
    
    def test_generate_complex_expression(self):
        """测试复杂表达式生成"""
        expression = self.generator.generate_complex_expression()
        self.assertIsInstance(expression, str)
        self.assertIn('(', expression)  # 应该包含括号
        self.assertIn(')', expression)
    
    def test_validate_expression_positive(self):
        """测试表达式验证（正例）"""
        valid_expressions = [
            "1 + 2",
            "3 * 4",
            "1/2 + 1/3",
            "(1 + 2) * 3",
            "5 - 2",
            "6 / 2"
        ]
        
        for expr in valid_expressions:
            with self.subTest(expression=expr):
                is_valid = self.generator.validate_expression(expr)
                self.assertTrue(is_valid, f"表达式 {expr} 应该有效")
    
    def test_validate_expression_negative(self):
        """测试表达式验证（负例）"""
        invalid_expressions = [
            "1 - 5",  # 负数结果
            "0 * 5",  # 零结果
            "5 / 0",  # 除零
            "1/2 / 1/3",  # 分数除法
            "invalid",  # 无效表达式
        ]
        
        for expr in invalid_expressions:
            with self.subTest(expression=expr):
                is_valid = self.generator.validate_expression(expr)
                self.assertFalse(is_valid, f"表达式 {expr} 应该无效")
    
    def test_generate_valid_expression(self):
        """测试生成有效表达式"""
        expression = self.generator.generate_valid_expression()
        self.assertIsInstance(expression, str)
        self.assertTrue(self.generator.validate_expression(expression))
    
    def test_generate_problems(self):
        """测试生成题目列表"""
        count = 5
        problems = self.generator.generate_problems(count)
        
        self.assertEqual(len(problems), count)
        
        for i, (expression, answer) in enumerate(problems):
            with self.subTest(problem=i):
                self.assertIsInstance(expression, str)
                self.assertIsInstance(answer, str)
                self.assertTrue(self.generator.validate_expression(expression))
    
    def test_generate_unique_problems(self):
        """测试生成唯一题目"""
        count = 10
        problems = self.generator.generate_problems(count)
        
        # 检查表达式是否唯一
        expressions = [expr for expr, _ in problems]
        unique_expressions = set(expressions)
        self.assertEqual(len(unique_expressions), len(expressions))
    
    def test_format_problem(self):
        """测试题目格式化"""
        formatted = self.generator.format_problem(1, "1 + 2")
        self.assertEqual(formatted, "1. 1 + 2 =")
    
    def test_format_answer(self):
        """测试答案格式化"""
        formatted = self.generator.format_answer(1, "3")
        self.assertEqual(formatted, "1. 3")


class TestProblemValidator(unittest.TestCase):
    """题目验证器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.validator = ProblemValidator()
    
    def test_validate_problem_valid(self):
        """测试有效题目验证"""
        valid_expressions = [
            "1 + 2",
            "3 * 4",
            "1/2 + 1/3",
            "(1 + 2) * 3"
        ]
        
        for expr in valid_expressions:
            with self.subTest(expression=expr):
                is_valid, error_msg = self.validator.validate_problem(expr)
                self.assertTrue(is_valid)
                self.assertEqual(error_msg, "")
    
    def test_validate_problem_invalid(self):
        """测试无效题目验证"""
        invalid_cases = [
            ("1 - 5", "结果不能为负数"),
            ("0 * 5", "结果不能为0"),
            ("5 / 0", "表达式解析错误"),
            ("invalid", "表达式解析错误")
        ]
        
        for expr, expected_error in invalid_cases:
            with self.subTest(expression=expr):
                is_valid, error_msg = self.validator.validate_problem(expr)
                self.assertFalse(is_valid)
                self.assertIn(expected_error.split(":")[0], error_msg)
    
    def test_validate_problems(self):
        """测试题目列表验证"""
        problems = [
            ("1 + 2", "3"),
            ("1 - 5", "-4"),
            ("3 * 4", "12")
        ]
        
        results = self.validator.validate_problems(problems)
        self.assertEqual(len(results), 3)
        
        # 第一个和第三个应该有效，第二个无效
        self.assertTrue(results[0][0])
        self.assertFalse(results[1][0])
        self.assertTrue(results[2][0])


class TestDeduplicator(unittest.TestCase):
    """去重器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.deduplicator = Deduplicator()
    
    def test_normalize_expression(self):
        """测试表达式标准化"""
        test_cases = [
            ("1 + 2", "1+2"),
            (" 1 + 2 ", "1+2"),
            ("1+2", "1+2")
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = self.deduplicator.normalize_expression(original)
                self.assertEqual(result, expected)
    
    def test_calculate_expression_hash(self):
        """测试表达式哈希计算"""
        hash1 = self.deduplicator.calculate_expression_hash("1 + 2")
        hash2 = self.deduplicator.calculate_expression_hash("1+2")
        hash3 = self.deduplicator.calculate_expression_hash("2 + 1")
        
        # 相同表达式应该产生相同哈希
        self.assertEqual(hash1, hash2)
        # 不同表达式应该产生不同哈希
        self.assertNotEqual(hash1, hash3)
    
    def test_is_duplicate_by_expression(self):
        """测试表达式去重"""
        # 第一次检查应该不重复
        self.assertFalse(self.deduplicator.is_duplicate_by_expression("1 + 2"))
        
        # 相同表达式应该重复
        self.assertTrue(self.deduplicator.is_duplicate_by_expression("1 + 2"))
        self.assertTrue(self.deduplicator.is_duplicate_by_expression("1+2"))
        
        # 不同表达式应该不重复
        self.assertFalse(self.deduplicator.is_duplicate_by_expression("2 + 1"))
    
    def test_is_duplicate_by_result(self):
        """测试结果去重"""
        # 第一次检查应该不重复
        self.assertFalse(self.deduplicator.is_duplicate_by_result("1 + 2"))
        
        # 相同结果的表达式应该重复
        self.assertTrue(self.deduplicator.is_duplicate_by_result("2 + 1"))
        self.assertTrue(self.deduplicator.is_duplicate_by_result("3 + 0"))
        
        # 不同结果的表达式应该不重复
        self.assertFalse(self.deduplicator.is_duplicate_by_result("1 + 3"))
    
    def test_is_duplicate_by_hash(self):
        """测试哈希去重"""
        # 第一次检查应该不重复
        self.assertFalse(self.deduplicator.is_duplicate_by_hash("1 + 2"))
        
        # 相同哈希的表达式应该重复
        self.assertTrue(self.deduplicator.is_duplicate_by_hash("1 + 2"))
        self.assertTrue(self.deduplicator.is_duplicate_by_hash("1+2"))
        
        # 不同哈希的表达式应该不重复
        self.assertFalse(self.deduplicator.is_duplicate_by_hash("2 + 1"))
    
    def test_deduplicate_problems(self):
        """测试题目去重"""
        problems = [
            ("1 + 2", "3"),
            ("2 + 1", "3"),  # 结果相同
            ("1 + 2", "3"),  # 完全相同
            ("3 * 4", "12"),
            ("4 * 3", "12")  # 结果相同
        ]
        
        # 使用表达式去重
        unique_by_expr = self.deduplicator.deduplicate_problems(problems, "expression")
        self.assertEqual(len(unique_by_expr), 4)  # 应该去重1个（"1 + 2"重复）
        
        # 使用结果去重
        self.deduplicator.reset()
        unique_by_result = self.deduplicator.deduplicate_problems(problems, "result")
        self.assertEqual(len(unique_by_result), 2)  # 应该去重3个
    
    def test_reset(self):
        """测试重置功能"""
        # 添加一些重复项
        self.deduplicator.is_duplicate_by_expression("1 + 2")
        self.deduplicator.is_duplicate_by_expression("2 + 1")
        
        # 重置
        self.deduplicator.reset()
        
        # 重置后应该不重复
        self.assertFalse(self.deduplicator.is_duplicate_by_expression("1 + 2"))
        self.assertFalse(self.deduplicator.is_duplicate_by_expression("2 + 1"))
    
    def test_get_statistics(self):
        """测试统计信息"""
        # 添加一些表达式
        self.deduplicator.is_duplicate_by_expression("1 + 2")
        self.deduplicator.is_duplicate_by_expression("2 + 1")
        
        stats = self.deduplicator.get_statistics()
        self.assertIn("unique_expressions", stats)
        self.assertIn("unique_results", stats)
        self.assertIn("unique_hashes", stats)


class TestAdvancedDeduplicator(unittest.TestCase):
    """高级去重器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.advanced_deduplicator = AdvancedDeduplicator()
    
    def test_is_semantically_equivalent(self):
        """测试语义等价检查"""
        # 相同结果的表达式应该语义等价
        self.assertTrue(self.advanced_deduplicator.is_semantically_equivalent("1 + 2", "2 + 1"))
        self.assertTrue(self.advanced_deduplicator.is_semantically_equivalent("3 * 4", "4 * 3"))
        
        # 不同结果的表达式应该不等价
        self.assertFalse(self.advanced_deduplicator.is_semantically_equivalent("1 + 2", "1 + 3"))
    
    def test_is_duplicate_semantic(self):
        """测试语义去重"""
        # 第一次检查应该不重复
        self.assertFalse(self.advanced_deduplicator.is_duplicate_semantic("1 + 2"))
        
        # 语义等价的表达式应该重复
        self.assertTrue(self.advanced_deduplicator.is_duplicate_semantic("2 + 1"))
        self.assertTrue(self.advanced_deduplicator.is_duplicate_semantic("1 + 2"))
        
        # 不等价的表达式应该不重复
        self.assertFalse(self.advanced_deduplicator.is_duplicate_semantic("1 + 3"))


class TestDeduplicationStats(unittest.TestCase):
    """去重统计测试"""
    
    def setUp(self):
        """测试前准备"""
        self.stats = DeduplicationStats()
    
    def test_add_generation(self):
        """测试添加生成记录"""
        # 添加一些记录
        self.stats.add_generation(False)  # 非重复
        self.stats.add_generation(True)   # 重复
        self.stats.add_generation(False)  # 非重复
        
        stats = self.stats.get_stats()
        self.assertEqual(stats["total_generated"], 3)
        self.assertEqual(stats["duplicates_found"], 1)
        self.assertEqual(stats["unique_problems"], 2)
        self.assertAlmostEqual(stats["duplication_rate"], 1/3, places=2)
    
    def test_reset(self):
        """测试重置统计"""
        # 添加一些记录
        self.stats.add_generation(False)
        self.stats.add_generation(True)
        
        # 重置
        self.stats.reset()
        
        stats = self.stats.get_stats()
        self.assertEqual(stats["total_generated"], 0)
        self.assertEqual(stats["duplicates_found"], 0)
        self.assertEqual(stats["unique_problems"], 0)
        self.assertEqual(stats["duplication_rate"], 0.0)


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""
    
    def test_generate_problems_function(self):
        """测试生成题目便捷函数"""
        problems = generate_problems(3, min_value=1, max_value=5)
        
        self.assertEqual(len(problems), 3)
        for expression, answer in problems:
            self.assertIsInstance(expression, str)
            self.assertIsInstance(answer, str)
    
    def test_deduplicate_problems_function(self):
        """测试去重便捷函数"""
        problems = [
            ("1 + 2", "3"),
            ("2 + 1", "3"),
            ("3 * 4", "12")
        ]
        
        unique_problems = deduplicate_problems(problems, "expression")
        self.assertEqual(len(unique_problems), 3)  # 没有重复，保持原数量


class TestGeneratorIntegration(unittest.TestCase):
    """生成器集成测试"""
    
    def test_full_generation_workflow(self):
        """测试完整生成工作流"""
        # 创建生成器
        generator = ProblemGenerator(min_value=1, max_value=10)
        
        # 生成题目
        problems = generator.generate_problems(5)
        
        # 验证题目
        validator = ProblemValidator()
        validation_results = validator.validate_problems(problems)
        
        # 所有题目都应该有效
        for is_valid, error_msg in validation_results:
            self.assertTrue(is_valid, f"题目验证失败: {error_msg}")
        
        # 去重
        deduplicator = Deduplicator()
        unique_problems = deduplicator.deduplicate_problems(problems, "expression")
        
        # 去重后应该保持或减少题目数量
        self.assertLessEqual(len(unique_problems), len(problems))
        
        # 格式化输出
        formatted_problems = []
        for i, (expression, answer) in enumerate(unique_problems, 1):
            problem_str = generator.format_problem(i, expression)
            answer_str = generator.format_answer(i, answer)
            formatted_problems.append((problem_str, answer_str))
        
        self.assertEqual(len(formatted_problems), len(unique_problems))


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
