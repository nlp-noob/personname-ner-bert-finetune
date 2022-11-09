import json
import re

ADVISOR_LIST = ["HealingLady", "PsychicSara","psychic Valerie", "psychic Moon", "PsychicMissLee", "psychic Clarissa",
                "PsychicFaith", "Advisor Angelica", "Bewitched", "Psychic", "Healing Lady", "Spiritualist Autumn"]

def name_is_in_list(name,name_list):
    for advisor_name in name_list:
        index = name.find(advisor_name)
        if(index!=-1):
            return True
    return False

def del_the_zero_in_begin(string):
    if len(string)==1:
        return int(string)
    elif string[0]=='0':
        string = string[1:]
        return del_the_zero_in_begin(string)
    else:
        return int(string)
    
def get_conversation():
    f = open("order.sample.txt")
    lines = f.readlines()
    order_num_list = []
    order_index_list = []
    # 记录order的坐标以及order的编号
    for line_index in range(len(lines)):
        if(lines[line_index][0]=='-'):
            order_num_str = re.findall('.*order: (.*) .*', lines[line_index])[0]
            order_num = del_the_zero_in_begin(order_num_str)
            order_num_list.append(order_num)
            order_index_list.append(line_index)
    conversation_list = []
    for conversation_num in range(len(order_index_list)):
        if(conversation_num<=len(order_index_list)-2 and order_num_list[conversation_num+1]==0):
            this_index = order_index_list[conversation_num]
            next_index = order_index_list[conversation_num+1] 
            conversation_to_append = lines[this_index+1:next_index-2]
        elif(conversation_num<=len(order_index_list)-2 and order_num_list[conversation_num+1]!=0):
            this_index = order_index_list[conversation_num]
            next_index = order_index_list[conversation_num+1]
            conversation_to_append = lines[this_index+1:next_index-1]
        else:
            this_index = order_index_list[conversation_num]
            conversation_to_append = lines[this_index+1:]
        if(len(conversation_to_append)!=0):
            conversation_list.append(conversation_to_append)
    print("There are {} conversations.".format(len(conversation_list)))
    # 逐个conversation进行处理
    conversation_json = {}
    for conversation_index in range(len(conversation_list)):
        conversation = conversation_list[conversation_index]
        have_advisor = 0
        have_name = True
        conversation_dict = {}
        for line_index in range(len(conversation)):
            a_sentence_dict = {}
            name_list = re.findall(".*\t(.*)\t:.*", conversation[line_index])
            text_list = re.findall(".*\t:(.*)",conversation[line_index])
            if(len(text_list)==0):
                text = ''
            else:
                text = text_list[0]
            # 假如没有名字，那么就是说相应的name对应的就是上一个name
            if(len(name_list)!=0):
                name = name_list[0] 
                have_name = True
            else:
                have_name = False
            if name_is_in_list(name,ADVISOR_LIST):
                conversation_dict["character"] = "ADVISOR"
                have_advisor = 1
            else: 
                conversation_dict["character"] = "USER" 
            conversation_dict["name"] = name
            conversation_dict["text"] = text
        conversation_json[conversation_index] = conversation_dict 
        if(have_advisor==0):
            print("warning: can't catch the advisor. please add it in the list a the bottom of the code")
            print("can't find in conversation{}".format(conversation_index))
            print(conversation)
    json_str = json.dumps(conversation_json)
    with open("conversation_data/data.json", "w") as jf:
        jf.write(json_str)
    
def main():
    get_conversation()

if __name__=="__main__":
    main()

