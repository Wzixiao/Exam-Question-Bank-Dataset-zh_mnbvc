from .abstract_exam_parser import AbstractExamParser
import re

class AnnotatedExamParser(AbstractExamParser):
    def __init__(self, content):
        super().__init__(content)
        # self.content = content

    @staticmethod
    def detect_this_exam_type(content):
        lines = content.splitlines()
        answer_count = AbstractExamParser.answer_count_total(lines)
        question_indexes = AbstractExamParser.find_questions_and_answer_indexes(lines)
        return answer_count > len(question_indexes) / 2

    def extract_questions(self):
        lines = self.content.splitlines()
        topic_numbers = self.find_all_topic_numbers_with_content(lines)
        print(topic_numbers)
        return AnnotatedExamParser.get_paper_question_by_number(question_indexes, lines)
    
    def extract_answers(self):
        answers = []
        for question in self.questions:
            pattern_arr_str = "|".join(f"【{tag}】" for tag in AnnotatedExamParser.answer_keywords)
            regex_pattern = rf"(?={pattern_arr_str})"
            part = re.split(regex_pattern, question, 1)
            answers.append(part[1])
            
        return answers

    def align(self):
        if len(self.questions) != len(self.answers):
            raise ValueError("题目和答案长度不一致")

        return [{"question": q.replace(a, ''), "answer": a} for q, a in zip(self.questions, self.answers)]

    @staticmethod
    def get_paper_question_by_number(question_indexes, lines):
        question_list = []
        for i, question_index in enumerate(question_indexes):
            if i+1 == len(question_indexes):
                question_list.append("".join(lines[question_indexes[i]:]))
            else:
                question_list.append("".join(lines[question_index:question_indexes[i+1]]))

        return question_list

    def find_all_topic_numbers_with_content(self, lines=None):
        """
        根据给定的文本行列表，提取出所有的题目序号及其对应的文本内容。
        
        参数:
            lines (list): 包含题目的文本行列表。
        
        返回:
            list: 返回一个字典列表，每个字典包含"topic_number"和对应的文本内容。
            
        示例:
            输入: ['1. 问题描述...', '解析...', '2. 问题描述...', '解析...']
            输出: [{'topic_number': 1, 'content': '1. 问题描述...解析...'}, {'topic_number': 2, 'content': '2. 问题描述...解析...'}]
        """
        if not lines:
            lines = self.content.spltlines()
    
        pattern = rf"^\d+{'[' + '|'.join(self.topic_number_keywords) + ']'}"
 
        topic_details = []
        start_index = None
        topic_number = None

        for index, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                if start_index is not None:
                    topic_details.append({"topic_number": topic_number, "content": ''.join(lines[start_index:index])})
                start_index = index
                topic_number = int(match.group().strip('.').strip('．').strip('、'))

        if start_index is not None:
            topic_details.append({"topic_number": topic_number, "content": ''.join(lines[start_index:])})

        return AbstractExamParser.construct_complete_topic_details(topic_details)
        
    @staticmethod
    def longest_increasing_subsequence_index(nums):
        n = len(nums)
        dp = [[i] for i in range(n)]
    
        for i in range(n):
            for j in range(i):
                if nums[j][0] < nums[i][0]:
                    if len(dp[j]) + 1 > len(dp[i]) or (len(dp[j]) + 1 == len(dp[i]) and dp[j][-1] == dp[i][-1] - 1):
                        dp[i] = dp[j] + [i]
    
        dp = list(filter(lambda lis: nums[lis[0]][1] < len(nums) / 2, dp))
        dp = sorted(dp, key=lambda lis: len(lis), reverse=True)
        return [nums[i][1] for i in dp[0]]
        
    @staticmethod
    def find_most_concentrated_increasing_subsequence(topic_details):
        nums = [(detail['topic_number'], idx) for idx, detail in enumerate(topic_details)]
        
        # Get the indices of the longest increasing subsequence
        lis_indices = longest_increasing_subsequence_index(nums)
    
        # Extract the subsequence from the topic_details using the indices
        return [topic_details[idx] for idx in lis_indices]
    
    @staticmethod
    def construct_complete_topic_details(topic_details):
        """
        根据题目详情列表构建完整的题目详情列表，处理非连续的题目编号。
        
        参数:
            topic_details (list): 原始题目详情列表
            
        返回:
            list: 完整的题目详情列表
        """
        complete_topic_details = []

        for index, detail in enumerate(topic_details):
            topic_number = detail["topic_number"]
            content = detail["content"]

            # 如果是最后一个元素
            if index == len(topic_details) - 1:
                complete_topic_details.append(detail)
                break

            next_topic_number = topic_details[index+1]["topic_number"]

            # 处理连续的题目编号
            if topic_number + 1 == next_topic_number:
                complete_topic_details.append(detail)
                continue

            # 处理非连续的题目编号
            while topic_number < next_topic_number:
                # 分割当前内容
                before_topic_content, after_topic_content = AbstractExamParser.split_topic_details_content(content, topic_number + 1)

                # 将当前题目内容添加到完整列表中
                complete_topic_details.append({"topic_number": topic_number, "content": before_topic_content})

                # 如果后续没有内容，则退出循环
                if not after_topic_content:
                    break

                # 否则，增加题目编号并设置下一次迭代的内容
                topic_number += 1
                content = after_topic_content

        return complete_topic_details
    
 
