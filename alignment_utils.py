import bisect
import re
import regex
import statistics
import numpy as np


GET_TOPIC_PATTERN = re.compile(r'^(\d+)\\*[．. ]|^(\\*[（(])\d+\\*[）)]|^\\*\d+\\\.|^\d+、|^\d+[ABCD] |^\[(\d+)\]|^\d+\（')
REMOVE_NOISE_CHAR = re.compile(r'image\d+\.')
GET_TOPIC_PATTERN_IN_NOT_START = regex.compile(r'(\d+)\\*[．. ]|(\\*[（(])\d+\\*[）)]|\\*\d+\\\.|\d+、|^\d+[ABCD]')


def one_file_per_process(text):
    """
    接受一个可能包含多行的文本字符串，将其拆分为行，去除每一行中的某些特定字符，移除空行，然后将清理后的行重新组合成一个单一的字符串。
    
    参数:
        text (str): 可以包含多行的文本字符串。
        
    返回:
        str: 每一行都已经被清理和重新组装的文本字符串。
    """

    liens = text.splitlines()
    liens = map(lambda x: x.replace("> ", "").replace(">", "").replace("*", "").replace("\u3000", ""), liens)
    liens = filter(lambda x: x.strip() != "", liens)
    return "\n".join(liens)


def extract_and_combine_numbers(str_val):
    """
    从给定的字符串中提取数字，它会寻找字符串中开始的题号，然后从中提取出数字字符，再将它们组合在一起。
    
    参数:
        str_val (str): 输入字符串，需要从中提取数字。
        
    返回:
        int: 从输入字符串中提取出的数字。如果没有数字，就返回0。
    """
    match = GET_TOPIC_PATTERN.match(str_val)

    numbers = None
    if match:
        numbers = ''.join(c for c in match[0] if c.isdigit())

    return int(numbers) if numbers else None


def extract_and_combine_numbers_in_not_start(str_val):
    """
     从给定的字符串中提取数字，它会寻找字符串中任意位置开始的第一个题号，然后从中提取出数字字符，再将它们组合在一起。
    
    参数:
        str_val (str): 输入字符串，需要从中提取数字。
        
    返回:
        int: 从输入字符串中提取出的数字。如果没有数字，就返回0。
    """
    str_val = REMOVE_NOISE_CHAR.sub("", str_val)
    pattern = regex.compile(r'(\d+\\*[．. ]|\\*[（(]\d+\\*[）)]|^\\*\d+\\\.|^\d+、|\d+[ABCD])')
    match = pattern.search(str_val)

    numbers = None
    if match:
        numbers = ''.join(c for c in match.group() if c.isdigit())

    return int(numbers) if numbers else None


def longest_increasing_subsequence_index(topics):
    """
    获取一个列表中的最长递增子序列的索引。首先，它从主题列表中提取数字，然后找到最长的递增子序列，只返回开始位置在topics长度一半之前的。
    
    参数:
        topics (list): 包含一系列题目的列表，这个题目列表应该是不完全正确的
        deviation: 允许在最长的公众序列中
        
    返回:
        list: 最长递增子序列的索引列表。
    """
    # Use a list of tuples, where each tuple contains the number and its index in the original list
    nums = [(extract_and_combine_numbers(topic), i) for i, topic in enumerate(topics) if extract_and_combine_numbers(topic) is not None]
    
    topics = nums
    if not nums:
        return []

    n = len(nums)
    dp = [[i] for i in range(n)]

    for i in range(n):
        for j in range(i):
            if nums[j][0] < nums[i][0]:
                if len(dp[j]) + 1 > len(dp[i]) or (len(dp[j]) + 1 == len(dp[i]) and dp[j][-1] == dp[i][-1] - 1):
                    dp[i] = dp[j] + [i]

    # We need to filter based on the original index, not the index in the nums list
    dp = list(filter(lambda lis:nums[lis[0]][1] < len(topics)/2, dp))
    dp = list(sorted(dp, key=lambda lis:len(lis), reverse=True))
    # Return the original indices, not the indices in the nums list
    return [nums[i][1] for i in dp[0]]


ANSWER_WORDS = ["答案", "参考答案", "试题解析", "参考解答"]
ANSWER_IN_QUESTION_WORDS = ["答案", "答", "解"]

def find_answer_split_str(all_question):
    """
    在试卷中寻找答案的位置，返回一个标志值或用于分隔答题区和答案区的字符串。
    
    参数:
        all_question (list): 包含所有问题的列表。
        
    返回:
        int/str: 返回一个标志值或用于分隔答题区和答案区的字符串。如果试卷无答案返回0，答案在每道试题下方返回1，如果答案在一个特定的区域，返回该区域的开始行。
    """

    occurrence_number = 0
    for question in all_question:
        if any(answer_word in question for answer_word in ANSWER_IN_QUESTION_WORDS):
            print(question)
            print("==============")
            occurrence_number += 1

    if occurrence_number == 0:
        return 0

    if occurrence_number > len(all_question) / 2:
        return 1

    for line in all_question[-1].split("\n"):
        if any(answer_word in line for answer_word in ANSWER_WORDS):
            return line

    return -1


def find_next_question_index(start, lines):
    """
    从给定的开始位置搜索下一道题目的索引。
    
    参数:
        start (int): 搜索的开始位置。
        lines (list): 包含所有行的列表。
        
    返回:
        int: 下一道题目的索引位置。如果没有更多的题目，就返回行列表的长度（即：返回到行列表的末尾）。
    """

    for index in range(start + 1, len(lines)):
        match = GET_TOPIC_PATTERN.match(lines[index])

        if match:
            return index

    return len(lines)


def generate_answer_area_string(text: str, split_str):
    splited_text = text.split(split_str)

    splited_text = list(filter(lambda x:x.replace(" ","") != "", splited_text))
    return None if len(splited_text) == 1 else "\n".join(splited_text[1:])


def answer_area_str_process(text):
    '''
    对包含答案的文本进行处理，主要是对每一行的处理。如果一行以中文数字开始，那么就提取该行第一个阿拉伯数字以后的内容，否则就保留该行。

    Args:
    text: 一个包含答案的文本。

    Returns:
    result: 一个处理后的字符串，每一行都已经进行了处理。
    '''

    lines = text.split('\n')
    result = []
    for line in lines:
        # 检查每一行是否以中文数字开始
        if re.match('^[一二三四五六七八九十]', line):
            line = REMOVE_NOISE_CHAR.sub("", line)
            matches = GET_TOPIC_PATTERN_IN_NOT_START.findall(line)
            # 如果找到匹配，那么就提取该行第一个匹配以后的内容
            if matches:
                first_match = matches[0][0] if matches[0][0] != '' else matches[0][1]
                pos = line.find(first_match)
                result.append(line[pos:].strip())
        else:
            # 如果一行不是以中文数字开始，那么就保留该行
            result.append(line.strip())
    return "\n".join(result)


def match_specific_from_end(text, number):
    '''
    从文本的末尾开始，匹配特定的数字。

    Args:
    text: 需要匹配的文本。
    number: 需要匹配的数字。

    Returns:
    返回一个元组，包含三个元素。第一个元素是匹配的文本，第二个元素是移除匹配部分后的剩余文本，第三个元素是文本开始的数字。如果没有匹配，那么返回(None, None, None)。
    '''
    text = REMOVE_NOISE_CHAR.sub("", text)
    pattern = regex.compile(r'(\d+\\*[．. ]|\\*[（(]\d+\\*[）)]|^\\*\d+\\\.|^\d+、|\d+[ABCD])')

    matches = [m for m in pattern.finditer(text)]

    if matches:
        specific_match = None
        for match in reversed(matches):  # 反向列表，从末尾开始匹配
            match_number = int(re.search(r'\d+', match.group()).group())
            if match_number == number:
                specific_match = match
                break
        if specific_match is None:
            return None, None, None
        else:
            # 在完整文本中匹配第一个符合模式的数字
            text = REMOVE_NOISE_CHAR.sub("", text)
            start_match = GET_TOPIC_PATTERN.search(text)
            if start_match:
                match_group = start_match.group()
            else:
                start_match = GET_TOPIC_PATTERN_IN_NOT_START.search(text)
                match_group = start_match.group()

            start_number = int(re.search(r'\d+', match_group).group())  # 提取数字部分
            remaining_text = text[:specific_match.start()]  # 移除匹配部分后的剩余文本
            return text[specific_match.start():], remaining_text, start_number
    else:
        return None, None, None


def match_specific_from_start(text, number):
    '''
    从文本的开始，匹配特定的数字。

    Args:
        text (str): 需要匹配的文本。
        number (int): 需要匹配的数字。

    Returns:
        tuple: 返回一个元组，包含两个元素。
               第一个元素是匹配的文本，第二个元素是匹配到的所有文本（包括当前行）。
               如果没有匹配，返回 (None, None)。
    '''
    lines = text.splitlines()
    number = str(number)
    pattern = re.compile(f'({number})[．.|\(]|（{number}）|{number}\\.|{number}、')
    for index, line in enumerate(lines):
        match = pattern.search(line)

        if match:
            return "\n".join(lines[:index]), "\n".join(lines[index:])

    return None, None


def refine_answers(raw_answer_list):
    '''
    对一个包含未完全处理好的答案列表进行重新拆分，以使其更为完整。

    Args:
    raw_answer_list: 一个包含未完全处理好的答案的列表。

    Returns:
    refined_answers: 一个包含重新处理过的答案的列表。
    '''

    refined_answers = []
    reversed_answers = raw_answer_list[::-1]

    # 对反向答案列表中的每一个答案进行遍历
    for index, current_answer in enumerate(reversed_answers):
        # 获取下一个题目的序号，如果当前题目是列表中的最后一个，
        # 那么下一个题目的序号应该是列表中的第一个题目的序号
        if index >= len(reversed_answers) - 1:
            next_topic_number = extract_and_combine_numbers(raw_answer_list[0])
        else:
            # 否则，下一个题目的序号应该是当前题目在反向列表中的下一个题目的序号
            next_topic_number = extract_and_combine_numbers(reversed_answers[index + 1])

        # 获取当前答案对应的题目序号
        current_topic_number = extract_and_combine_numbers(current_answer)

        # 从答案的末尾开始查找，尝试匹配题目序号+1的答案
        previous_answer, remaining_text, start_number = match_specific_from_end(current_answer,
                                                                                current_topic_number + 1)

        # 如果找到了匹配的答案，那么将剩余的文本添加到所有答案的列表中
        if previous_answer:
            refined_answers.append(remaining_text)
        else:
            # 否则，直接将当前答案添加到所有答案的列表中
            refined_answers.append(current_answer)

        # 计算逻辑上的上一道题的题目序号（如现在是20题，那么"previous_topic_number"应该等于19）
        previous_topic_number = current_topic_number - 1

        # 如果下一序列的道题的题目序号等于逻辑上的上一道题的题目序号，那么继续下一次循环
        if next_topic_number == previous_topic_number:
            continue

        # 否则，将反向答案列表中的剩余部分合并成一段文本
        search_text = "/n".join(reversed_answers[:index:-1])

        # 当下一道题的题目序号小于上一道题的题目序号时，进入循环
        while next_topic_number < previous_topic_number:
            # 从文本的末尾开始查找，尝试匹配上一道题的题目序号的答案
            previous_answer, remaining_text, start_number = match_specific_from_end(search_text, previous_topic_number)

            # 如果没有找到匹配的答案
            if not previous_answer:
                refined_answers.append(search_text)
                break

            # 如果找到了匹配的答案，那么将该答案添加到所有答案的列表中
            refined_answers.append(previous_answer)
            # 计算前一道题的题目序号
            previous_topic_number -= 1
            # 更新待查找的文本
            search_text = remaining_text

    # 返回所有答案的列表
    return refined_answers


ANSWERS_KEY_WORDS_IN_QUESTIONS = ["标准答案", "试题分析", "答案", "解析", "答", "解"]


def split_text_by_keywords(text: str, keywords: list) -> dict:
    # Create the regular expression pattern for the first match from the left
    # pattern = r"(【(?:" + "|".join(re.escape(keyword) for keyword in ANSWERS_KEY_WORDS_IN_QUESTIONS) + r")】)"
    pattern = r"【[^】]*】"
    match = re.search(pattern, text)

    if not match:
        pattern = f"({'|'.join(ANSWERS_KEY_WORDS_IN_QUESTIONS)})"
        lines = text.splitlines()

        for index in range(1, len(lines)-1):
            line = lines[index]
            match = re.search(pattern, line)
            if match:
                return {
                    "question": "\n".join(lines[:index]),
                    "answer": "\n".join(lines[index:])
                }
                    
    else:
        # Get the matched text
        matched_text = match.group(0)

        # Split the text into two parts at the matched text
        first_part, second_part = text.split(matched_text, 1)

        # Return the result as a dictionary
        return {
            "question": first_part.strip(),
            "answer": matched_text + second_part.strip()
        }
    


def align_answers_in_questions(questions: list, keywords: list = ANSWERS_KEY_WORDS_IN_QUESTIONS) -> list:
    answers_with_questions = []
    for question in questions:
        answer_with_question = split_text_by_keywords(question, keywords)
        if answer_with_question:
            answers_with_questions.append(answer_with_question)

    return answers_with_questions


def type_of_judgment(text):
    """判断文本类型。

    该函数接受一个文本块，并根据问题编号列表中数字 "1" 的出现情况来确定判断类型。函数假设文本以 "一、"、"二、" 等形式进行编号。

    参数：
        text (str)：包含问题及其编号的输入文本。

    返回：
        bool：如果数字 "1" 出现次数超过问题数量的一半，则返回 True，否则返回 False。
    """
    
    # 将文本拆分成行
    lines = text.splitlines()
    
    # 初始化一个空列表用于存储问题编号
    question_number_list = []
    
    # 定义一个正则表达式模式，用于匹配问题编号如 "一、"、"二、" 等
    pattern = r'^[一二三四五六七八九十][、．.]'
    
    # 遍历文本中的每一行
    for i in range(len(lines)):
        line = lines[i]
        
        # 检查当前行是否匹配问题编号的模式
        match = re.match(pattern, line)
        
        if match:
            # 如果匹配成功，从下一行中提取并组合数字，并将其添加到列表中
            if i + 1 < len(lines):
                next_line = lines[i+1]
                question_number_list.append(extract_and_combine_numbers(next_line))
    
    # 统计问题编号列表中数字 "1" 的出现次数
    count_of_ones = question_number_list.count(1)
    
    # 如果数字 "1" 出现次数超过问题数量的一半，则返回 True，否则返回 False
    return count_of_ones > len(question_number_list) / 2


def split_question(question, topic_number=0, target_topic_number=0):
    """
    将问题拆分成子问题的函数。

    该函数将给定问题拆分为多个子问题，并返回一个子问题的列表。每个子问题以特定编号开始，编号从 `topic_number` 开始。
    搜索将从 `target_topic_number` 结束。如果未指定 `topic_number` 和 `target_topic_number`，则默认值为0。

    Args:
        question (str): 要拆分的问题文本。
        topic_number (int, optional): 子问题的起始编号。默认值为0。
        target_topic_number (int, optional): 拆分的终止编号。默认值为0。

    Returns:
        list: 包含拆分后的子问题的列表。
    """
    # 如果未指定 topic_number，则从问题文本中提取并组合数字作为起始编号
    topic_number = topic_number if topic_number else extract_and_combine_numbers(question)
    
    # 如果未指定 target_topic_number，则默认情况下进行递归搜索直到结束
    recursion = False if target_topic_number else True
    target_topic_number = target_topic_number if target_topic_number else topic_number + 1

    # 初始化用于存储拆分后子问题的列表
    split_question_list = []
    
    # 从问题文本和起始编号开始搜索子问题
    search_question = question
    search_number = topic_number + 1
    
    # 循环搜索子问题，直到达到目标编号或无法找到更多子问题
    while True:
        # 使用函数 match_specific_from_start 在搜索文本中匹配特定编号的子问题
        current_question, next_question = match_specific_from_start(search_question, search_number) 
        
        # 如果找到子问题，将其添加到拆分后的子问题列表中，并更新搜索文本为下一个问题的起始位置
        if current_question is not None:
            split_question_list.append(current_question)
            search_question = next_question
        else:
            break
            
        # 如果已经达到目标编号，而且不需要进行递归搜索，停止拆分
        if target_topic_number - search_number <= 0:
            if not recursion:
                break

        # 增加搜索编号，以搜索下一个子问题
        search_number = search_number + 1
        
    # 将最后一个子问题添加到列表中
    split_question_list.append(search_question)
   
    # 返回拆分后的子问题列表
    return split_question_list


def find_continuous_sequence(all_question):
    """
    查找连续编号问题序列的函数。

    该函数处理给定的问题列表 `all_question`，并查找其中连续编号的问题序列。
    连续编号的问题序列指的是问题编号相邻且连续的问题组成的序列。

    Args:
        all_question (list): 包含问题文本的列表。

    Returns:
        list: 包含连续编号问题序列的列表。
    """
    # 初始化一个新的问题列表，用于存储连续编号问题序列
    new_all_question = []
    
    # 遍历所有问题
    for index, question in enumerate(all_question):
        # 检查是否到达问题列表的末尾
        if index + 1 == len(all_question):
            # 如果到达末尾，则将当前问题拆分后添加到新的问题列表中，然后跳出循环
            new_all_question.append(question)
            break
            
        # 提取当前问题的编号
        topic_number = extract_and_combine_numbers(question)
        
        # 提取下一个问题的编号
        next_topic_number = extract_and_combine_numbers(all_question[index+1])
        
        # 如果当前问题编号加1等于下一个问题编号，则它们是连续的
        if topic_number + 1 == next_topic_number:
            # 将当前问题添加到新的问题列表中
            new_all_question.append(question)
            continue
        
        # 如果当前问题编号和下一个问题编号不连续，则需要拆分当前问题，并将拆分后的子问题添加到新的问题列表中
        new_all_question += split_question(question, topic_number, next_topic_number-1)
        
    # 返回包含连续编号问题序列的新问题列表
    return new_all_question




if __name__ == "__main__":
    test =['1．答卷前，考生务必将自己的姓名、准考证号填写在答题卡上。',
 '2．回答选择题时，选出每小题答案后，用铅笔把答题卡上对应题目的答案标号涂黑，如需改动，用橡皮擦干净后，再选涂其它答案标号。回答非选择题时，将答案写在答题卡上，写在本试卷上无效。',
 '3．考试结束后，将本试卷和答题卡一并交回。\n可能用到的相对原子质量：H 1 C 12 N 14 O 16 Na 23 Al 27 P 31 S 32 Cl 35.5 V 51 Fe 56\n一、选择题：本题共13个小题，每小题6分。共78分，在每小题给出的四个选项中，只有一项是符合题目要求的。',
 '7．国家卫健委公布的新型冠状病毒肺炎诊疗方案指出，乙醚、75%乙醇、含氯消毒剂、过氧乙酸(CH~3~COOOH)、氯仿等均可有效灭活病毒。对于上述化学药品，下列说法错误的是\nA．CH~3~CH~2~OH能与水互溶\nB．NaClO通过氧化灭活病毒\nC．过氧乙酸相对分子质量为76\nD．氯仿的化学名称是四氯化碳',
 '8．紫花前胡醇![](./notebook/image/media/image4.png)可从中药材当归和白芷中提取得到，能提高人体免疫力。有关该化合物，下列叙述错误的是\nA．分子式为C~14~H~14~O~4~\nB．不能使酸性重铬酸钾溶液变色\nC．能够发生水解反应\nD．能够发生消去反应生成双键',
 '9．下列气体去除杂质的方法中，不能实现目的的是\n  ----- ---------------- ----------------------\n        气体（杂质）     方法\n  A．   SO~2~（H~2~S）   通过酸性高锰酸钾溶液\n  B．   Cl~2~（HCl）     通过饱和的食盐水\n  C．   N~2~（O~2~）     通过灼热的铜丝网\n  D．   NO（NO~2~）      通过氢氧化钠溶液\n  ----- ---------------- ----------------------',
 '10．铑的配合物离子\\[Rh(CO)~2~I~2~\\]^－^可催化甲醇羰基化，反应过程如图所示。\n![](./notebook/image/media/image5.png)\n下列叙述错误的是\nA．CH~3~COI是反应中间体\nB．甲醇羰基化反应为CH~3~OH+CO=CH~3~CO~2~H\nC．反应过程中Rh的成键数目保持不变\nD．存在反应CH~3~OH+HI=CH~3~I+H~2~O',
 '11．1934年约里奥--居里夫妇在核反应中用α粒子（即氦核）轰击金属原子，得到核素，开创了人造放射性核素的先河：\n+→+\n其中元素X、Y的最外层电子数之和为8。下列叙述正确的是\nA．的相对原子质量为26 B．X、Y均可形成三氯化物\nC．X的原子半径小于Y的 D．Y仅有一种含氧酸',
 '12．科学家近年发明了一种新型Zn−CO~2~水介质电池。电池示意图如下，电极为金属锌和选择性催化材料，放电时，温室气体CO~2~被转化为储氢物质甲酸等，为解决环境和能源问题提供了一种新途径。\n![](./notebook/image/media/image10.png)\n下列说法错误的是\nA．放电时，负极反应为\nB．放电时，1 mol CO~2~转化为HCOOH，转移的电子数为2 mol\nC．充电时，电池总反应为\nD．充电时，正极溶液中OH^−^浓度升高',
 '13．以酚酞为指示剂，用0.1000 mol·L^−1^的NaOH溶液滴定20.00 mL未知浓度的二元酸H~2~A溶液。溶液中，pH、分布系数随滴加NaOH溶液体积的变化关系如下图所示。\n\\[比如A^2−^的分布系数：\\]\n![](./notebook/image/media/image16.png)\n下列叙述正确的是\nA．曲线①代表，曲线②代表\nB．H~2~A溶液的浓度为0.2000 mol·L^−1^\nC．HA^−^的电离常数K~a~=1.0×10^−2^\nD．滴定终点时，溶液中\n三、非选择题：共174分，第22\\~32题为必考题，每个试题考生都必须作答。第33\\~38题为选考题，考生根据要求作答。\n（一）必考题：共129分。',
 '26．（14分）\n钒具有广泛用途。黏土钒矿中，钒以+3、+4、+5价的化合物存在，还包括钾、镁的铝硅酸盐，以及SiO~2~、Fe~3~O~4~。采用以下工艺流程可由黏土钒矿制备NH~4~VO~3~。\n![](./notebook/image/media/image20.png)\n该工艺条件下，溶液中金属离子开始沉淀和完全沉淀的pH如下表所示：\n  ------------ -------- -------- -------- --------\n  金属离子     Fe^3+^   Fe^2+^   Al^3+^   Mn^2+^\n  开始沉淀pH   1.9      7.0      3.0      8.1\n  完全沉淀pH   3.2      9.0      4.7      10.1\n  ------------ -------- -------- -------- --------\n回答下列问题：\n（1）"酸浸氧化"需要加热，其原因是\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。\n（2）"酸浸氧化"中，VO^+^和VO^2+^被氧化成![](./notebook/image/media/image21.wmf)，同时还有\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_离子被氧化。写出VO^+^转化为![](./notebook/image/media/image21.wmf)反应的离子方程式\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。\n（3）"中和沉淀"中，钒水解并沉淀为![](./notebook/image/media/image22.wmf)，随滤液②可除去金属离子K^+^、Mg^2+^、Na^+^、\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_，以及部分的\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。\n（4）"沉淀转溶"中，![](./notebook/image/media/image22.wmf)转化为钒酸盐溶解。滤渣③的主要成分是\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。\n（5）"调pH"中有沉淀生产，生成沉淀反应的化学方程式是\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。\n（6）"沉钒"中析出NH~4~VO~3~晶体时，需要加入过量NH~4~Cl，其原因是\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。',
 '27．（15分）\n为验证不同化合价铁的氧化还原能力，利用下列电池装置进行实验。\n![](./notebook/image/media/image23.png)\n回答下列问题：\n（1）由FeSO~4~·7H~2~O固体配制0.10 mol·L^−1^ FeSO~4~溶液，需要的仪器有药匙、玻璃棒、\\_\\_\\_\\_\\_\\_\\_\\_\\_(从下列图中选择，写出名称)。\n![](./notebook/image/media/image24.png)\n（2）电池装置中，盐桥连接两电极电解质溶液。盐桥中阴、阳离子不与溶液中的物质发生化学反应，并且电迁移率(u^∞^)应尽可能地相近。根据下表数据，盐桥中应选择\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_作为电解质。\n  -------- ----------------------------------- -------- -----------------------------------\n  阳离子   u^∞^×10^8^/（m^2^·s^−1^·V^−1^）   阴离子   u^∞^×10^8^/（m^2^·s^−1^·V^−1^）\n  Li^+^    4.07                                         4.61\n  Na^+^    5.19                                         7.40\n  Ca^2+^   6.59                                Cl^−^    7.91\n  K^+^     7.62                                         8.27\n  -------- ----------------------------------- -------- -----------------------------------\n（3）电流表显示电子由铁电极流向石墨电极。可知，盐桥中的阳离子进入\\_\\_\\_\\_\\_\\_\\_\\_电极溶液中。\n（4）电池反应一段时间后，测得铁电极溶液中c(Fe^2+^)增加了0.02 mol·L^−1^。石墨电极上未见Fe析出。可知，石墨电极溶液中c(Fe^2+^)=\\_\\_\\_\\_\\_\\_\\_\\_。\n（5）根据（3）、（4）实验结果，可知石墨电极的电极反应式为\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_，铁电极的电极反应式为\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。因此，验证了Fe^2+^氧化性小于\\_\\_\\_\\_\\_\\_\\_\\_，还原性小于\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。\n（6）实验前需要对铁电极表面活化。在FeSO~4~溶液中加入几滴Fe~2~(SO~4~)~3~溶液，将铁电极浸泡一段时间，铁电极表面被刻蚀活化。检验活化反应完成的方法是\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。',
 '28．（14分）',
 '硫酸是一种重要的基本化工产品，接触法制硫酸生产中的关键工序是SO~2~的催化氧化：SO~2~(g)+O~2~(g) ![](./notebook/image/media/image29.png)SO~3~(g) ΔH=−98 kJ·mol^−1^。回答下列问题：\n（1）钒催化剂参与反应的能量变化如图(a)所示，V~2~O~5~(s)与SO~2~(g)反应生成VOSO~4~(s)和V~2~O~4~(s)的热化学方程式为：\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。',
 "![](./notebook/image/media/image30.png)\n（2）当SO~2~(g)、O~2~(g)和N~2~(g)起始的物质的量分数分别为7.5%、10.5%和82%时，在0.5MPa、2.5MPa和5.0MPa压强下，SO~2~平衡转化率α随温度的变化如图(b)所示。反应在5.0MPa、550℃时的α=\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_，判断的依据是\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。影响α的因素有\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。\n（3）将组成(物质的量分数)为2m% SO~2~(g)、m% O~2~(g)和q% N~2~(g)的气体通入反应器，在温度t、压强p条件下进行反应。平衡时，若SO~2~转化率为α，则SO~3~压强为\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_，平衡常数K~p~=\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_(以分压表示，分压=总压×物质的量分数)。\n（4）研究表明，SO~2~催化氧化的反应速率方程为：\nv=k(−1)^0.8^(1−nα\\')\n式中：k为反应速率常数，随温度t升高而增大；α为SO~2~平衡转化率，α\\'为某时刻SO~2~转化率，n为常数。在α\\'=0.90时，将一系列温度下的k、α值代入上述速率方程，得到v\\~t曲线，如图（c）所示。\n![](./notebook/image/media/image32.png)\n曲线上v最大值所对应温度称为该α\\'下反应的最适宜温度t~m~。t\\<t~m~时，v逐渐提高；t\\t~m~后，v逐渐下降。原因是\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_。\n（二）选考题：共45分。请考生从2道物理题、2道化学题、2道生物题中每科任选一题作答。如果多做，则每科按所做的第一题计分。",
 '35．\\[化学------选修3：物质结构与性质\\]（15分）\nGoodenough等人因在锂离子电池及钴酸锂、磷酸铁锂等正极材料研究方面的卓越贡献而获得2019年诺贝尔化学奖。回答下列问题：\n（1）基态Fe^2+^与Fe^3+^离子中未成对的电子数之比为\\_\\_\\_\\_\\_\\_\\_\\_\\_。\n（2）Li及其周期表中相邻元素的第一电离能（I~1~）如表所示。I~1~(Li)\\I~1~(Na)，原因是\\_\\_\\_\\_\\_\\_\\_\\_\\_。I~1~(Be)\\I~1~(B)\\I~1~(Li)，原因是\\_\\_\\_\\_\\_\\_\\_\\_。\n（3）磷酸根离子的空间构型为\\_\\_\\_\\_\\_\\_\\_，其中P的价层电子对数为\\_\\_\\_\\_\\_\\_\\_、杂化轨道类型为\\_\\_\\_\\_\\_\\_\\_。\n（4）LiFePO~4~的晶胞结构示意图如(a)所示。其中O围绕Fe和P分别形成正八面体和正四面体，它们通过共顶点、共棱形成空间链结构。每个晶胞中含有LiFePO~4~的单元数有\\_\\_\\_\\_个。\n![](./notebook/image/media/image33.png)\n电池充电时，LiFeO~4~脱出部分Li^+^，形成Li~1−x~FePO~4~，结构示意图如(b)所示，则x=\\_\\_\\_\\_\\_\\_\\_，n(Fe^2+^ )∶n(Fe^3+^)=\\_\\_\\_\\_\\_\\_\\_。',
 '36．\\[化学------选修5：有机化学基础\\]（15分）\n有机碱，例如二甲基胺（![](./notebook/image/media/image34.png)）、苯胺（![](./notebook/image/media/image35.png)），吡啶（![](./notebook/image/media/image36.png)）等，在有机合成中应用很普遍，目前"有机超强碱"的研究越来越受到关注，以下为有机超强碱F的合成路线：\n![](./notebook/image/media/image37.png)\n已知如下信息：\n①H~2~C=CH~2~![](./notebook/image/media/image39.png)\n②![](./notebook/image/media/image40.png)+RNH~2~![](./notebook/image/media/image42.png)\n③苯胺与甲基吡啶互为芳香同分异构体\n回答下列问题：\n（1）A的化学名称为\\_\\_\\_\\_\\_\\_\\_\\_。\n（2）由B生成C的化学方程式为\\_\\_\\_\\_\\_\\_\\_\\_。\n（3）C中所含官能团的名称为\\_\\_\\_\\_\\_\\_\\_\\_。\n（4）由C生成D的反应类型为\\_\\_\\_\\_\\_\\_\\_\\_。\n（5）D的结构简式为\\_\\_\\_\\_\\_\\_\\_\\_。\n（6）E的六元环芳香同分异构体中，能与金属钠反应，且核磁共振氢谱有四组峰，峰面积之比为6∶2∶2∶1的有\\_\\_\\_\\_\\_\\_\\_\\_种，其中，芳香环上为二取代的结构简式为\\_\\_\\_\\_\\_\\_\\_\\_。\n2020年普通高等学校招生全国统一考试\n理科综合 化学参考答案\n7．D 8．B 9．A 10．C 11．B 12．D 13．C\n26．（1）加快酸浸和氧化反应速率（促进氧化完全）\n（2）Fe^2+^ VO^+^+MnO~2~ +2H^+^ =+Mn^2+^+H~2~O\n（3）Mn^2+^ Al^3+^和Fe^3+^\n（4）Fe(OH)~3~\n（5）NaAl(OH)~4~+ HCl= Al(OH)~3~↓+NaCl+H~2~O\n（6）利用同离子效应，促进NH~4~VO~3~尽可能析出完全\n27．（1）烧杯、量筒、托盘天平\n（2）KCl\n（3）石墨\n（4）0.09 mol·L^−1^\n（5）Fe^3+^+e^−^=Fe^2+^ Fe−2e^−^= Fe^2+^ Fe^3+^ Fe\n（6）取少量溶液，滴入KSCN溶液，不出现血红色\n28．（1）2V~2~O~5~(s)+ 2SO~2~(g)=2VOSO~4~(s)+V~2~O~4~(s) ΔH =−351 kJ·mol^−1^\n（2）0.975 该反应气体分子数减少，增大压强，α提高。5.0MPa\\2.5MPa = p~2~，所以p~1~= 5.0Mpa 温度、压强和反应物的起始浓度（组成）\n（3）\n（4）升高温度，k增大使v逐渐提高，但α降低使v逐渐下降。t\\<t~m~时，k增大对v的提高大于α引起的降低； t\\t~m~后，k增大对v的提高小于α引起的降低\n35．（15分）\n（1）\n（2）Na与Li同族，Na电子层数多，原子半径大，易失电子\nLi、Be、B同周期，核电荷数依次增加。Be为1s^2^2s^2^全满稳定结构，第一电离能最大。与Li相比，B核电荷数大，原子半径小，较难失去电子，第一电离能较大。\n（3）正四面体 4 sp^3^\n（4）4 13∶3\n36．（15分）\n（1）三氯乙烯\n（2）![](./notebook/image/media/image48.png)\n（3）碳碳双键、氯原子\n（4）取代反应\n（5）![](./notebook/image/media/image49.png)\n（6）6 ![](./notebook/image/media/image50.png)\n![](./notebook/image/media/image51.jpeg)']
    # for row in find_continuous_sequence(test):
    #     # print()
    #     # print(row["question"])
    #     # print("-------------------------------------------------------")
    #     # print(f"{row['answer']}")
    #     # print()
    #     print(row)
    #     print("============================================================")

    print(find_answer_split_str(test))
