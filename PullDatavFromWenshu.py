# -*- coding: UTF-8 -*-
import re
import os
import csv
import codecs
from docx import Document

import Spider

def download_case(search_criteria, case):
    wenshu = Spider.WenShu()
    download_condition = search_criteria.replace(':', '为').replace(',', '且')
    wenshu.setDownloadConditions(download_condition)

    for i in range(len(case['name'])):
#       print('Download')
#       print(case['name'][i])
#       print(case['date'][i])
#       print(case['id'][i]) 
        wenshu.downloadDocument(case['name'][i], case['id'][i], case['date'][i])

def get_case(search_criteria):
    wenshu = Spider.WenShu()
    wenshu.setSearchCriteria(search_criteria)
    
    download_condition = search_criteria.replace(':', '为').replace(',', '且')
    wenshu.setDownloadConditions(download_condition)
    
    total_items = wenshu.getTotalItems()
    print("Total case number is %s" % total_items)
    
    case = wenshu.getCaseList(total_items)
    print(case)
    return case
    
def write_2_csv(case, col_name, key):
    with open('case.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write(u'\ufeff')
        fieldnames = [col_name]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(case[key])):
            writer.writerow({col_name: case[key][i]})

def read_csv():
    name_list = []
    with open('case.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name_list.append(row['二审判决书名称'])
    return name_list       
            
def get_case_1st_id(case_list):
    id_1st_list = []
    for case in case_list:
        doc = read_doc(case + '.docx')
        id_1st_list.append(process_doc_data(doc))
    return id_1st_list
    
def read_doc(doc_name=None):
    #打开文档
    document = Document(doc_name) if doc_name else sys.exit(0)
    
    #读取每段资料
    l = [ paragraph.text for paragraph in document.paragraphs];
    s = ''.join(str(e) for e in l)
    #输出并观察结果，也可以通过其他手段处理文本即可
    #for i in l:
    #    print(i)
    #读取表格材料，并输出结果
    #tables = [table for table in document.tables];
    #for table in tables:
    #    for row in table.rows:
    #        for cell in row.cells:
    #            print(cell.text.encode('utf-8'),'\t',)
    #        print("")
    #    print('\n')
    return s
    
def process_doc_data(doc_data=None):    
    #pattern1 = re.compile('判处(.*?)', re.S)
    #a = re.findall(pattern1,doc_data)
    #print(doc_data)
    #print()
    #a = re.search('判处.*?。',doc_data)
    #print(a)
    #print(a.group())
    id_1st = re.search('.\d\d\d\d.\w+民初字第\d+号(?=民事判决)',doc_data)
    
    #print(id_1st.group())
    return id_1st.group()

        
def main():
# Get Search Criteria here
# 案件类型:民事案件,法院地域:四川省,四级案由:离婚纠纷,审判程序:二审
    #search_criteria = "案件类型:民事案件,法院地域:四川省,四级案由:离婚纠纷,审判程序:二审"
    
# Search and get case list
    #case = get_case(search_criteria)
    
# Write case name to csv file
    #write_2_csv(case, u'二审判决书名称', 'name')
    
# Download all case in the list
    #download_case(search_criteria, case)
    
# Read case name from csv file
    case_name_list = read_csv()
    
# Get 1st 初字第ID
    id_1st_list = get_case_1st_id(case_name_list)

# Write case name to csv file
    
# Search and Download 1st case 
    for id_1st in id_1st_list:
        print(id_1st)
        search_criteria = '全文检索:' + id_1st + ',审判程序:一审'    
        case = get_case(search_criteria)
        if case['name']:
            print('not empty')
            download_case(search_criteria, case)
if __name__ == "__main__":
    main()