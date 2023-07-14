"""
此模块定义了一个文本分类器模型，该模型使用BERT进行词嵌入，并使用双向GRU进行文本编码。
模型在TextClassifier类中定义，该类包括训练模型和保存模型的方法。
"""
import torch
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import BertModel, BertTokenizer
from tqdm import tqdm


# 定义文本分类器模型类
class TextClassifier(nn.Module):
    def __init__(self, num_classes):
        super(TextClassifier, self).__init__()
        # 加载预训练的BERT中文模型
        self.bert = BertModel.from_pretrained('bert-base-chinese')
        # 定义双向GRU层
        self.gru = nn.GRU(768, 256, bidirectional=True, batch_first=True)
        # 定义全连接层，用于最后的分类预测
        self.fc = nn.Linear(512, num_classes)

    # 定义前向传播过程
    def forward(self, input_ids, attention_mask):
        # 通过BERT模型获取词向量
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        x = outputs[0]
        # 通过GRU处理BERT的输出
        x, _ = self.gru(x)
        # 取最后一个时间步的输出
        x = x[:, -1, :]
        # 通过全连接层进行分类预测
        x = self.fc(x)
        return x

    def train_model(self, documents, labels, epochs=10, batch_size=2, learning_rate=1e-5):
        # 加载BERT的tokenizer
        tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
        # 定义优化器
        optimizer = AdamW(self.parameters(), lr=learning_rate)
        # 定义损失函数
        criterion = nn.CrossEntropyLoss()

        # 计算总的批次数量
        total_batches = len(documents) // batch_size
        if len(documents) % batch_size != 0:
            total_batches += 1
        total_steps = total_batches * epochs

        # 创建一个tqdm对象
        with tqdm(total=total_steps, desc='Training', unit='step') as pbar:
            # 进行多个epoch的训练
            for epoch in range(epochs):
                # 分批处理数据
                for i in range(0, len(documents), batch_size):
                    # 准备数据批次
                    batch_docs = documents[i:i+batch_size]
                    batch_labels = torch.tensor(labels[i:i+batch_size])

                    # 预处理数据
                    inputs = tokenizer(batch_docs, padding=True, truncation=True, max_length=512, return_tensors='pt')
                    input_ids = inputs['input_ids']
                    attention_mask = inputs['attention_mask']

                    # 前向传播，得到预测结果
                    outputs = self(input_ids, attention_mask)

                    # 计算损失
                    loss = criterion(outputs, batch_labels)

                    # 反向传播和优化
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                    # 更新进度条
                    pbar.update(1)

    # 定义保存模型的方法
    def save_model(self, path):
        torch.save(self, path)

    def predict(self, documents):
        # 加载BERT的tokenizer
        tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

        # 预处理数据
        inputs = tokenizer(documents, padding=True, truncation=True, max_length=512, return_tensors='pt')
        input_ids = inputs['input_ids']
        attention_mask = inputs['attention_mask']

        # 使用模型进行预测
        outputs = self(input_ids, attention_mask)

        # 获得预测的类别
        predicted_classes = torch.argmax(outputs, dim=-1)
        return predicted_classes

import glob

if __name__ == '__main__':
    math_file_paths = glob.glob("./data/docx_math_markdown" + '/' + "*.md")
    math_train_documents = []
    math_train_labels = []
    
    for file_path in math_file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            math_train_documents.append(f.read())
            math_train_labels.append(0)

    other_file_paths = glob.glob("./docx_other_markdown" + '/' + "*.md")
    other_train_documents = []
    other_train_labels = []
    
    for file_path in other_file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            other_train_documents.append(f.read())
            other_train_labels.append(1)

    model = TextClassifier(2)
    # # 训练模型
    model.train_model(math_train_documents + other_train_documents, math_train_labels + other_train_labels)
    # # 保存模型
    model.save_model("./model.pth")
    #
    # print(model.predict(["纠错日记。"]))
