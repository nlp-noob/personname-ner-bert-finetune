from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
model_path = "dslim/bert-base-NER" 
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)


##### Process text sample (from wikipedia)

sentence = ["Hug Jackman is the best actor in the world."]
inputs = tokenizer(
            sentence, add_special_tokens=True, return_tensors="pt"
        )

with torch.no_grad():
        logits = model(**inputs).logits

predicted_token_class_ids = logits.argmax(-1)

# Note that tokens are classified rather then input words which means that
# there might be more predicted token classes than words.
# Multiple token classes might account for the same word
predicted_tokens_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]
print(predicted_tokens_classes)

from transformers import pipeline

nlp = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")
result = nlp(sentence)

# 这里先做一个标记
labels = ["B-PER", "O", "O", "O", "0", "O", "O", "O", "O"]
label_all_tokens = False
def align_label_example(tokenized_input, labels):
    word_ids = tokenized_input.word_ids()
    previous_word_idx = None
    label_ids = []              
    for word_idx in word_ids:
        if word_idx is None:
            label_ids.append(-100)      
        elif word_idx != previous_word_idx:
            try:
                label_ids.append(model.config.label2id[labels[word_idx]])
            except:
                label_ids.append(-100)
        else:
            label_ids.append(model.config.label2id[labels[word_idx]] if label_all_tokens else -100)
        previous_word_idx = word_idx                  
    return label_ids
def ids2labels(id_list):
    label_list = []
    for label_id in id_list:
        if(label_id==-100):
            label_list.append("O")
        else:
            label_list.append(model.config.id2label[label_id])
    return label_list
import pdb; pdb.set_trace()


print(result)
