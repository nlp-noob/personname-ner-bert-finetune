import re

ADVISOR_LIST = ["HealingLady", "PsychicSara","psychicValerie", "psychicMoon", "PsychicMissLee", "psychicClarissa",
                "PsychicFaith", "AdvisorAngelica", "Bewitched", "Psychic"]

def name_is_in_list(name, name_list):
    for advisor_name in name_list:
        index = name.find(advisor_name)
        if(index!=-1):
            return True
    return False
                
def get_conversations():
    f = open("order.sample.txt")
    lines = f.readlines()
    conversations_list = []
    a_conversation = []
    for line in lines:
        if(len(line)<2):
            continue
        if(line[1]=='2'):
            line = re.findall("\t.+?\t(.*)", line)[0]
            name = re.findall("(.*)\t.*", line)[0]
            name = ''.join(list(filter(str.isalpha,name)))
            rest = re.findall(".*\t(.*)", line)[0]
            if name_is_in_list(name, ADVISOR_LIST):
                result = '[ADVISOR]'+'\t'+rest
            else:
                result = '[USER]'+'\t'+rest
            print(result)
            a_conversation.append(result)
        else:
            if(len(a_conversation)!=0):
                conversations_list.append(a_conversation)
                a_conversation = []
    return conversations_list

def write_conversation(conversations_list):
    conversation_num = 0
    for conversation in conversations_list:
        conversation_num += 1
        if(conversation_num < 22):
            continue
        f = open("conversation_data/{}conversation.txt".format(conversation_num), "w")
        for sentence in conversation:
            f.writelines(sentence+'\n')

def main():
    conversations_list = get_conversations()
    write_conversation(conversations_list)

if __name__=="__main__":
    main()
