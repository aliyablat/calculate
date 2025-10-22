- # [软件工程作业三](https://www.cnblogs.com/aliyaablat/p/19156576)

   计算机科学与技术 王阿丽亚·阿不来海提 3223004639

   计算机科学与技术 阿依古再丽·艾力 3223004595

   | 这个作业属于哪个课程 | https://edu.cnblogs.com/campus/gdgy/Class34Grade23ComputerScience |      |
   | -------------------- | ------------------------------------------------------------ | ---- |
   | 这个作业要求在哪里   | https://edu.cnblogs.com/campus/gdgy/Class34Grade23ComputerScience/homework/13477 |      |
   | 这个作业目标         | 实现一个自动生成小学四则运算题目的命令行程序                 |      |

   ## PSP表格相关记录

   | PSP2 1                                | Personal Software Process Stages       | 预估耗时（分钟） | 实际耗时（分钟） |
   | ------------------------------------- | -------------------------------------- | ---------------- | ---------------- |
   | Planning                              | 计划                                   | 30               | 30               |
   | Estimate                              | 估计这个任务需要多少时间               | 615              | 605              |
   | Development                           | 开发                                   | 15               | 15               |
   | Analysis                              | 需求分析（包括学习新技术）             | 60               | 90               |
   | Design Spec                           | 生成设计文档                           | 20               | 10               |
   | Design Review                         | 设计复审                               | 30               | 15               |
   | Coding Standard                       | 代码规范（为目前的开发制定合适的规范） | 30               | 30               |
   | Design                                | 具体设计                               | 60               | 60               |
   | Coding                                | 具体编码                               | 240              | 240              |
   | Code Review                           | 代码复审                               | 10               | 10               |
   | Test                                  | 测试（自我测试，修改代码，提交修改）   | 30               | 40               |
   | Reporting                             | 报告                                   | 15               | 15               |
   | Test Report                           | 测试报告                               | 15               | 15               |
   | Size Measurement                      | 计算工作量                             | 30               | 15               |
   | Postmortem & Process Improvement Plan | 事后总结，并提出过程改进计划           | 30               | 20               |

   ## 模块接口的设计与实现过程

   ### 总体说明

   目标：生成小学四则运算题目、解析与计算表达式、并对用户答案进行判题与评分。各模块职责清晰，尽量使用 Fraction 类型保证精度。
   公共约定：表达式树使用 tuple 结构 (op, left, right) 或 Fraction/int 作为叶子。所有 I/O 操作（读写文件）封装成可能抛出 FileOperationError 的高层 API。
   解析/计算失败使用领域异常：ExpressionParseError、RuleViolationError、ParameterValidationError 等。

   -  errors.py — 异常模块
      目的：定义域内自定义异常类型，统一错误处理接口。
      公共类型（接口）：
   -  CalculatorError(Exception) — 基类。
   -  RuleViolationError(CalculatorError) — 规则校验失败（如生成题目时出现负数、不合法分数等）。
   -  ExpressionParseError(CalculatorError) — 解析表达式失败，构造器允许传入 message 与 text（原始文本）。
   -  FileOperationError(CalculatorError) — 封装文件 I/O 错误，构造器接受 message 和可选 path 字段。
   -  ParameterValidationError(CalculatorError) — 输入参数验证失败。
   -  utils.py — 工具库
      主要职责：
      格式化与解析分数（format_fraction, parse_fraction）。
      将表达式树正规化用于去重（normalize_expr）。
      表达式词法与语法解析：tokenize、parse_expression（返回表达式树）。
      基础分数算术封装（fraction_add/sub/mul/div）与便利函数 is_proper_fraction。

   ### 主要函数摘要

   -  format_fraction(frac: Fraction|int) -> str
      描述：把 Fraction 格式化为字符串，真分数显示为 "a'b/c" 或 "num/den" 或整数。
      错误模式：接受可转为 Fraction 的对象；不会抛错，除非传入非法类型（会在调用处报错）。
   -  parse_fraction(s: str) -> Fraction
      描述：解析字符串到 Fraction，支持 "2'3/5"、"3/5"、"2"。
      错误模式：无法解析时抛 ExpressionParseError（含原文本）。
   -  tokenize(expr: str) -> iterator[(kind, token)]
      描述：词法化；在遇到无法识别字符时抛 ExpressionParseError，提供位置信息。
   -  parse_expression(s: str) -> expr_tree
      描述：基于递归下降解析实现，返回表达式树（tuple 或 Fraction/int）。
      错误模式：遇到语法错误抛 ExpressionParseError；接口保证在输入合法时返回可交给 eval_expr 的树。
   -  normalize_expr(expr) -> str
      描述：把表达式树归一化为字符串键，支持 + 和 × 的交换律（将子项排序）。
      用途：用于题目去重集合的判定。
   -  generator.py— 题目生成模块
      主要职责：
      随机生成题目表达式树（random_expr、random_number）。
      计算表达式值（eval_expr）。
      将表达式转换为字符串（expr_to_str）。
      批量生成并写入文件（generate(n, r) -> writes Exercises.txt & Answers.txt）。
      接口契约（函数签名）：
   -  random_number(r: int) -> int|Fraction
      行为：以50%概率返回自然数或真分数，范围基于 r。
      错误模式：假定 r 为 int 且 r > 1。
   -  random_expr(r: int, max_ops: int=3) -> expr_tree
      描述：递归生成表达式树，max_ops 控制运算符数量。
   -  eval_expr(expr) -> Fraction
      描述：递归计算表达式树的 Fraction 结果；在非法数学情况时抛 ValueError（负数、除以0、非真分数结果等）。
   -  expr_to_str(expr) -> str
      描述：把表达式树转换为文本形式（带括号），叶子用 format_fraction 格式化。
   -  generate(n: int, r: int) -> None
      描述：生成 n 道题并写入 Exercises.txt 与 Answers.txt，过程进行参数验证、去重（normalize_expr）、规则校验（捕获 RuleViolationError）及 I/O 错误封装为FileOperationError。
      输出/副作用：在控制台打印生成数量；在异常情况下抛出 FileOperationError 或 ParameterValidationError。
      边界情况与错误模式：
      参数验证：n 必须为正 int，r 必须大于 1（否则抛 ParameterValidationError）。
      生成失败：在多次尝试后仍未生成足够题目，函数当前只是结束并写入已生成的题目；可增强以在不足时抛自定义异常或返回状态。
      数学规则：eval_expr 对减法、除法结果做严格检查（例如不允许负数和非真分数），并抛 ValueError；这被 generator 捕获并跳过该表达式。
      grader.py — 判题模块
      主要职责：
      读取题目文件与用户答案文件，解析题目文本为表达式树，计算标准答案，比较用户答案并把统计写回 [Grade.txt](vscode-file://vscode-app/d:/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)。

   ### 公共接口

   grade(exercise_file: str, answer_file: str) -> None
   输入：exercise_file（路径），answer_file（路径）
   行为：读取两文件、逐行解析表达式、计算标准值、解析用户答案（parse_fraction），比对并分类到 correct/wrong、最后写 [Grade.txt](vscode-file://vscode-app/d:/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)。
   错误模式：文件读写失败抛 FileOperationError；解析失败会将该题计为 wrong，并在日志中记录 debug；在极端未处理异常时捕获并记录，继续判题以保证输出。

   ### 边界情况

   文件行数不匹配：如果 user_answers 更短，后续题目不会被判分（未处理）。
   解析差异：若表达式解析成功但 eval_expr 抛异常，当前会被 broad except 捕获并计为 wrong（并输出到控制台）。
   数据形状与示例

   ### 表达式树示例：

   5 -> int or Fraction(5,1)
   ( '+', 1, 2 ) -> 表示 1 + 2
   ( '×', ( '+', 1, 2 ), 3 ) -> (1+2)×3
   normalize_expr 返回例如 "+(1/2,3/4)" 用于集合去重。

   ### generate 输出文件格式

   Exercises.txt的行： "1/2 + 3 ="
   Answers.txt 的行： "7/2" 或 "3'1/2"（由 format_fraction 产生）
   Grade.txt

   ### 格式

   Correct: (list)
   Wrong: (list)
   错误与异常模型（总结）

   -  低层（解析/数学）：
      ExpressionParseError（解析问题）
      ValueError（当前用于数学约束，如负数、除零）
   -  中层（生成/判题）：
      RuleViolationError（生成时违反表达式规则）
      ParameterValidationError（非法参数）
   -  高层（I/O）：
      FileOperationError（读写失败，包含 path）
   -  规则检查处理
      目标：检查数学运算中不符合题目规则要求的情况（如除以零、减法产生负值、除法结果不是真分数等）。

   对应代码片段：
   def **truediv**(self, other: 'FractionNumber') -> 'FractionNumber': # 除零异常检查
   if other.numerator == 0: # 检查是否存在除数为零的情况
   raise ZeroDivisionError("Cannot divide by zero.")
   new_num = self.numerator * other.denominator
   new_den = self.denominator * other.numerator
   return FractionNumber(new_num, new_den)

   def **sub**(self, other: 'FractionNumber') -> 'FractionNumber': # 减法结果负值异常检查
   new_num = self.numerator * other.denominator - other.numerator * self.denominator
   new_den = self.denominator * other.denominator
   return FractionNumber(new_num, new_den)

   elif self.op == '-': # 检查是否存在e1 < e2的情况
   if l.value() < r.value():
   raise ValueError("Subtraction would result in negative.")
   return l - r

   def is_proper_fraction(fraction: FractionNumber) -> bool: # 真分数约束检查
   return abs(fraction.numerator) < fraction.denominator and fraction.denominator > 1

   if op == '/': # 在除法运算后的验证
   res = l / r # 严格检查除法结果是否为真分数
   if not is_proper_fraction(res):
   raise ValueError("Division result must be a proper fraction...")

   -  表达式解析异常处理
      目标：处理用户输入表达式格式错误或求值错误（语法错误、非法字符、运算异常等）。

   对应代码片段：
   def evaluate_expression(expression: str) -> FractionNumber:
   expr_processed = preprocess_expression(expression)
   try:
   result = eval(expr_processed)
   except Exception as e:
   raise ValueError(f"表达式求值失败：{e}")
   if isinstance(result, Fraction): # 类型检查
   return FractionNumber(int(result.numerator), int(result.denominator))
   elif isinstance(result, int):
   return FractionNumber(result, 1)
   else:
   raise ValueError(f"无法识别的计算结果类型：{type(result)}")

   -  文件操作异常处理
      目标：确保文件读写操作的可靠性并在异常时给出明确提示或回退。

   对应代码片段：
   def compare_answers(exercise_file: str, answer_file: str):
   try:
   with open(exercise_file, 'r', encoding='utf-8') as f:
   exercises = f.readlines()
   with open(answer_file, 'r', encoding='utf-8') as f:
   answers = f.readlines()
   if len(exercises) != len(answers):
   print(f"❌ 错误：题目数量({len(exercises)}) 与答案数量({len(answers)}) 不相等。")
   return
   except Exception as e:
   print(f"批改时发生错误：{e}")

   -  题目生成重试机制
      目标：处理生成过程中的临时错误和不满足规则的情况，确保最终输出满足约束或在失败时以明确方式终止。

   对应代码片段：
   def generate_expression(r: int, max_ops: int = MAX_OPERATORS) -> Tuple[str, FractionNumber, str]:
   num_tries = 0
   max_tries = 1000
   while num_tries < max_tries:
   num_tries += 1
   try: # 生成逻辑
   return expr_str, val, structure_hash
   except Exception as e:
   continue # 静默重试
   raise RuntimeError("Failed to generate valid expression after many tries.")

   -  参数验证异常
      目标：确保程序入口输入参数合法，避免下游函数收到非法参数导致难以排查的错误。

   对应代码片段：
   def main(): # 参数解析
   if r < 1:
   print("❌ 错误：-r 后的数值范围必须 >= 1，例如：-r 10")
   return
   except ValueError:
   print("❌ 错误：-n 后必须跟一个整数，表示题目数量。例如：-n 10")
   return

   ## 项目总结

   通过本次结对编程项目，我们圆满实现了需求规格中的所有功能要求，并在合作过程中获得了显著的成长与收获。在项目成果方面，结对编程模式有效提升了我们的代码质量。通过实时代码审查和深入讨论，我们成功减少了因疏忽导致的低级错误。特别是在分数运算和表达式生成等复杂功能的实现过程中，持续的头脑风暴和即时反馈帮助我们攻克了多个技术难点，确保了项目的顺利推进。在个人成长与团队协作方面，这次合作为我们创造了宝贵的相互学习机会。团队成员各展所长：一位成员在编码实现和调试方面表现出色，能够熟练运用调试工具进行性能分析，快速定位问题根源；另一位成员则展现了优秀的架构设计能力，善于从整体角度规划代码结构，避免陷入细节陷阱，同时在调试复杂逻辑时展现出极大的耐心和细致。这种优势互补的合作模式，特别是在代码规范和模块化设计方面的深入交流，为我们后续的项目开发奠定了坚实基础。通过项目复盘，我们也认识到在逻辑严谨性方面仍有提升空间，代码问题的排查效率可以进一步优化。展望未来的项目开发，我们计划更系统地采用测试驱动开发方法，并建立更完善的调试流程，以持续提升代码质量。
