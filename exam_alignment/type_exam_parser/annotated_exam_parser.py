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
        
    
 
