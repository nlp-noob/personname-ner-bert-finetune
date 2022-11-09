import json
import sys
import re

pair_pattern = '==================== pair:'
order_pattern = '-------------------- order:'
order_info_words = 'order_price total_cost 3m_free 3m_convert_tag'.split()

dialog_split = '\t:'

ADVISOR_LIST = ["HealingLady", "PsychicSara","psychic Valerie", "psychic Moon", "PsychicMissLee", "psychic Clarissa",
                "PsychicFaith", "Advisor Angelica", "Bewitched", "Psychic", "Healing Lady", "Spiritualist Autumn"]

def is_name_in_list(name,name_list):
    for advisor_name in name_list:
        index = name.find(advisor_name)
        if(index!=-1):
            return True
    return False

def is_order_info(line):
    for order_word in order_info_words:
        if order_word not in line:
            return False
    return True

def extract_order(fin):
    orders = []
    order = []
    for line in fin:

        if not line.strip():
            continue

        if pair_pattern in line:
            continue

        if order_pattern in line:
            continue
            
        if is_order_info(line):
            # end of order
            if order:
                orders.append(order)
                order = []
            continue

        # order text
        dialog_parts = line.strip().split(dialog_split)
        txt = dialog_parts[-1]
        sender = dialog_parts[0].split('\t')[-1]
        is_user = not is_name_in_list(sender, ADVISOR_LIST)
        order.append([is_user, txt])

    if order:
        orders.append(order)

    for order in orders:
        print('**' * 20)
        print(order)

def main():
    txt_file = sys.argv[1] if len(sys.argv) > 1 else 'order.sample.txt'
    with open(txt_file, 'r') as fin:
        extract_order(fin)

if __name__ == '__main__':
    main()
