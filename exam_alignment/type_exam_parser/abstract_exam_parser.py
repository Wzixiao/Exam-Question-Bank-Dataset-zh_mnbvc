from abc import ABC, abstractmethod
import re

class AbstractExamParser(ABC):
    answer_keywords=["答案"]

    def __init__(self, content):
        self.content = content
        self.questions = self.extract_questions()
        self.answers = self.extract_answers() 

    @staticmethod
    @abstractmethod
    def detect_this_exam_type(content):
        """
        检测试卷的类型是否为此类。
        
        此方法应该分析试卷的内容，识别并返回试卷的具体类型。
        
        返回:
            bool: 是否为当前类可以解析的类型
        """
        pass

    @abstractmethod
    def extract_questions(self):
        """
        提取试卷中的题目。
        
        此方法应该从试卷内容中提取出所有的题目。
        
        返回:
            list: 包含所有题目，每个元素是一个question。
        """
        pass

    @abstractmethod
    def extract_answers(self):
        """
        提取试卷中的答案。
        
        此方法应该从试卷内容中提取出所有的答案。
        
        返回:
            list: 包含所有答案，每个元素是一个answer。
        """
        pass

    @abstractmethod
    def align(self):
        """
        对齐试卷的题目和答案。
        
        此方法应该确保每个题目与其对应的答案正确对齐，以便于阅卷或其他处理。
        
        返回:
            None
        """
        pass
    
    @staticmethod
    def check_contains_answers(content):
        """检测试卷是否存在答案"""
        """Todo: 不完整"""
        lines = content.splitlines()
        answer_count = AbstractExamParser.answer_count_total(lines)
        return answer_count > 0
    
    @staticmethod
    def answer_count_total(lines):
        question_indexes = AbstractExamParser.find_questions_and_answer_indexes(lines)
        answer_count = 0
        for i, question_index in enumerate(question_indexes):
            if i+1 == len(question_indexes):
                break

            current_question = "".join(lines[question_index:question_indexes[i+1]])
            if any(keyword in current_question for keyword in AbstractExamParser.answer_keywords):
                answer_count += 1

        return answer_count
    
    @staticmethod
    def find_questions_and_answer_indexes(lines: list[str]) -> list[int]:
        indexes = []
        pattern = r"^\d+[\.|\．|、]"
        for index in range(len(lines)):
            match = re.search(pattern, lines[index].replace("\\",""))
            if match: 
                indexes.append(index)
        return indexes 
    
  