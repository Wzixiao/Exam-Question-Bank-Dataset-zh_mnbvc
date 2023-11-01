from abc import ABC, abstractmethod
import re

class StandardExamParser(AbstractExamParser):
    def __init__(self, content):
        super().__init__(content)

    
    @staticmethod
    def detect_this_exam_type(content):
        lines = content.splitlines()
        question_indexes = StandardExamParser.find_questions_and_answer_indexes(lines)
        if len(question_indexes) == 0:
            return False
        question_number_list = [StandardExamParser.extract_leading_number(lines[question_index]) for question_index in question_indexes]
        return StandardExamParser.has_equal_subsequences(question_number_list)

    
    def extract_questions(self):
        lines = self.content.splitlines()
        all_question =  longest_increasing_subsequence_index(StandardExamParser.get_topic_number_super(lines))
        return [lines[question] for question in all_question]
    def extract_topic_details(self):
        topic_numbers_with_content = self.find_all_topic_numbers_with_content()
        topic_details = self.construct_complete_topic_details(topic_numbers_with_content)
        topic_details = self.find_most_concentrated_increasing_subsequence(topic_details)
        return topic_details
    
    def extract_answers(self):
        lines = self.content.splitlines()
        question_list, answer_str = StandardExamParser.find_all_topic_numbers_with_content(lines)
        joined_questions = "".join(question_list[-1]['content'])
        answer_list = []
        if answer_str in joined_questions:
            # 分割字符串，获取 answer_str 右边的内容
            answer_right_side = joined_questions.split(answer_str, 1)[1]
            answer_number = 1
            while(True):
                answer = find_answer_by_number(answer_right_side, answer_number)
                if answer is not None:
                    answer_list.append(answer)
                    answer_number = answer_number + 1
                else:
                    return answer_list
        else:
            return []
        
 
    def align(self):
        pass
    
    @staticmethod
    def find_answer_by_number(text, number):
        # 将数字转换为字符串
        number_str = str(number)
        next_number_str = str(number + 1)

        # 构建正则表达式：匹配特定的题号到下一个题号之前的所有内容
        # 注意这里使用了非贪婪匹配.*?和对下一题号的前瞻(?=\d+\.)
        pattern = re.compile(rf'({number_str}．).*?(?={next_number_str}．|\Z)', re.DOTALL)

        match = pattern.search(text)
        if match:
            # 匹配到的文本是当前题号到下一个题号之间的内容
            matched_text = match.group(0)
            # 剩余的文本是从头到当前题号之前的内容
            rest_text = text[:match.start()]
            return matched_text

        return None

    @staticmethod
    def extract_number_from_string(input_string):
        pattern = r"(\d+(\.\d+)*)"  # 匹配一个或多个数字和可选的小数点
        match = re.search(pattern, input_string)
        if match:
            number_str = match.group(1)  # 获取匹配的数字部分
            return int(float(number_str))  # 将数字部分转换为浮点数，然后再转换为整数
        return None 
    
    @staticmethod
    def get_paper_question_by_number(question_indexes, lines):
        question_list = []
        answer_words = ["答案", "参考答案", "试题解析", "参考解答"]
        answer_area_str = ""
        for i, question_index in enumerate(question_indexes):
            if i+1 == len(question_indexes):
                question_list.append("".join(lines[question_indexes[i]:]))
                for line in lines[question_indexes[i]:]:
                    if any(answer_word in line for answer_word in answer_words):
                        answer_area_str = line
                        break
            else:
                question_list.append("".join(lines[question_index:question_indexes[i+1]]))

        return question_list,answer_area_str
    @staticmethod
    def extract_number(s):
        match = re.search(r'(\d+)', s)
        return int(match.group(1)) if match else None
    @staticmethod
    def has_equal_subsequences(lst):
        def get_subsequences(lst):
            subs = []
            temp = [lst[0]]

            i = 1
            while i < len(lst):
                expected_next = str(StandardExamParser.extract_number(temp[-1]) + 1)
                if lst[i] == expected_next:  # Continuation found
                    temp.append(lst[i])
                    i += 1
                else:  # Not continuous, but check if the next expected is coming up later
                    if expected_next in lst[i:i+5]:  # Look ahead up to 5 elements to find the next continuation
                        next_index = lst[i:i+5].index(expected_next) + i
                        temp.append(lst[next_index])
                        i = next_index + 1
                    else:  # No continuation found soon enough, so reset
                        subs.append(temp)
                        temp = [lst[i]]
                        i += 1
            if temp:
                subs.append(temp)

            subs.sort(key=len, reverse=True)
            return subs

        subsequences = get_subsequences(lst)
        if len(subsequences) != 2:
            return False
        return subsequences[0]==subsequences[1]

    @staticmethod
    def extract_leading_number(line):
        match = re.search(r"^\d+[\.|\．|、]", line.replace("\\",""))
        if match:
            return match.group().rstrip('.').rstrip('．').rstrip('、')
        else:
            return None
    
    @staticmethod
    def get_topic_number_super(lines: list[str]) -> list[super]:
        """
        获取题目和答案的lines下标

        判断行的开始是否为 数字+[. ．]
        """
        question_nums = []
        question_num_indexs = []
        pattern = r"^(\d+)[\.|\．|、]"
        for index in range(len(lines)):
            match = re.search(pattern, lines[index].replace("\\",""))
            if match: 
                question_number = match.group(1)
                question_nums.append(question_number)
                question_num_indexs.append(index)
        return [(int(x), y) for x, y in zip(question_nums, question_num_indexs)]
    
    @staticmethod
    def find_questions_and_answer_indexes(lines: list[str]) -> list[int]:
        indexes = []
        pattern = r"^\d+[\.|\．|、]"
        for index in range(len(lines)):
            match = re.search(pattern, lines[index].replace("\\",""))
            if match: 
                indexes.append(index)
        return indexes 
    
    @staticmethod
    def find_all_topic_numbers_with_content(lines):
        """
        获取标准试卷答案区
        返回每题答案的集合
        """
        question_number_indexs = longest_increasing_subsequence_index(StandardExamParser.get_topic_number_super(lines))
        question_list,answer_area_str = StandardExamParser.get_paper_question_by_number(question_number_indexs, lines)
        new_question_list = []
        for question in question_list:
            new_question_list.append({"topic_number":StandardExamParser.extract_number_from_string(question), "content": question})
        return StandardExamParser.construct_complete_topic_details(new_question_list),answer_area_str