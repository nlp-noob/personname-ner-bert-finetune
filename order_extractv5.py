import re
import sys
import json

byte_name_list = [b'Healing Lady', 
                  b'Psychic Sara \xf0\x9f\x92\xab',
                  b'Spiritualist Autumn ',
                  b'\xe2\xad\x90\xef\xb8\x8f\xe2\x9c\xa8psychic Valerie\xe2\x9c\xa8\xe2\xad\x90\xef\xb8\x8f',
                  b'psychic Moon \xf0\x9f\x8c\x99',
                  b'Psychic Miss Lee ',
                  b'psychic Clarissa ',
                  b'Psychic Faith',
                  b'\xf0\x9f\x8c\xb8Advisor Angelica \xf0\x9f\x8c\xb8',
                  b'Bewitched ',
                  b'\xf0\x9f\x94\xaePsychic\xf0\x9f\x92\x98\xf0\x9f\x92\x94Monika\xf0\x9f\x92\x8e']
catch_text_compile = re.compile(r".*(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}).(\d+).*")
pair_line = "==================== pair:"
order_line = "-------------------- order:"
LABEL_LIST = [[[7, 0, 1], [7, 8, 9]], [[7, 0, 1], [7, 7, 8]], [[2, 3, 4], [2, 13], [2, 3, 4], [2, 13], [5, 10]], [], [[4, 0]], [[3, 3], [3, 11]], [[1, 3], [7, 0]], [[1, 3], [5, 5]], [[1, 3], [7, 0]], [], [[2, 0], [6, 0]], [[7, 2], [11, 0], [46, 2], [48, 13], [49, 0], [50, 0]], [[1, 5]], [[4, 3]], [[8, 0]], [], [[5, 2, 3], [6, 2, 3]], [[5, 0]], [[10, 3], [10, 15], [11, 3]], [[5, 0]], [], [], [[5, 0, 1]], [[7, 0], [9, 0]]]
def get_data(fin):
    pair_no = -1
    orders = []
    order_no = 0
    an_order = {"pairNO":pair_no,
                "orderNO":order_no,
                "order":[],
                "label":LABEL_LIST[len(orders)]}
    for line in fin:
    
        if not line.strip():
            continue

        if order_line in line and an_order["order"]:
            orders.append(an_order)
            order_no += 1
            an_order = {"pairNO":pair_no,
                        "orderNO":order_no,
                        "order":[],
                        "label":LABEL_LIST[len(orders)]}

        if pair_line in line:
            pair_no += 1

        if pair_line in line and an_order["order"]:
            orders.append(an_order)
            an_order = {"pairNO":pair_no,
                        "orderNO":order_no,
                        "order":[],
                        "label":LABEL_LIST[len(orders)]}
            order_no = 0

        if catch_text_compile.match(line):
            sentence = re.findall("\t.*\t(.*)\t:(.*)", line)
            name = sentence[0][0]
            if name.encode() in byte_name_list:
                name = "[ADVISOR]"
            else:
                name = "[USER]"
            text = sentence[0][1]
            an_order["order"].append([name,text])

    orders.append(an_order)
            
    return orders


def main():
    txt_file = sys.argv[1] if len(sys.argv) > 1 else 'order.sample.txt'
    with open(txt_file, 'r') as fin:
        orders = get_data(fin)
        print(orders)
    json_str = json.dumps(orders)
    with open("conversation_data/data5.json", "w") as jf: 
        jf.write(json_str)
    

if __name__=="__main__":
    main()







