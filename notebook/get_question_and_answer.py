import re
from datasets import Features, Value

class Utility:
    
    def find_questions_and_answer_index(self, lines: list[str]) -> list[int]:
        indexes = []
        pattern = r"^\d+[\.|\．|、]"
        for index in range(len(lines)):
            match = re.search(pattern, lines[index].replace("\\",""))
            if match: 
                indexes.append(index)
        return indexes 

    def answer_count_total(self, lines, answer_keywords):
        question_indexes = self.find_questions_and_answer_index(lines)
        answer_count = 0
        for i, question_index in enumerate(question_indexes):
            if i+1 == len(question_indexes):
                break
            current_question = "".join(lines[question_index:question_indexes[i+1]])
            if any(keyword in current_question for keyword in answer_keywords):
                answer_count += 1
        return answer_count

    def extract_leading_number(self, line):
        match = re.search(r"^\d+[\.|\．|、]", line.replace("\\",""))
        if match:
            return match.group().rstrip('.').rstrip('．').rstrip('、')
        else:
            return None

    def has_equal_subsequences(self, question_number_list):
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

    def check_standard_paper_type(self, lines):
        question_indexes = self.find_questions_and_answer_index(lines)
        question_number_list = [self.extract_leading_number(lines[question_index]) for question_index in question_indexes]
        
        return self.has_equal_subsequences(question_number_list)

    def check_paper_type(self, text, answer_keywords=['答案']):
        lines = text.splitlines()
        answer_count = self.answer_count_total(lines, answer_keywords)
        question_indexes = self.find_questions_and_answer_index(lines)
        if answer_count > 0:
            if answer_count > len(question_indexes)/2:
                return 2
            elif self.check_standard_paper_type(lines):
                return 1
            else:
                return 0
        else:
            return -1
    
    def get_paper_question_by_number(self, question_indexes, lines):
        question_list = []
        for i, question_index in enumerate(question_indexes):
            if i+1 == len(question_indexes):
                question_list.append("".join(lines[question_indexes[i]:]))
            else:
                question_list.append("".join(lines[question_index:question_indexes[i+1]]))
        return question_list

class parse_type:
    FEATURES = Features(
        {
            "type": Value("int32"),
            "content": Value("string")
        }
    )

    def __init__(self):
        self.utility = Utility()

    def get_analysis(self, text):
        lines = text.splitlines()
        
        question_indexes = self.utility.find_questions_and_answer_index(lines)
        
        question_list = self.utility.get_paper_question_by_number(question_indexes, lines)

        return datasets.Dataset.from_dict({"type":[2]*len(question_list),"content":question_list})

    def alignment(self, question_list):
        question_and_answer = []
        for question in question_list:
            part = re.split(r'(?=\【答案】)', question, 1)
            question_and_answer.append({"question":part[0], "answer": part[1]})
        return question_and_answer

class standard_paper_type:

    def __init__(self):
        self.utility = Utility()

    def get_answer_area(self, text):
        lines = text.splitlines()
        for i in range(len(lines)):
            if bool(re.search(r'参考答案|试卷解析', lines[i])):
                return lines[i:]
        return None

    def get_analysis(self, lines):
        question_number = self.utility.find_questions_and_answer_index(lines)
        question_list = self.utility.get_paper_question_by_number(question_number, lines)
        return question_list

    def alignment(self, question_list):
        question_and_answer = []
        for question in question_list:
            part = re.split(r'(?=\【答案】)', question, 1)
            question_and_answer.append({"question":part[0], "answer": part[1]})
        return question_and_answer
