import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification


# 是否把sub-word全部标记的选项
LABEL_ALL_TOKENS = True

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
                label.appen(index_list)
        label_list.append(label)
        conversation_list.append(conversation)
    return label_list, conversation_list

def align_label(tokenized_input, labels, model):
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
    inputs = tokenizer(conversation, add_special_tokens=True, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_token_class_ids = logits.argmax(-1)
    predicted_tokens_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]
    print(len(predicted_tokens_classes))
    return predicted_tokens_classes

# 用来产生文本形式的输入输出的函数
def modify_inputs_and_labels_text1(conversation_list, label_list):
    inputs = []
    labels = []
    for i in range(len(conversation_list)):
        conversation = conversation_list[i]
        label = label_list[i]
        user_indexs = []
        for index in range(len(conversation)):
            if(conversation[index][0]=="[USER]"):
                user_indexs.append(index)
        for index in user_indexs:
            if(index==0 and len(conversation)>1):
                a_sen = conversation[index]
                a_sen.append("\n")
                b_sen = conversation[index+1]
                a_sen.extend(b_sen)
                sen = a_sen
                a_label = label[index]
                a_label.append("O")
                b_label = label[index+1]
                a_label.extend(b_label)
                sen_label = a_label
            elif(index==0 and len(conversation)==1):
                sen = conversation[index]
                sen_label = label[index]
            elif(index==len(conversation)-1):
                a_sen = conversation[index-1]
                a_sen.append("\n")
                b_sen = conversation[index]
                a_sen.extend(b_sen)
                sen = a_sen
                a_label = label[index-1]
                a_label.append("O")
                b_label = label[index]
                a_label.extend(b_label)
                sen_label = a_label
            else:
                a_sen = conversation[index-1]
                a_sen.append("\n")
                b_sen = conversation[index]
                b_sen.append('\n')
                c_sen = conversation[index+1] 
                a_sen.extend(b_sen)
                a_sen.extend(c_sen)
                sen = a_sen 
                a_label = label[index-1]
                a_label.append("O")
                b_label = label[index]
                b_label.append('O')
                c_label = label[index+1] 
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
    inputs, true_labels = modify_inputs_and_labels_text1(conversations,labels)
    print("There are {} conversations".format(len(conversations)))
    print("There are {} labels".format(len(labels)))
    for i in range(len(inputs)): 
        predict_label = get_predict_label(inputs[i], model, tokenizer)

if __name__=="__main__":
    main()
