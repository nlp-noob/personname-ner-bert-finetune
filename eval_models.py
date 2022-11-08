import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from seqeval.metrics import accuracy_score, precision_score, recall_score, f1_score
from seqeval.metrics import classification_report

# 是否把sub-word全部标记的选项
LABEL_ALL_TOKENS = True
# 设置打标签的名字，分别对应前面的标签和后面的标签
PREVIOUS_LABEL = "B-PER"
CENTER_LABEL = "I-PER"

def get_conversations_and_labels():
    file_list = os.listdir("conversation_data")
    conversation_list = []
    label_list = []
    for file_name in file_list:
        f = open("conversation_data/"+file_name)
        lines = f.readlines()
        conversation = [] 
        label = []
        index = 0
        for line in lines:
            if(line[0]=="["):
                name = re.findall("(.*)\t:.*",line)[0]
                content = re.findall(".*\t:(.*)",line)[0]
                conversation_temp = name + " " + ":" + " " + content
                conversation.append(conversation_temp.split())
            else:
                if(len(line)==0):
                    continue
                index_list = line.split()
                for i in range(len(index_list)):
                    index_list[i] = int(index_list[i])
                label.append(index_list)
        label_list.append(label)
        conversation_list.append(conversation)
    return label_list, conversation_list

def align_label_b(tokenized_input, labels, model):
    word_ids = tokenized_input.word_ids()
    previous_word_idx = None
    label_ids = []
    for word_idx in word_ids:
        # print(word_idx)
        if word_idx is None:
            label_ids.append(-100)      
        elif word_idx != previous_word_idx:
            try:
                label_ids.append(model.config.label2id[labels[word_idx]])
            except:
                label_ids.append(-100)
        else:
            label_ids.append(model.config.label2id[labels[word_idx]] if LABEL_ALL_TOKENS else -100)
        previous_word_idx = word_idx                  
    label_list = []
    for label_id in label_ids:
        if(label_id==-100):
            label_list.append("O")
        else:
            label_list.append(model.config.id2label[label_id])
    
    return label_list

def get_predict_label(conversation, model, tokenizer):
    inputs = tokenizer(conversation, add_special_tokens=False, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_token_class_ids = logits.argmax(-1)
    predicted_tokens_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]
    return predicted_tokens_classes

def align_label(sentence, label, tokenizer):
    # 这里传入的label就是当前这句话中所有标记的坐标
    # 如果label为空表示这里面没有标注
    joined_sentence = " ".join(sentence)
    inputs = tokenizer(joined_sentence, add_special_tokens=False, return_tensors="pt")
    word_ids = inputs.word_ids()
    tokenized_sentence = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    # 计算坐标的偏移
    label_bias = 0
    for token_id in range(len(tokenized_sentence)):
        if tokenized_sentence[token_id]==None:
            continue
        if tokenized_sentence[token_id]==":":
            label_bias = word_ids[token_id] + 1
            break
    aligned_label = []
    for token_ids in range(len(tokenized_sentence)):
        aligned_label.append("O")
    for a_label in label:
        for label_index in range(len(a_label)):
            if(label_index==0):
                label_name = PREVIOUS_LABEL
            else:
                label_name = CENTER_LABEL
            for label_to_modify_index in range(len(aligned_label)):
                if word_ids[label_to_modify_index]==a_label[label_index]+label_bias:
                   aligned_label[label_to_modify_index]=label_name
    return aligned_label

# 用来产生文本形式的输入输出的函数
def modify_inputs_and_labels_text1(conversation_list, label_list, tokenizer):
    inputs = []
    labels = []
    for i in range(len(conversation_list)):
        conversation = conversation_list[i]
        label = label_list[i]
        user_indexs = []
        aligned_labels = []
        #############################
        # 将label转换成tokenized的形式
        for index in range(len(conversation)):
            label_to_convert = []
            for one_label in label:
                if(len(one_label)>0 and one_label[0]==(index+1)):
                    a_label_in_sentence = []
                    for label_index in range(len(one_label)):
                        if label_index==0:
                            continue
                        else:
                            a_label_in_sentence.append(one_label[label_index])
                    label_to_convert.append(a_label_in_sentence)
            aligned_labels.append(align_label(conversation[index],label_to_convert,tokenizer))    
        # 将label转换成tokenized的形式
        ##############################
        ##############################
        # 按照我们需要的形式对文本进行组合，同时将label用同样的方式组合在一起
        for index in range(len(conversation)):
            if(conversation[index][0]=="[USER]"):
                user_indexs.append(index)
        for index in user_indexs:
            if(index==0 and len(conversation)>1):
                a_sen = conversation[index].copy()
                b_sen = conversation[index+1].copy()
                a_sen.extend(b_sen)
                sen = a_sen
                a_label = aligned_labels[index].copy()
                b_label = aligned_labels[index+1].copy()
                a_label.extend(b_label)
                sen_label = a_label
            elif(index==0 and len(conversation)==1):
                sen = conversation[index]
                sen_label = aligned_labels[index]
            elif(index==len(conversation)-1):
                a_sen = conversation[index-1].copy()
                b_sen = conversation[index].copy()
                a_sen.extend(b_sen)
                sen = a_sen
                a_label = aligned_labels[index-1].copy()
                b_label = aligned_labels[index].copy()
                a_label.extend(b_label)
                sen_label = a_label
            else:
                a_sen = conversation[index-1].copy()
                b_sen = conversation[index].copy()
                c_sen = conversation[index+1].copy()
                a_sen.extend(b_sen)
                a_sen.extend(c_sen)
                sen = a_sen 
                a_label = aligned_labels[index-1].copy()
                b_label = aligned_labels[index].copy()
                c_label = aligned_labels[index+1].copy()
                a_label.extend(b_label)
                a_label.extend(c_label)
                sen_label = a_label
            symbol = ' ' 
            sen = symbol.join(sen)
            inputs.append(sen)
            labels.append(sen_label)
    return inputs, labels

def main():
    model_path = "dslim/bert-base-NER"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    labels, conversations = get_conversations_and_labels()
    print(labels)
    print("There are {} conversations".format(len(conversations)))
    print("There are {} labels".format(len(labels)))
    inputs, true_labels = modify_inputs_and_labels_text1(conversations,labels,tokenizer)
    y_true = []
    y_pred = []
    for i in range(len(inputs)): 
        predict_labels = get_predict_label(inputs[i], model, tokenizer)
        y_true.append(true_labels[i])
        y_pred.append(predict_labels)
    # 评估模型
    print(f'\t\t准确率为： {accuracy_score(y_true, y_pred)}')
    print(f'\t\t查准率为： {precision_score(y_true, y_pred)}')
    print(f'\t\t召回率为： {recall_score(y_true, y_pred)}')
    print(f'\t\tf1值为： {f1_score(y_true, y_pred)}')
    print(classification_report(y_true, y_pred))
    import pdb;pdb.set_trace()
if __name__=="__main__":
    main()
