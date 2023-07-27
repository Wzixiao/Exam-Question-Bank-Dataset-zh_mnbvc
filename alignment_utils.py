import bisect
import re


GET_TOPIC_PATTERN = re.compile(r'^(\d+)[．.|\(]|^[（(]\d+[）)]|^\d+\\\.|^\d+、')

def one_file_per_process(text):
    """
    接受一个可能包含多行的文本字符串，将其拆分为行，去除每一行中的某些特定字符，移除空行，然后将清理后的行重新组合成一个单一的字符串。
    
    参数:
        text (str): 可以包含多行的文本字符串。
        
    返回:
        str: 每一行都已经被清理和重新组装的文本字符串。
    """

    liens = text.splitlines()
    liens = map(lambda x: x.replace("> ","").replace(">","").replace("*", "").replace("\u3000", ""), liens)
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


ANSWER_WORDS = ["解析", "答案", "分析", "详解", "试题解析", "参考解答"]


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
    
    for index in range(start+1, len(lines)):
        match = GET_TOPIC_PATTERN.match(lines[index])
        
        if match:
            return index

    return len(lines)


def generate_answer_area_string(text:str, split_str):
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
            next_topic_number = extract_and_combine_numbers(reversed_answers[index+1])
        
        # 获取当前答案对应的题目序号
        current_topic_number = extract_and_combine_numbers(current_answer)
        
        # 从答案的末尾开始查找，尝试匹配题目序号+1的答案
        previous_answer, remaining_text, start_number = match_specific_from_end(current_answer, current_topic_number+1)
        
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


ANSWERS_KEY_WORDS_IN_QUESTIONS = {"答案"}


def split_text_by_keywords(text: str, keywords: list) -> dict:
    # 创建正则表达式模式
    pattern = f"【({'|'.join(keywords)})】"
    
    # 使用正则表达式模式分割文本
    split_text = re.split(pattern, text)
    
    # 准备一个列表来存储分割的结果
    keyword_splits = []

    # 遍历分割后的文本，将其添加到列表中
    for i in range(0, len(split_text), 2):
        keyword_splits.append(split_text[i].rstrip('\n'))
        if i+1 < len(split_text):
            keyword_splits.append("【" + split_text[i+1] + "】" + split_text[i + 2].lstrip('\n'))

    # 如果列表中有多于2个元素，我们将最后两个元素合并
    if len(keyword_splits) > 2:
        keyword_splits[-2] = keyword_splits[-2] + keyword_splits[-1]
        keyword_splits.pop()

    question = keyword_splits[0]
    answer = None

    if len(keyword_splits) != 1:
        answer = keyword_splits[1]

    return {
        "question": question,
        "answer": answer
    }

def align_answers_in_questions(questions: list, keywords: list = ANSWERS_KEY_WORDS_IN_QUESTIONS) -> list:
    return [split_text_by_keywords(question, keywords) for question in questions]



if __name__ == "__main__":
    test = ['1.下列各数中比小的数是（ ）\nA. B. C. D.\n【答案】A\n【解析】\n【分析】\n先根据正数都大于0，负数都小于0，可排除C、D，再根据两个负数，绝对值大的反而小，可得比-2小的数是-3．\n【详解】∵\\|-3\\|=3，\\|-1\\|=1，\n又0＜1＜2＜3，\n∴-3＜-2，\n所以，所给出的四个数中比-2小的数是-3，\n故选：A\n【点睛】本题考查了有理数的大小比较，其方法如下：（1）负数＜0＜正数；（2）两个负数，绝对值大的反而小．',
 '2.计算的结果是（ ）\nA. B. C. D.\n【答案】C\n【解析】\n【分析】\n先处理符号，化为同底数幂的除法，再计算即可．\n【详解】解：\n故选C．\n【点睛】本题考查的是乘方符号的处理，考查同底数幂的除法运算，掌握以上知识是解题的关键．',
 '3.下列四个几何体中，主视图为三角形的是\nA. ![](./notebook/image/media/image14.png) B. ![](./notebook/image/media/image15.png) C. ![](./notebook/image/media/image16.png) D. ![](./notebook/image/media/image17.png)\n【答案】A\n【解析】\n试题分析：主视图是从物体正面看，所得到的图形．\nA、圆锥的主视图是三角形，符合题意；\nB、球的主视图是圆，不符合题意；\nC、圆柱的主视图是长方形，不符合题意；\nD、正方体的主视图是正方形，不符合题意.\n故选A．\n考点: 简单几何体的三视图．',
 '4.安徽省计划到2022年建成亩高标准农田，其中用科学记数法表示为（ ）\nA. 0![](./notebook/image/media/image19.wmf)547 B. C. D.\n【答案】D\n【解析】\n【分析】\n根据科学记数法的表示方法对数值进行表示即可．\n【详解】解：54700000=5.47×10^7^，\n故选：D．\n【点睛】本题考查了科学记数法，掌握科学记数法的表示方法是解题关键．',
 '5.下列方程中，有两个相等实数根的是（ ）\nA. B.\nC. D.\n【答案】A\n【解析】\n【分析】\n根据根的判别式逐一判断即可．\n【详解】A.变形为，此时△=4-4=0，此方程有两个相等的实数根，故选项A正确；\nB.中△=0-4=-4＜0，此时方程无实数根，故选项B错误；\nC.整理为，此时△=4+12=16＞0，此方程有两个不相等的实数根，故此选项错误；\nD.中，△=4＞0，此方程有两个不相等的实数根，故选项D错误.\n故选：A.\n【点睛】本题主要考查根的判别式，熟练掌握根的情况与判别式间的关系是解题的关键．',
 '6.冉冉的妈妈在网上销售装饰品．最近一周， 每天销售某种装饰品的个数为：．关于这组数据，冉冉得出如下结果，其中错误的是（ ）\nA. 众数是 B. 平均数是 C. 方差是 D. 中位数是\n【答案】D\n【解析】\n【分析】\n分别根据众数、平均数、方差、中位数的定义判断即可．\n【详解】将这组数据从小到大的顺序排列：10,11,11,11,13,13,15，\nA．这组数据的众数为11，此选项正确，不符合题意；\nB．这组数据的平均数为（10+11+11+11+13+13+15）÷7=12，此选项正确，不符合题意；\nC．这组数据的方差为=，此选项正确，不符合题意；\nD．这组数据的中位数为11，此选项错误，符合题意，\n故选：D．\n【点睛】本题考查了众数、平均数、方差、中位数，熟练掌握他们的意义和计算方法是解答的关键．',
 '7.已知一次函数的图象经过点，且随的增大而减小，则点的坐标可以是（ ）\nA. B. C. D.\n【答案】B\n【解析】\n【分析】\n先根据一次函数的增减性判断出k的符号，再将各项坐标代入解析式进行逐一判断即可．\n【详解】∵一次函数的函数值随的增大而减小，\n∴k﹤0，\nA．当x=-1，y=2时，-k+3=2，解得k=1﹥0，此选项不符合题意；\nB．当x=1，y=-2时，k+3=-2,解得k=-5﹤0，此选项符合题意；\nC．当x=2，y=3时，2k+3=3，解得k=0，此选项不符合题意；\nD．当x=3，y=4时，3k+3=4，解得k=﹥0，此选项不符合题意，\n故选：B．\n【点睛】本题考查了一次函数的性质、待定系数法，熟练掌握一次函数图象上点的坐标特征是解答的关键．',
 '8.如图，中， ，点在上，．若，则的长度为（ ）\n![](./notebook/image/media/image52.png)\nA. B. C. D.\n【答案】C\n【解析】\n【分析】\n先根据，求出AB=5，再根据勾股定理求出BC=3，然后根据，即可得cos∠DBC=cosA=，即可求出BD．\n【详解】∵∠C=90°，\n∴，\n∵，\n∴AB=5，\n根据勾股定理可得BC==3，\n∵，\n∴cos∠DBC=cosA=，\n∴cos∠DBC==，即=\n∴BD=，\n故选：C．\n【点睛】本题考查了解直角三角形和勾股定理，求出BC的长是解题关键．',
 '9.已知点在上．则下列命题为真命题的是（ ）\nA. 若半径平分弦．则四边形是平行四边形\nB. 若四边形是平行四边形．则\nC. 若．则弦平分半径\nD. 若弦平分半径．则半径平分弦\n【答案】B\n【解析】\n【分析】\n根据圆的有关性质、垂径定理及其推论、特殊平行四边形的判定与性质依次对各项判断即可．\n![](./notebook/image/media/image68.wmf)详解】A．∵半径平分弦，\n∴OB⊥AC，AB=BC，不能判断四边形OABC是平行四边形，\n假命题；\nB．∵四边形是平行四边形,且OA=OC,\n∴四边形是菱形，\n∴OA=AB=OB，OA∥BC，\n∴△OAB是等边三角形，\n∴∠OAB=60º,\n∴∠ABC=120º,\n真命题；\nC．∵，\n∴∠AOC=120º，不能判断出弦平分半径，\n假命题；\nD．只有当弦垂直平分半径时，半径平分弦，所以是\n假命题，\n故选：B．\n【点睛】本题主要考查命题与证明，涉及垂径定理及其推论、菱形的判定与性质、等边三角形的判定与性质等知识，解答的关键是会利用所学的知识进行推理证明命题的真假．',
 '10.如图和都是边长为的等边三角形，它们的边在同一条直线上，点，重合，现将沿着直线向右移动，直至点与重合时停止移动．在此过程中，设点移动的距离为，两个三角形重叠部分的面积为，则随变化的函数图像大致为（ ）\n![](./notebook/image/media/image78.png)\nA. ![](./notebook/image/media/image79.png) B. ![](./notebook/image/media/image80.png)\nC. ![](./notebook/image/media/image81.png) D. ![](./notebook/image/media/image82.png)\n【答案】A\n【解析】\n【分析】\n根据图象可得出重叠部分三角形的边长为x,根据特殊角三角函数可得高为,由此得出面积y是x的二次函数,直到重合面积固定,再往右移动重叠部分的边长变为(4－x),同时可得\n【详解】C点移动到F点,重叠部分三角形的边长为x,由于是等边三角形,则高为,面积为y=x··=,\nB点移动到F点,重叠部分三角形的边长为(4－x),高为,面积为\ny=(4－x)··=,\n两个三角形重合时面积正好为.\n由二次函数图象的性质可判断答案为A,\n故选A.\n【点睛】本题考查三角形运动面积和二次函数图像性质,关键在于通过三角形面积公式结合二次函数图形得出结论.\n二、填空题(本大题共4小题，每小题5分，满分20分)',
 '11.计算：=\\_\\_\\_\\_\\_\\_.\n【答案】2\n【解析】\n![](./notebook/image/media/image68.wmf)分析】\n根据算术平方根的性质即可求解.\n【详解】=3-1=2.\n故填：2.\n【点睛】此题主要考查实数的运算，解题的关键是熟知算术平方根的性质.',
 '12.分解因式：=\\_\\_\\_\\_\\_\\_．\n【答案】a（b+1）（b﹣1）．\n【解析】\n【详解】解：原式==a（b+1）（b﹣1），\n故答案为a（b+1）（b﹣1）．',
 '13.如图，一次函数的图象与轴和轴分别交于点和点与反比例函数上的图象在第一象限内交于点轴，轴，垂足分别为点，当矩形与的面积相等时，的值为\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_．\n![](./notebook/image/media/image100.png)\n【答案】\n【解析】\n【分析】\n根据题意由反比例函数的几何意义得：再求解的坐标及建立方程求解即可．\n【详解】解： 矩形，在上，\n把代入：\n把代入：\n由题意得：\n解得：（舍去）\n故答案为：\n【点睛】本题考查的是一次函数与反比例函数的性质，掌握反比例函数中的几何意义，一次函数与坐标轴围成的三角形面积的计算是解题的关键．',
 '14.在数学探究活动中，敏敏进行了如下操作：如图，将四边形纸片沿过点的直线折叠，使得点落在上的点处，折痕为；再将分别沿折叠，此时点落在上的同一点处．请完成下列探究：\n的大小为\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_；\n当四边形是平行四边形时的值为\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_．\n![](./notebook/image/media/image131.png)\n【答案】 (1). 30 (2).\n【解析】\n【分析】\n（1）根据折叠得到∠D+∠C=180°，推出AD∥BC，，进而得到∠AQP=90°，以及∠A=180°-∠B=90°，再由折叠，得到∠DAQ=∠BAP=∠PAQ=30°即可；\n（2）根据题意得到DC∥AP，从而证明∠APQ=∠PQR，得到QR=PR和QR=AR，结合（1）中结论，设QR=a，则AP=2a，由勾股定理表达出AB=AQ=即可解答．\n【详解】解：（1）由题意可知，∠D+∠C=180°，\n∴AD∥BC，\n由折叠可知∠AQD=∠AQR，∠CQP=∠PQR，\n∴∠AQR+∠PQR=，即∠AQP=90°，\n∴∠B=90°，则∠A=180°-∠B=90°，\n由折叠可知，∠DAQ=∠BAP=∠PAQ，\n∴∠DAQ=∠BAP=∠PAQ=30°，\n故答案为：30；\n（2）若四边形APCD为平行四边形，则DC∥AP，\n∴∠CQP=∠APQ，\n由折叠可知：∠CQP=∠PQR，\n∴∠APQ=∠PQR，\n∴QR=PR，\n同理可得：QR=AR，即R为AP的中点，\n由（1）可知，∠AQP=90°，∠PAQ=30°，且AB=AQ，\n设QR=a，则AP=2a，\n∴QP=，\n∴AB=AQ=，\n∴，\n故答案为：．\n【点睛】本题考查了四边形中的折叠问题，涉及了平行四边形的性质，勾股定理等知识点，解题的关键是读懂题意，熟悉折叠的性质．\n三、解答题',
 '15.解不等式：\n【答案】\n【解析】\n【分析】\n根据解不等式的方法求解即可．\n【详解】解：\n．\n【点睛】此题主要考查不等式的求解，解题的关键是熟知其解法．',
 '16.如图1，在由边长为个单位长度的小正方形组成的网格中，给出了以格点(网格线的交点)为端点的线段，线段在网格线上，\n画出线段关于线段所在直线对称的线段 (点分别为的对应点)；\n将线段，绕点，顺时针旋转得到线段，画出线段．\n![](./notebook/image/media/image150.png)\n【答案】（1）见解析；（2）见解析．\n【解析】\n【分析】\n（1）先找出A，B两点关于MN对称的点A~1~，B~1~，然后连接A~1~B~1~即可；\n（2）根据旋转的定义作图可得线段B~1~A~2~．\n【详解】（1）如图所示，即为所作；\n![](./notebook/image/media/image151.png)\n（2）如图所示，即为所作．\n【点睛】本题主要考查作图-旋转与轴对称，解题的关键是掌握旋转变换和轴对称的定义与性质．\n四、解答题',
 '17.观察以下等式：\n第1个等式：\n第个等式：\n第3个等式：\n第个等式：\n第5个等式：\n······\n按照以上规律．解决下列问题：\n写出第个等式\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_；\n写出你猜想的第个等式： [ ]{.underline} (用含的等式表示)，并证明．\n【答案】（1）；（2），证明见解析．\n【解析】\n【分析】\n（1）根据前五个个式子的规律写出第六个式子即可；\n（2）观察各个式子之间的规律，然后作出总结，再根据等式两边相等作出证明即可．\n【详解】（1）由前五个式子可推出第6个等式为：；\n（2），\n证明：∵左边==右边，\n∴等式成立．\n【点睛】本题是规律探究题，解答过程中，要注意各式中相同位置数字的变化规律，并将其用代数式表示出来．',
 '18.如图，山顶上有一个信号塔，已知信号塔高米，在山脚下点处测得塔底的仰角，塔顶的仰角．求山高(点在同一条竖直线上)．\n(参考数据： )\n![](./notebook/image/media/image168.png)\n【答案】75米\n【解析】\n【分析】\n设山高CD=x米，先在Rt△BCD中利用三角函数用含x的代数式表示出BD，再在Rt△ABD中，利用三角函数用含x的代数式表示出AD，然后可得关于x的方程，解方程即得结果．\n【详解】解：设山高CD=x米，则在Rt△BCD中，，即，\n∴，\n在Rt△ABD中，，即，\n∴，\n∵AD－CD=15，\n∴1.2x－x=15，解得：x=75．\n∴山高CD=75米．\n【点睛】本题考查了解直角三角形的应用，属于常考题型，正确理解题意、熟练掌握三角函数的知识是解题的关键．\n五、解答题',
 '19.某超市有线上和线下两种销售方式．与2019年4月份相比．该超市2020年4月份销售总额增长其中线上销售额增长．线下销售额增长，\n设2019年4月份的销售总额为元．线上销售额为元，请用含的代数式表示2020年4月份的线下销售额(直接在表格中填写结果)；\n![](./notebook/image/media/image180.png)\n求2020年4月份线上销售额与当月销售总额的比值．\n【答案】；\n【解析】\n【分析】\n根据增长率的含义可得答案；\n由题意列方程求解即可得到比值．\n【详解】解：年线下销售额为元，\n故答案为：．\n由题意得：\n2020年4月份线上销售额与当月销售总额的比值为：\n答：2020年4月份线上销售额与当月销售总额的比值为：\n【点睛】本题考查的列代数式及一元一次方程的应用，掌握列一元一次方程解决应用题是解题的关键．',
 '20.如图，是半圆的直径，是半圆上不同于的两点与相交于点是半圆所任圆的切线，与的延长线相交于点，\n求证：；\n若求平分．\n![](./notebook/image/media/image195.png)\n【答案】证明见解析；证明见解析．\n【解析】\n【分析】\n利用证明利用![](./notebook/image/media/image198.wmf)直径，证明结合已知条件可得结论；\n利用等腰三角形的性质证明： 再证明 利用切线的性质与直径所对的圆周角是直角证明： 从而可得答案．\n【详解】证明：\n为直径，\n．\n证明：\n为半圆的切线，\n平分．\n【点睛】本题考查的是圆的基本性质，弧，弦，圆心角，圆周角之间的关系，直径所对的圆周角是直角，三角形的全等的判定，切线的性质定理，三角形的内角和定理，掌握以上知识是解题的关键．\n六、解答题',
 '21.某单位食堂为全体名职工提供了四种套餐，为了解职工对这四种套餐的喜好情况，单位随机抽取名职工进行"你最喜欢哪一种套餐（必选且只选一种）"问卷调查，根据调查结果绘制了条形统计图和扇形统计图，部分信息如下：\n![](./notebook/image/media/image223.png)\n在抽取的人中最喜欢套餐的人数为 [ ]{.underline} ，扇形统计图中""对应扇形的圆心角的大小为 [ ]{.underline} ；\n依据本次调查的结果，估计全体名职工中最喜欢套餐的人数；\n现从甲、乙、丙、丁四名职工中任选两人担任"食品安全监督员"，求甲被选到的概率．\n【答案】（1）60，108°；（2）336；（3）\n【解析】\n【分析】\n（1）用最喜欢套餐的人数对应的百分比乘以总人数即可，先求出最喜欢C套餐的人数，然后用最喜欢C套餐的人数占总人数的比值乘以360°即可求出答案；\n（2）先求出最喜欢B套餐的人数对应的百分比，然后乘以960即可；\n（3）用列举法列出所有等可能的情况，然后找出甲被选到的情况即可求出概率．\n【详解】（1）最喜欢套餐的人数=25%×240=60（人），\n最喜欢C套餐![](./notebook/image/media/image226.wmf)人数=240-60-84-24=72（人），\n扇形统计图中""对应扇形的圆心角为：360°×=108°，\n故答案为：60，108°；\n（2）最喜欢B套餐的人数对应的百分比为：×100%=35%，\n估计全体名职工中最喜欢套餐的人数为：960×35%=336（人）；\n（3）由题意可得，从甲、乙、丙、丁四名职工中任选两人，总共有6种不同的结果，每种结果发生的可能性相同，列举如下：甲乙，甲丙，甲丁，乙丙，乙丁，丙丁，\n其中甲被选到的情况有甲乙，甲丙，甲丁3种，\n故所求概率P==．\n【点睛】本题考查了条形统计图和扇形统计图，用样本估计总体，用列举法求概率，由图表获取正确的信息是解题关键．\n七、解答题',
 '22.在平而直角坐标系中，已知点，直线经过点．抛物线恰好经过三点中的两点．\n判断点是否在直线上．并说明理由；\n求的值；\n平移抛物线，使其顶点仍在直线上，求平移后所得抛物线与轴交点纵坐标的最大值．\n【答案】（1）点在直线上，理由见详解；（2）a=-1，b=2；（3）\n【解析】\n【分析】\n（1）先将A代入，求出直线解析式，然后将将B代入看式子能否成立即可；\n（2）先跟抛物线与直线AB都经过（0，1）点，且B，C两点的横坐标相同，判断出抛物线只能经过A，C两点，然后将A，C两点坐标代入得出关于a，b的二元一次方程组；\n（3）设平移后所得抛物线的对应表达式为y=-（x-h）^2^+k，根据顶点在直线上，得出k=h+1，令x=0，得到平移后抛物线与y轴交点的纵坐标为-h^2^+h+1，在将式子配方即可求出最大值．\n【详解】（1）点在直线上，理由如下：\n将A（1，2）代入得，\n解得m=1，\n∴直线解析式为，\n将B（2，3）代入，式子成立，\n∴点在直线上；\n（2）∵抛物线与直线AB都经过（0，1）点，且B，C两点的横坐标相同，\n∴抛物线只能经过A，C两点，\n将A，C两点坐标代入得，\n解得：a=-1，b=2；\n（3）设平移后所得抛物线的对应表达式为y=-（x-h）^2^+k，\n∵顶点在直线上，\n∴k=h+1，\n令x=0，得到平移后抛物线与y轴交点的纵坐标为-h^2^+h+1，\n∵-h^2^+h+1=-（h-）^2^+，\n∴当h=时，此抛物线与轴交点的纵坐标取得最大值．\n【点睛】本题考查了求一次函数解析式，用待定系数法求二次函数解析式，二次函数的平移和求最值，求出两个函数的表达式是解题关键．\n八、解答题',
 '23.如图1．已知四边形是矩形．点在的延长线上．与相交于点，与相交于点\n求证：；\n若，求的长；\n![](./notebook/image/media/image246.png)\n如图2，连接，求证：．\n![](./notebook/image/media/image249.png)\n【答案】（1）见解析；（2）；（3）见解析\n【解析】\n【分析】\n（1）由矩形的形及已知证得△EAF≌△DAB，则有∠E=∠ADB，进而证得∠EGB=90º即可证得结论；\n（2）设AE=x，利用矩形性质知AF∥BC，则有，进而得到x的方程，解之即可；\n（3）在EF上截取EH=DG，进而证明△EHA≌△DGA，得到∠EAH=∠DAG，AH=AG，则证得△HAG为等腰直角三角形，即可得证结论．\n【详解】（1）∵四边形ABCD是矩形，\n∴∠BAD=∠EAD=90º，AO=BC，AD∥BC，\n在△EAF和△DAB，\n，\n∴△EAF≌△DAB(SAS)，\n∴∠E=∠BDA，\n∵∠BDA+∠ABD=90º，\n∴∠E+∠ABD=90º，\n∴∠EGB=90º，\n∴BG⊥EC；\n（2）设AE=x，则EB=1+x，BC=AD=AE=x，\n∵AF∥BC，∠E=∠E，\n∴△EAF∽△EBC，\n∴，又AF=AB=1，\n∴即，\n解得：，（舍去）\n即AE=；\n（3）在EG上截取EH=DG，连接AH，\n在△EAH和△DAG，\n，\n∴△EAH≌△DAG(SAS)，\n∴∠EAH=∠DAG，AH=AG，\n∵∠EAH+∠DAH=90º，\n∴∠DAG+∠DAH=90º，\n∴∠EAG=90º，\n∴△GAH是等腰直角三角形，\n∴即，\n∴GH=AG，\n∵GH=EG-EH=EG-DG，\n∴．\n![](./notebook/image/media/image261.png)\n【点睛】本题主要考查了矩形的性质、全等三角形的判定与性质、等腰三角形的判定与性质、直角定义、相似三角形的判定与性质、解一元二次方程等知识，涉及知识面广，解答的关键是认真审题，提取相关信息，利用截长补短等解题方法确定解题思路，进而推理、探究、发现和计算．']
    
    for row in align_answers_in_questions(test):
        print()
        print(row["question"])
        print("-------------------------------------------------------")
        print(f"{row['answer']}")
        print()
        print("============================================================")
