"""
主程序测试模块

测试命令行接口和文件处理功能
"""

import unittest
import sys
import os
import tempfile
import subprocess
from unittest.mock import patch, mock_open

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from file_utils import FileHandler, FileValidator, write_problems_to_files, grade_problems_from_files


class TestFileHandler(unittest.TestCase):
    """文件处理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.handler = FileHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_write_exercises(self):
        """测试写入题目文件"""
        problems = [
            ("1 + 2", "3"),
            ("3 * 4", "12"),
            ("1/2 + 1/3", "5/6")
        ]
        
        filename = os.path.join(self.temp_dir, "test_exercises.txt")
        self.handler.write_exercises(problems, filename)
        
        # 验证文件内容
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("1. 1 + 2 =", content)
        self.assertIn("2. 3 * 4 =", content)
        self.assertIn("3. 1/2 + 1/3 =", content)
    
    def test_write_answers(self):
        """测试写入答案文件"""
        problems = [
            ("1 + 2", "3"),
            ("3 * 4", "12"),
            ("1/2 + 1/3", "5/6")
        ]
        
        filename = os.path.join(self.temp_dir, "test_answers.txt")
        self.handler.write_answers(problems, filename)
        
        # 验证文件内容
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("1. 3", content)
        self.assertIn("2. 12", content)
        self.assertIn("3. 5/6", content)
    
    def test_read_exercises(self):
        """测试读取题目文件"""
        # 创建测试文件
        filename = os.path.join(self.temp_dir, "test_exercises.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("1. 1 + 2 =\n")
            f.write("2. 3 * 4 =\n")
            f.write("3. 1/2 + 1/3 =\n")
        
        exercises = self.handler.read_exercises(filename)
        
        self.assertEqual(len(exercises), 3)
        self.assertEqual(exercises[0], "1 + 2")
        self.assertEqual(exercises[1], "3 * 4")
        self.assertEqual(exercises[2], "1/2 + 1/3")
    
    def test_read_answers(self):
        """测试读取答案文件"""
        # 创建测试文件
        filename = os.path.join(self.temp_dir, "test_answers.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("1. 3\n")
            f.write("2. 12\n")
            f.write("3. 5/6\n")
        
        answers = self.handler.read_answers(filename)
        
        self.assertEqual(len(answers), 3)
        self.assertEqual(answers[0], "3")
        self.assertEqual(answers[1], "12")
        self.assertEqual(answers[2], "5/6")
    
    def test_grade_exercises(self):
        """测试批改题目"""
        exercises = ["1 + 2", "3 * 4", "1/2 + 1/3"]
        answers = ["3", "12", "5/6"]
        
        results = self.handler.grade_exercises(exercises, answers)
        
        self.assertEqual(len(results), 3)
        # 所有题目都应该正确
        for is_correct, error_msg in results:
            self.assertTrue(is_correct)
            self.assertEqual(error_msg, "")
    
    def test_grade_exercises_wrong_answers(self):
        """测试批改错误答案"""
        exercises = ["1 + 2", "3 * 4"]
        answers = ["4", "11"]  # 错误答案
        
        results = self.handler.grade_exercises(exercises, answers)
        
        self.assertEqual(len(results), 2)
        # 所有题目都应该错误
        for is_correct, error_msg in results:
            self.assertFalse(is_correct)
            self.assertIn("正确答案", error_msg)
    
    def test_write_grade_results(self):
        """测试写入批改结果"""
        results = [
            (True, ""),
            (False, "正确答案: 12, 学生答案: 11"),
            (True, "")
        ]
        
        filename = os.path.join(self.temp_dir, "test_grade.txt")
        self.handler.write_grade_results(results, filename)
        
        # 验证文件内容
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("Correct: 2 (2)", content)
        self.assertIn("Wrong: 1 (1)", content)
        self.assertIn("1. Correct", content)
        self.assertIn("2. Wrong. 正确答案: 12, 学生答案: 11", content)
        self.assertIn("3. Correct", content)
    
    def test_compare_answers(self):
        """测试答案比较"""
        # 相同答案
        self.assertTrue(self.handler._compare_answers("3", "3"))
        self.assertTrue(self.handler._compare_answers("1/2", "1/2"))
        self.assertTrue(self.handler._compare_answers("1'1/2", "1'1/2"))
        
        # 不同答案
        self.assertFalse(self.handler._compare_answers("3", "4"))
        self.assertFalse(self.handler._compare_answers("1/2", "1/3"))
    
    def test_normalize_answer(self):
        """测试答案标准化"""
        # 整数
        self.assertEqual(self.handler._normalize_answer("3"), "3")
        self.assertEqual(self.handler._normalize_answer(" 3 "), "3")
        
        # 分数
        self.assertEqual(self.handler._normalize_answer("1/2"), "1/2")
        self.assertEqual(self.handler._normalize_answer(" 1/2 "), "1/2")
        
        # 带分数
        self.assertEqual(self.handler._normalize_answer("1'1/2"), "1'1/2")


class TestFileValidator(unittest.TestCase):
    """文件验证器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.validator = FileValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_exercise_file_valid(self):
        """测试有效题目文件验证"""
        # 创建有效题目文件
        filename = os.path.join(self.temp_dir, "valid_exercises.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("1. 1 + 2 =\n")
            f.write("2. 3 * 4 =\n")
        
        is_valid, error_msg = self.validator.validate_exercise_file(filename)
        
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_validate_exercise_file_invalid(self):
        """测试无效题目文件验证"""
        # 测试不存在的文件
        is_valid, error_msg = self.validator.validate_exercise_file("nonexistent.txt")
        self.assertFalse(is_valid)
        self.assertIn("文件不存在", error_msg)
        
        # 测试空文件
        filename = os.path.join(self.temp_dir, "empty.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            pass
        
        is_valid, error_msg = self.validator.validate_exercise_file(filename)
        self.assertFalse(is_valid)
        self.assertIn("文件为空", error_msg)
    
    def test_validate_answer_file_valid(self):
        """测试有效答案文件验证"""
        # 创建有效答案文件
        filename = os.path.join(self.temp_dir, "valid_answers.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("1. 3\n")
            f.write("2. 12\n")
        
        is_valid, error_msg = self.validator.validate_answer_file(filename)
        
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_validate_answer_file_invalid(self):
        """测试无效答案文件验证"""
        # 测试不存在的文件
        is_valid, error_msg = self.validator.validate_answer_file("nonexistent.txt")
        self.assertFalse(is_valid)
        self.assertIn("文件不存在", error_msg)


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_write_problems_to_files(self):
        """测试便捷写入函数"""
        problems = [
            ("1 + 2", "3"),
            ("3 * 4", "12")
        ]
        
        exercise_file = os.path.join(self.temp_dir, "test_exercises.txt")
        answer_file = os.path.join(self.temp_dir, "test_answers.txt")
        
        write_problems_to_files(problems, exercise_file, answer_file)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(exercise_file))
        self.assertTrue(os.path.exists(answer_file))
    
    def test_grade_problems_from_files(self):
        """测试便捷批改函数"""
        # 创建测试文件
        exercise_file = os.path.join(self.temp_dir, "test_exercises.txt")
        answer_file = os.path.join(self.temp_dir, "test_answers.txt")
        grade_file = os.path.join(self.temp_dir, "test_grade.txt")
        
        with open(exercise_file, 'w', encoding='utf-8') as f:
            f.write("1. 1 + 2 =\n")
            f.write("2. 3 * 4 =\n")
        
        with open(answer_file, 'w', encoding='utf-8') as f:
            f.write("1. 3\n")
            f.write("2. 12\n")
        
        # 执行批改
        stats = grade_problems_from_files(exercise_file, answer_file, grade_file)
        
        # 验证结果
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["correct"], 2)
        self.assertEqual(stats["wrong"], 0)
        self.assertEqual(stats["accuracy"], 1.0)
        
        # 验证批改文件存在
        self.assertTrue(os.path.exists(grade_file))


class TestMainProgram(unittest.TestCase):
    """主程序测试"""
    
    def test_argument_parsing_generate_mode(self):
        """测试生成模式参数解析"""
        # 测试有效参数
        with patch('sys.argv', ['main.py', '-n', '10', '-r', '10']):
            from main import parse_arguments
            args = parse_arguments()
            self.assertEqual(args.number, 10)
            self.assertEqual(args.range, 10)
            self.assertIsNone(args.exercise)
            self.assertIsNone(args.answer)
    
    def test_argument_parsing_grade_mode(self):
        """测试批改模式参数解析"""
        # 测试有效参数
        with patch('sys.argv', ['main.py', '-e', 'test.txt', '-a', 'ans.txt']):
            with patch('os.path.exists', return_value=True):
                from main import parse_arguments
                args = parse_arguments()
                self.assertEqual(args.exercise, 'test.txt')
                self.assertEqual(args.answer, 'ans.txt')
                self.assertIsNone(args.number)
                self.assertIsNone(args.range)
    
    def test_argument_validation_missing_params(self):
        """测试参数验证 - 缺少参数"""
        with patch('sys.argv', ['main.py']):
            with patch('sys.exit') as mock_exit:
                from main import parse_arguments
                try:
                    parse_arguments()
                except SystemExit:
                    pass
                mock_exit.assert_called()
    
    def test_argument_validation_invalid_number(self):
        """测试参数验证 - 无效题目数量"""
        with patch('sys.argv', ['main.py', '-n', '10001', '-r', '10']):
            with patch('sys.exit') as mock_exit:
                from main import parse_arguments
                try:
                    parse_arguments()
                except SystemExit:
                    pass
                mock_exit.assert_called()
    
    def test_argument_validation_invalid_range(self):
        """测试参数验证 - 无效数值范围"""
        with patch('sys.argv', ['main.py', '-n', '10', '-r', '101']):
            with patch('sys.exit') as mock_exit:
                from main import parse_arguments
                try:
                    parse_arguments()
                except SystemExit:
                    pass
                mock_exit.assert_called()


class TestMainIntegration(unittest.TestCase):
    """主程序集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_mode_integration(self):
        """测试生成模式集成"""
        # 模拟命令行参数
        with patch('sys.argv', ['main.py', '-n', '3', '-r', '5']):
            with patch('main.generate_problems_mode') as mock_generate:
                from main import main
                main()
                mock_generate.assert_called_once_with(3, 5)
    
    def test_grade_mode_integration(self):
        """测试批改模式集成"""
        # 创建测试文件
        exercise_file = os.path.join(self.temp_dir, "test_exercises.txt")
        answer_file = os.path.join(self.temp_dir, "test_answers.txt")
        
        with open(exercise_file, 'w', encoding='utf-8') as f:
            f.write("1. 1 + 2 =\n")
        
        with open(answer_file, 'w', encoding='utf-8') as f:
            f.write("1. 3\n")
        
        # 模拟命令行参数
        with patch('sys.argv', ['main.py', '-e', exercise_file, '-a', answer_file]):
            with patch('main.grade_problems_mode') as mock_grade:
                from main import main
                main()
                mock_grade.assert_called_once_with(exercise_file, answer_file)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
