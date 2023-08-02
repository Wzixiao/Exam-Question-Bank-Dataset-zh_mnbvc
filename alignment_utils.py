import bisect
import re

GET_TOPIC_PATTERN = re.compile(r'^(\d+)[．.|(]|^(\\*[（(])\d+\\*[）)]|^\\*\d+\\\.|^\d+、')


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
    从给定的字符串中提取数字，它首先获取字符串的前两个字符，然后从中提取出数字字符，再将它们组合在一起。
    
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


def longest_increasing_subsequence_index(topics):
    """
    获取一个列表中的最长递增子序列的索引。首先，它从主题列表中提取数字，然后找到最长的递增子序列。
    
    参数:
        topics (list): 包含一系列题目的列表，这个题目列表应该是不完全正确的
        
    返回:
        list: 最长递增子序列的索引列表。
    """
    nums = [extract_and_combine_numbers(topic) for topic in topics]

    if not nums:
        return []

    n = len(nums)
    dp = [[i] for i in range(n)]
    max_length = 1
    max_index = 0

    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                # Check if the sequence is more contiguous by comparing the last index of the current sequence (j)
                # with the last index of the sequence that would be created by appending the current number (dp[i][-1])
                if len(dp[j]) + 1 > len(dp[i]) or (len(dp[j]) + 1 == len(dp[i]) and dp[j][-1] == dp[i][-1] - 1):
                    dp[i] = dp[j] + [i]

        if len(dp[i]) > max_length:
            max_length = len(dp[i])
            max_index = i

    return dp[max_index]


ANSWER_WORDS = ["答案", "参考答案", "试题解析", "参考解答", "答"]


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
        if any(answer_word in question for answer_word in ANSWER_WORDS):
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
    return None if len(splited_text) == 1 else splited_text[-1]


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
            matches = re.findall(r'(\d+)[．.|(]|（(\d+)）|\((\d+)\)|\d+\\.', line)
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

    matches = [m for m in re.finditer(re.compile(r'(\d+)[．.|\(]|（\d+）|\d+\\.|\d+、'), text)]
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
            start_match = re.search(r'^(\d+)[．.|\(]|（\d+）|\d+\\.|\d+、', text)
            if start_match:
                match_group = start_match.group()
            else:
                start_match = re.search(r'(\d+)[．.|\(]|（\d+）|\d+\\.|\d+、', text)
                match_group = start_match.group()

            start_number = int(re.search(r'\d+', match_group).group())  # 提取数字部分
            remaining_text = text[:specific_match.start()]  # 移除匹配部分后的剩余文本
            return text[specific_match.start():], remaining_text, start_number
    else:
        return None, None, None


def match_specific_from_start_by_lines(text, number):
    '''
    从文本的末尾开始，匹配特定的数字。

    Args:
        text (str): 需要匹配的文本。
        number (int): 需要匹配的数字。

    Returns:
        tuple: 返回一个元组，包含三个元素。
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
        match = re.search(pattern, text)

    if match:
        # Get the matched text
        matched_text = match.group(0)

        # Split the text into two parts at the matched text
        first_part, second_part = text.split(matched_text, 1)

        # Return the result as a dictionary
        return {
            "question": first_part.strip(),
            "answer": matched_text + second_part.strip()
        }
    else:
        # If no match found, return None
        return None


def align_answers_in_questions(questions: list, keywords: list = ANSWERS_KEY_WORDS_IN_QUESTIONS) -> list:
    return [split_text_by_keywords(question, keywords) for question in questions]


if __name__ == "__main__":
    test = """5．下列结论正确的是 （ ）',
 'A．当 B．',
 'C．的最小值为2 D．当无最大值',
 '![](./notebook/image/media/image22.emf)6．函数的图象如图，其中a、b为常数，则下列结论正确的是 （ ）"""

    # for row in align_answers_in_questions(test):
    #     print()
    #     print(row["question"])
    #     print("-------------------------------------------------------")
    #     print(f"{row['answer']}")
    #     print()
    #     print("============================================================")

    print(match_specific_from_start_by_lines(test, 6))
