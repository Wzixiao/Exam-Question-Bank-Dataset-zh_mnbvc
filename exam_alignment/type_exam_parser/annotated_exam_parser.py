from .abstract_exam_parser import AbstractExamParser
import re

class AnnotatedExamParser(AbstractExamParser):
    def __init__(self, content):
        super().__init__(content)

    @staticmethod
    def detect_this_exam_type(content):
        lines = content.splitlines()
        answer_count = AbstractExamParser.answer_count_total(lines)
        question_indexes = AbstractExamParser.find_questions_and_answer_indexes(lines)
        return answer_count > len(question_indexes) / 2

    def extract_questions(self):
        lines = self.content.splitlines()
        question_indexes = self.find_questions_and_answer_indexes(lines)
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

    
 
