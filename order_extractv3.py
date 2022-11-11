import re
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
LABEL_LIST = [[[7, 0, 1], [7, 8, 9]], [[7, 0, 1], [7, 7, 8]], [[2, 3, 4], [2, 13], [2, 3, 4], [2, 13], [5, 10]], [], [[4, 0]], [[3, 3], [3, 11]], [[1, 3], [7, 0]], [[1, 3], [5, 5]], [[1, 3], [7, 0]], [], [[2, 0], [6, 0]], [[7, 2], [11, 0], [46, 2], [48, 13], [49, 0], [50, 0]], [[1, 5]], [[4, 3]], [[8, 0]], [], [[5, 2, 3], [6, 2, 3]], [[5, 0]], [[10, 3], [10, 15], [11, 3]], [[5, 0]], [], [], [[5, 0, 1]], [[7, 0], [9, 0]]]
order_line_re = "-------------------- order: (.*) --------------------"
pair_line_re = "==================== pair: (.*) ===================="

# Get the byte names of advisor when running this at the first time.
def get_bytes_name(fin):
    for line in fin:
        name_get = re.findall(".*\t(.*)\t:.*", line)
        if name_get:
            name = name_get[0]
            
            if name not in name_list:
                print(name)
                name_list.append(name)

            if name.encode() not in byte_name_list:
                print(name.encode())
                byte_name_list.append(name.encode())

def extract_order(fin):
    record_flag = False
    pairNO = 0
    counter = 1
    orders = []
    an_order = {"pairNO": pairNO,
                "orderNO": 0,
                "order": [],
                "label": LABEL_LIST[len(orders)]}
    
    for line in fin:

        if not line.strip():
            continue
        
        order_line_get = re.findall(order_line_re, line)
        if(order_line_get):
            # 找到order_line就开始记录
            if an_order["order"]:
                counter += 1
                del(an_order["order"][-1])
                orders.append(an_order.copy())
                an_order = {"pairNO": pairNO,
                            "orderNO": int(order_line_get[0]),
                            "order": [],
                            "label": LABEL_LIST[len(orders)]}
            else:
                an_order = {"pairNO": pairNO,
                            "orderNO": int(order_line_get[0]),
                            "order": [],
                            "label": LABEL_LIST[len(orders)]}
            record_flag = True
            continue
                
        pair_line_get = re.findall(pair_line_re, line)
        if(pair_line_get):
            pairNO = int(pair_line_get[0].strip())
            if an_order["order"]:
                counter += 1
                orders.append(an_order.copy())
                an_order["order"] = []
            record_flag = False
            print(pairNO)
            continue
        
        if(record_flag):
            get_line_text = re.findall("\t.*\t(.*)\t:(.*)\n",line)
            if get_line_text:
                name = get_line_text[0][0]
                if name.encode() in byte_name_list:
                    name = "[ADVISOR]"
                else:
                    name = "[USER]"
                text = get_line_text[0][1]
            else:
                name = "[NEWLINE]"
                text = line
            an_order["order"].append([name,text])
    
    orders.append(an_order)
    print(counter)

    return orders

def main():
    with open("order.sample.txt", "r") as fin:
        # get_bytes_name(fin)    
        orders = extract_order(fin)
        print(orders)
    json_str = json.dumps(orders)
    with open("conversation_data/datav3.json", "w") as jf: 
        jf.write(json_str)

if __name__=="__main__":
    main()
