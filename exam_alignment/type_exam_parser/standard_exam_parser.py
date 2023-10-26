from .abstract_exam_parser import AbstractExamParser
import re

class StandardExamParser(AbstractExamParser):
    def __init__(self, content):
        super().__init__(content)

    @staticmethod
    def detect_this_exam_type(content):
        lines = content.splitlines()
        question_indexes = StandardExamParser.find_questions_and_answer_indexes(lines)
        question_number_list = [StandardExamParser.extract_leading_number(lines[question_index]) for question_index in question_indexes]
        return StandardExamParser.has_equal_subsequences(question_number_list)

    def extract_questions(self):
        pass


    def extract_answers(self):
        pass

 
    def align(self):
        pass


    @staticmethod
    def has_equal_subsequences(question_number_list):
        first_element = question_number_list[0]
        split_index = -1
        for i in range(1, len(question_number_list)):
            if question_number_list[i] == first_element:
                split_index = i
                break

        if split_index == -1:
            return False
        
        first_subseq = question_number_list[:split_index]
        second_subseq = question_number_list[split_index:]

        return first_subseq == second_subseq

    @staticmethod
    def extract_leading_number(line):
        match = re.search(r"^\d+[\.|\．|、]", line.replace("\\",""))
        if match:
            return match.group().rstrip('.').rstrip('．').rstrip('、')
        else:
            return None
    