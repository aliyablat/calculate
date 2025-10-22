"""
文件处理工具模块

处理题目文件、答案文件和批改结果的读写
"""

import os
import re
import sys
from typing import List, Tuple, Dict, Any

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))
from expression_parser import ExpressionParser
from rational import Rational


class FileHandler:
    """文件处理器"""
    
    def __init__(self):
        self.parser = ExpressionParser()
    
    def write_exercises(self, problems: List[Tuple[str, str]], filename: str):
        """
        写入题目文件
        
        Args:
            problems (List[Tuple[str, str]]): 题目列表，每个元素为(表达式, 答案)
            filename (str): 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for i, (expression, _) in enumerate(problems, 1):
                    f.write(f"{i}. {expression} =\n")
            print(f"题目文件已写入: {filename}")
        except Exception as e:
            raise Exception(f"写入题目文件失败: {e}")
    
    def write_answers(self, problems: List[Tuple[str, str]], filename: str):
        """
        写入答案文件
        
        Args:
            problems (List[Tuple[str, str]]): 题目列表，每个元素为(表达式, 答案)
            filename (str): 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for i, (_, answer) in enumerate(problems, 1):
                    f.write(f"{i}. {answer}\n")
            print(f"答案文件已写入: {filename}")
        except Exception as e:
            raise Exception(f"写入答案文件失败: {e}")
    
    def read_exercises(self, filename: str) -> List[str]:
        """
        读取题目文件
        
        Args:
            filename (str): 题目文件名
            
        Returns:
            List[str]: 题目表达式列表
        """
        exercises = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # 解析题目格式: "1. 1 + 2 = ?" 或 "1. 1 + 2 ="
                        match = re.match(r'^\d+\.\s*(.+)\s*=\s*\??$', line)
                        if match:
                            expression = match.group(1).strip()
                            exercises.append(expression)
                        else:
                            print(f"警告: 跳过无效题目格式: {line}")
        except Exception as e:
            raise Exception(f"读取题目文件失败: {e}")
        
        return exercises
    
    def read_answers(self, filename: str) -> List[str]:
        """
        读取答案文件
        
        Args:
            filename (str): 答案文件名
            
        Returns:
            List[str]: 答案列表
        """
        answers = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # 解析答案格式: "1. 3"
                        match = re.match(r'^\d+\.\s*(.+)$', line)
                        if match:
                            answer = match.group(1).strip()
                            answers.append(answer)
                        else:
                            print(f"警告: 跳过无效答案格式: {line}")
        except Exception as e:
            raise Exception(f"读取答案文件失败: {e}")
        
        return answers
    
    def grade_exercises(self, exercises: List[str], answers: List[str]) -> List[Tuple[bool, str]]:
        """
        批改题目
        
        Args:
            exercises (List[str]): 题目表达式列表
            answers (List[str]): 答案列表
            
        Returns:
            List[Tuple[bool, str]]: 批改结果列表，每个元素为(是否正确, 错误信息)
        """
        results = []
        
        for i, (exercise, answer) in enumerate(zip(exercises, answers)):
            try:
                # 计算正确答案
                correct_answer = self.parser.parse(exercise)
                correct_answer_str = correct_answer.to_string()
                
                # 比较答案
                is_correct = self._compare_answers(correct_answer_str, answer)
                
                if is_correct:
                    results.append((True, ""))
                else:
                    error_msg = f"正确答案: {correct_answer_str}, 学生答案: {answer}"
                    results.append((False, error_msg))
                    
            except Exception as e:
                error_msg = f"题目解析错误: {e}"
                results.append((False, error_msg))
        
        return results
    
    def _compare_answers(self, correct_answer: str, student_answer: str) -> bool:
        """
        比较答案是否正确
        
        Args:
            correct_answer (str): 正确答案
            student_answer (str): 学生答案
            
        Returns:
            bool: 是否正确
        """
        # 标准化答案格式
        correct_normalized = self._normalize_answer(correct_answer)
        student_normalized = self._normalize_answer(student_answer)
        
        return correct_normalized == student_normalized
    
    def _normalize_answer(self, answer: str) -> str:
        """
        标准化答案格式
        
        Args:
            answer (str): 原始答案
            
        Returns:
            str: 标准化后的答案
        """
        # 移除空格
        normalized = answer.replace(' ', '')
        
        # 统一分数格式
        # 将带分数转换为假分数进行比较
        try:
            if "'" in normalized:
                # 处理带分数格式
                rational = Rational.from_string(normalized)
                return rational.to_string()
            else:
                # 处理普通分数或整数
                if '/' in normalized:
                    rational = Rational.from_string(normalized)
                    return rational.to_string()
                else:
                    # 整数
                    return str(int(normalized))
        except Exception:
            # 如果解析失败，返回原始答案
            return normalized
    
    def write_grade_results(self, results: List[Tuple[bool, str]], filename: str):
        """
        写入批改结果文件
        
        Args:
            results (List[Tuple[bool, str]]): 批改结果列表
            filename (str): 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # 统计信息
                correct_count = sum(1 for is_correct, _ in results if is_correct)
                total_count = len(results)
                wrong_count = total_count - correct_count
                
                # 收集正确和错误的题目编号
                correct_numbers = [i for i, (is_correct, _) in enumerate(results, 1) if is_correct]
                wrong_numbers = [i for i, (is_correct, _) in enumerate(results, 1) if not is_correct]
                
                # 按照要求格式写入
                if correct_numbers:
                    correct_str = ", ".join(map(str, correct_numbers))
                    f.write(f"Correct: {correct_count} ({correct_str})\n")
                else:
                    f.write(f"Correct: {correct_count}\n")
                
                if wrong_numbers:
                    wrong_str = ", ".join(map(str, wrong_numbers))
                    f.write(f"Wrong: {wrong_count} ({wrong_str})\n")
                else:
                    f.write(f"Wrong: {wrong_count}\n")
            
            print(f"批改结果文件已写入: {filename}")
        except Exception as e:
            raise Exception(f"写入批改结果文件失败: {e}")
    
    def validate_file_format(self, filename: str, file_type: str) -> bool:
        """
        验证文件格式
        
        Args:
            filename (str): 文件名
            file_type (str): 文件类型 ("exercise" 或 "answer")
            
        Returns:
            bool: 格式是否正确
        """
        try:
            if file_type == "exercise":
                exercises = self.read_exercises(filename)
                return len(exercises) > 0
            elif file_type == "answer":
                answers = self.read_answers(filename)
                return len(answers) > 0
            else:
                return False
        except Exception:
            return False
    
    def find_answer_files(self, directory: str) -> List[str]:
        """
        在目录中查找所有答案文件
        
        Args:
            directory (str): 目录路径
            
        Returns:
            List[str]: 答案文件路径列表
        """
        answer_files = []
        
        # 递归遍历目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                # 检查文件扩展名
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    # 跳过批改结果文件
                    if not file.endswith('_Grade.txt') and not file.endswith('Grade.txt'):
                        answer_files.append(file_path)
        
        return sorted(answer_files)
    
    def get_file_stats(self, filename: str) -> Dict[str, Any]:
        """
        获取文件统计信息
        
        Args:
            filename (str): 文件名
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            return {
                "total_lines": len(lines),
                "non_empty_lines": len([line for line in lines if line.strip()]),
                "file_size": os.path.getsize(filename)
            }
        except Exception:
            return {
                "total_lines": 0,
                "non_empty_lines": 0,
                "file_size": 0
            }


class FileValidator:
    """文件验证器"""
    
    def __init__(self):
        self.file_handler = FileHandler()
    
    def validate_exercise_file(self, filename: str) -> Tuple[bool, str]:
        """
        验证题目文件格式
        
        Args:
            filename (str): 文件名
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not os.path.exists(filename):
            return False, f"文件不存在: {filename}"
        
        try:
            exercises = self.file_handler.read_exercises(filename)
            if not exercises:
                return False, "文件为空或格式错误"
            
            # 验证每个题目是否可以解析
            for i, exercise in enumerate(exercises, 1):
                try:
                    self.file_handler.parser.parse(exercise)
                except Exception as e:
                    return False, f"第{i}题解析失败: {e}"
            
            return True, ""
        except Exception as e:
            return False, f"文件读取失败: {e}"
    
    def validate_answer_file(self, filename: str) -> Tuple[bool, str]:
        """
        验证答案文件格式
        
        Args:
            filename (str): 文件名
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not os.path.exists(filename):
            return False, f"文件不存在: {filename}"
        
        try:
            answers = self.file_handler.read_answers(filename)
            if not answers:
                return False, "文件为空或格式错误"
            
            return True, ""
        except Exception as e:
            return False, f"文件读取失败: {e}"


# 便捷函数
def write_problems_to_files(problems: List[Tuple[str, str]], 
                          exercise_file: str = "Exercises.txt",
                          answer_file: str = "Answers.txt"):
    """
    将题目写入文件的便捷函数
    
    Args:
        problems (List[Tuple[str, str]]): 题目列表
        exercise_file (str): 题目文件名
        answer_file (str): 答案文件名
    """
    handler = FileHandler()
    handler.write_exercises(problems, exercise_file)
    handler.write_answers(problems, answer_file)


def grade_problems_from_files(exercise_file: str, answer_file: str,
                            grade_file: str = "Grade.txt") -> Dict[str, Any]:
    """
    从文件批改题目的便捷函数
    
    Args:
        exercise_file (str): 题目文件名
        answer_file (str): 答案文件名
        grade_file (str): 批改结果文件名
        
    Returns:
        Dict[str, Any]: 批改统计信息
    """
    handler = FileHandler()
    
    # 读取题目和答案
    exercises = handler.read_exercises(exercise_file)
    answers = handler.read_answers(answer_file)
    
    # 批改题目
    results = handler.grade_exercises(exercises, answers)
    
    # 写入批改结果
    handler.write_grade_results(results, grade_file)
    
    # 返回统计信息
    correct_count = sum(1 for is_correct, _ in results if is_correct)
    total_count = len(results)
    
    return {
        "total": total_count,
        "correct": correct_count,
        "wrong": total_count - correct_count,
        "accuracy": correct_count / total_count if total_count > 0 else 0
    }


# 测试代码
if __name__ == "__main__":
    print("=== 文件处理工具测试 ===")
    
    # 创建测试题目
    test_problems = [
        ("1 + 2", "3"),
        ("3 * 4", "12"),
        ("1/2 + 1/3", "5/6"),
        ("(1 + 2) * 3", "9")
    ]
    
    # 测试文件写入
    handler = FileHandler()
    handler.write_exercises(test_problems, "test_exercises.txt")
    handler.write_answers(test_problems, "test_answers.txt")
    
    # 测试文件读取
    exercises = handler.read_exercises("test_exercises.txt")
    answers = handler.read_answers("test_answers.txt")
    
    print(f"读取到 {len(exercises)} 道题目")
    print(f"读取到 {len(answers)} 个答案")
    
    # 测试批改功能
    results = handler.grade_exercises(exercises, answers)
    correct_count = sum(1 for is_correct, _ in results if is_correct)
    print(f"批改结果: {correct_count}/{len(results)} 正确")
    
    # 测试文件验证
    validator = FileValidator()
    is_valid, error_msg = validator.validate_exercise_file("test_exercises.txt")
    print(f"题目文件验证: {'通过' if is_valid else '失败 - ' + error_msg}")
    
    # 清理测试文件
    for filename in ["test_exercises.txt", "test_answers.txt"]:
        if os.path.exists(filename):
            os.remove(filename)
    
    print("测试完成")
