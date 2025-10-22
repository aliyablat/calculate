#!/usr/bin/env python3
"""
四则运算题目生成器 - 主程序

支持生成和批改四则运算题目
"""

import argparse
import sys
import os
from typing import List, Tuple

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from problem_generator import ProblemGenerator, ProblemValidator
from deduplicator import Deduplicator
from file_utils import FileHandler


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='四则运算题目生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  生成题目: python main.py -n 10 -r 10
  批改单个学生: python main.py -e Exercises.txt -a student1_answers.txt
  批改多个学生: python main.py -e Exercises.txt -a student_answers/
        """
    )
    
    # 生成模式参数
    parser.add_argument('-n', '--number', type=int, 
                       help='生成题目数量 (1-10000)')
    parser.add_argument('-r', '--range', type=int, 
                       help='数值范围上限 (1-100)')
    
    # 批改模式参数
    parser.add_argument('-e', '--exercise', type=str,
                       help='题目文件路径')
    parser.add_argument('-a', '--answer', type=str,
                       help='学生答案文件路径或目录路径')
    
    args = parser.parse_args()
    
    # 验证参数
    validate_arguments(args)
    
    return args


def validate_arguments(args):
    """
    验证命令行参数
    
    Args:
        args: 解析后的参数
        
    Raises:
        SystemExit: 参数无效时退出程序
    """
    # 检查是否提供了生成或批改参数
    has_generate = args.number is not None or args.range is not None
    has_grade = args.exercise is not None or args.answer is not None
    
    if not has_generate and not has_grade:
        print("错误: 必须提供生成参数(-n, -r)或批改参数(-e, -a)")
        print("使用 -h 查看帮助信息")
        sys.exit(1)
    
    # 验证生成模式参数
    if has_generate:
        if args.number is None:
            print("错误: 生成模式必须指定题目数量(-n)")
            sys.exit(1)
        if args.range is None:
            print("错误: 生成模式必须指定数值范围(-r)")
            sys.exit(1)
        
        if not (1 <= args.number <= 10000):
            print("错误: 题目数量必须在1-10000之间")
            sys.exit(1)
        
        if not (1 <= args.range <= 100):
            print("错误: 数值范围必须在1-100之间")
            sys.exit(1)
    
    # 验证批改模式参数
    if has_grade:
        if args.exercise is None or args.answer is None:
            print("错误: 批改模式必须同时指定题目文件(-e)和答案文件/目录(-a)")
            sys.exit(1)
        
        if not os.path.exists(args.exercise):
            print(f"错误: 题目文件不存在: {args.exercise}")
            sys.exit(1)
        
        if not os.path.exists(args.answer):
            print(f"错误: 答案文件/目录不存在: {args.answer}")
            sys.exit(1)


def generate_problems_mode(number: int, max_range: int):
    """
    生成题目模式
    
    Args:
        number (int): 题目数量
        max_range (int): 数值范围上限
    """
    print(f"正在生成 {number} 道题目，数值范围: 1-{max_range}")
    
    # 创建题目生成器
    generator = ProblemGenerator(min_value=1, max_value=max_range)
    
    # 生成题目
    problems = generator.generate_problems(number)
    
    # 创建文件处理器
    file_handler = FileHandler()
    
    # 写入题目文件
    exercises_file = "Exercises.txt"
    answers_file = "Answers.txt"
    
    file_handler.write_exercises(problems, exercises_file)
    file_handler.write_answers(problems, answers_file)
    
    print(f"题目已生成:")
    print(f"  - 题目文件: {exercises_file}")
    print(f"  - 答案文件: {answers_file}")
    print(f"  - 题目数量: {len(problems)}")


def grade_problems_mode(exercise_file: str, answer_path: str):
    """
    批改题目模式
    
    Args:
        exercise_file (str): 题目文件路径
        answer_path (str): 学生答案文件路径或目录路径
    """
    print(f"正在批改题目...")
    print(f"  - 题目文件: {exercise_file}")
    print(f"  - 答案路径: {answer_path}")
    
    # 创建文件处理器
    file_handler = FileHandler()
    
    # 读取题目
    try:
        exercises = file_handler.read_exercises(exercise_file)
    except Exception as e:
        print(f"错误: 读取题目文件失败 - {e}")
        sys.exit(1)
    
    # 判断是文件还是目录
    if os.path.isfile(answer_path):
        # 单个文件批改
        answer_files = [answer_path]
        print("批改模式: 单个学生答案文件")
    elif os.path.isdir(answer_path):
        # 目录批改
        try:
            answer_files = file_handler.find_answer_files(answer_path)
        except Exception as e:
            print(f"错误: 查找答案文件失败 - {e}")
            sys.exit(1)
        
        if not answer_files:
            print(f"错误: 在目录 {answer_path} 中未找到答案文件")
            sys.exit(1)
        
        print(f"批改模式: 目录批改，找到 {len(answer_files)} 个学生答案文件")
    else:
        print(f"错误: 答案路径既不是文件也不是目录: {answer_path}")
        sys.exit(1)
    
    # 批改每个学生的答案
    total_correct = 0
    total_wrong = 0
    
    for answer_file in answer_files:
        try:
            print(f"正在批改: {answer_file}")
            
            # 读取学生答案
            student_answers = file_handler.read_answers(answer_file)
            
            # 验证文件格式
            if len(exercises) != len(student_answers):
                print(f"  警告: 题目数量({len(exercises)})与学生答案数量({len(student_answers)})不匹配，跳过")
                continue
            
            # 批改题目
            results = file_handler.grade_exercises(exercises, student_answers)
            
            # 生成批改结果文件名
            base_name = os.path.splitext(os.path.basename(answer_file))[0]
            if os.path.isfile(answer_path):
                # 单个文件模式，在当前目录生成结果
                grade_file = f"{base_name}_Grade.txt"
            else:
                # 目录模式，在答案文件同目录生成结果
                grade_file = os.path.join(os.path.dirname(answer_file), f"{base_name}_Grade.txt")
            
            # 写入批改结果
            file_handler.write_grade_results(results, grade_file)
            
            # 统计结果
            correct_count = sum(1 for is_correct, _ in results if is_correct)
            wrong_count = len(results) - correct_count
            total_correct += correct_count
            total_wrong += wrong_count
            
            print(f"  批改完成: 正确 {correct_count}, 错误 {wrong_count}, 正确率 {correct_count/len(results)*100:.1f}%")
            print(f"  批改结果文件: {grade_file}")
            
        except Exception as e:
            print(f"  错误: 批改文件 {answer_file} 失败 - {e}")
            continue
    
    print(f"\n批改完成:")
    print(f"  - 批改文件数: {len(answer_files)}")
    print(f"  - 总正确题目: {total_correct}")
    print(f"  - 总错误题目: {total_wrong}")
    if total_correct + total_wrong > 0:
        print(f"  - 总体正确率: {total_correct/(total_correct+total_wrong)*100:.1f}%")


def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 根据参数选择模式
        if args.number is not None and args.range is not None:
            # 生成模式
            generate_problems_mode(args.number, args.range)
        elif args.exercise is not None and args.answer is not None:
            # 批改模式
            grade_problems_mode(args.exercise, args.answer)
        else:
            print("错误: 参数组合无效")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
