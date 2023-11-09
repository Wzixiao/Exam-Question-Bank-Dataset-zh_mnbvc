import argparse
import json
import os
import glob
from pathlib import Path
import re

from exam_alignment.utils.alignment_utils import one_file_per_process
from exam_alignment.utils.alignment_utils import extract_and_combine_numbers
from exam_alignment.utils.alignment_utils import extract_and_combine_numbers_in_not_start
from exam_alignment.utils.alignment_utils import longest_increasing_subsequence_index
from exam_alignment.utils.alignment_utils import find_answer_split_str
from exam_alignment.utils.alignment_utils import find_next_question_index
from exam_alignment.utils.alignment_utils import refine_answers
from exam_alignment.utils.alignment_utils import match_specific_from_end
from exam_alignment.utils.alignment_utils import answer_area_str_process
from exam_alignment.utils.alignment_utils import generate_answer_area_string
from exam_alignment.utils.alignment_utils import align_answers_in_questions
from exam_alignment.utils.alignment_utils import match_specific_from_start
from exam_alignment.utils.alignment_utils import type_of_judgment
from exam_alignment.utils.alignment_utils import split_question
from exam_alignment.utils.alignment_utils import find_continuous_sequence
from exam_alignment.utils.alignment_utils import extract_and_combine_numbers_in_not_start_by_number



from exam_alignment.exam_parser_container import ExamParserContainer


def process(md_text: str, file_local: Path, output_local: Path):
    examParserContainer = ExamParserContainer(md_text)
    exam_parser = examParserContainer.get_exam_parser()

    if not exam_parser:
        # print(f"无法检测 '{file_local.name}' 的类型")
        return
    
    try:
        align_qustion = exam_parser.align()
    except:
        # print(f"'{file_local.name}' 对齐失败")
        return

    if not align_qustion:
        # print(f"'{file_local.name}' 对齐失败")
        return
  
    for qustion_with_answer in align_qustion:
        with open(output_local, "a") as f:
            f.write(f"{json.dumps(qustion_with_answer)}\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True, help="输入目录, 包含md文档的文件夹")
    parser.add_argument('--output_file', type=str, required=True, help="输出文件, jsonl格式")

    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_local = Path(args.output_file)

    for file in input_path.glob("**/*.md"):
        with open(file, "r", encoding="utf-8") as f:
            md_text = one_file_per_process(f.read())
            process(md_text, file, output_local)
