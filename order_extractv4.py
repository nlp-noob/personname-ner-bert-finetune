import re
import sys
import json

ADVISOR_LIST = ["HealingLady", "PsychicSara","psychic Valerie", "psychic Moon", "PsychicMissLee", "psychic Clarissa",
                "PsychicFaith", "Advisor Angelica", "Bewitched", "Psychic", "Healing Lady", "Spiritualist Autumn"]
LABEL_LIST = [[[7, 0, 1], [7, 8, 9]], [[7, 0, 1], [7, 7, 8]], [[2, 3, 4], [2, 13], [2, 3, 4], [2, 13], [5, 10]], [], [[4, 0]], [[3, 3], [3, 11]], [[1, 3], [7, 0]], [[1, 3], [5, 5]], [[1, 3], [7, 0]], [], [[2, 0], [6, 0]], [[7, 2], [11, 0], [46, 2], [48, 13], [49, 0], [50, 0]], [[1, 5]], [[4, 3]], [[8, 0]], [], [[5, 2, 3], [6, 2, 3]], [[5, 0]], [[10, 3], [10, 15], [11, 3]], [[5, 0]], [], [], [[5, 0, 1]], [[7, 0], [9, 0]]]
line_order_re = "-------------------- order: (.*) --------------------"
line_pair_re = "==================== pair: (.*) ===================="
order_price_re = "order_price: (.*), total_cost: (.*), 3m_free: (.*), 3m_convert_tag: (.*)" 

def is_name_in_list(name, name_list):
    for advisor_name in name_list:
        index = name.find(advisor_name)
        if(index!=-1):
            return True
    return False

def extract_order(fin):
    pair_no = -1
    order_no = None
    pair_no_pre = None
    an_order = []
    orders = []
    for line in fin:

        if not line.strip():
            continue
        
        order_text = re.findall(line_order_re, line)
        if order_text:
            order_no = int(order_text[0])
            if order_no == 0:
                pair_no += 1
            continue

        pair_text = re.findall(line_pair_re, line)
        if pair_text:
            continue

        order_price_text = re.findall(order_price_re, line)
        if order_price_text:
            if not an_order:
                continue
            orders.append({"pairNO": pair_no, 
                           "orderNO": order_no,
                           "order": an_order,
                           "label": LABEL_LIST[len(orders)]})
            an_order = []
        else:
            sentence = re.findall("\t.*\t(.*)\t:(.*)", line)
            if (len(sentence[0])<2):
                an_order.append(["[NEWLINE]",line]) 
                continue

            name = sentence[0][0]
            text = sentence[0][1]
            if is_name_in_list(name, ADVISOR_LIST):
                name = "[ADVISOR]"
            else:
                name = "[USER]"
            an_order.append([name,text])

    orders.append({"pairNO": pair_no, 
                   "orderNO": order_no,
                   "order": an_order,
                   "label": LABEL_LIST[-1]})
    print(len(orders))
    return orders
            
def main():
    txt_file = sys.argv[1] if len(sys.argv) > 1 else 'order.sample.txt'
    with open(txt_file, 'r') as fin:
        orders = extract_order(fin)
    json_str = json.dumps(orders)
    with open("conversation_data/data4.json", "w") as jf: 
        jf.write(json_str)



if __name__=="__main__":
    main()
