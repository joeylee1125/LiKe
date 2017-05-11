# -*- coding: UTF-8 -*-
import re
import sys
import os
import time
import csv
import argparse
import codecs
from docx import Document

import Spider


def download_case(wenshu):
    wenshu.setDownloadConditions()
    download_list = ['Y'] * len(wenshu.case['name'])
    print(len(download_list))
    for i in range(len(wenshu.case['name'])):
        #print(i)
        file_name = 'Download/' + wenshu.case['name'][i] + wenshu.case['date'][i] + '.docx'
        if not os.path.exists(file_name):
            print(i)
            wenshu.downloadDocument(wenshu.case['name'][i],
                                    wenshu.case['id'][i],
                                    wenshu.case['date'][i])
        else:
            pass
        #    print('file %s exist, skip...' % file_name)   
        #if os.path.exists(file_name):
        #    os.rename(file_name, 'Download1/' + str(i+2) + '_' + wenshu.case['name'][i] + wenshu.case['date'][i] + '.docx')
        docsize = os.path.getsize(file_name)
        # if docsize < 80k, it may corrupt. resend request.
        #print('docsize is %s' % docsize)
        if docsize < 80000:
            #input("Refresh the Page and Enter:")
            #time.sleep(10)
            print('file %s is invalid' % file_name)
            print(i)
            wenshu.downloadDocument(wenshu.case['name'][i],
                                    wenshu.case['id'][i],
                                    wenshu.case['date'][i])
            docsize = os.path.getsize(file_name)
            print('docsize is %s' % docsize)
        if docsize < 80000:
            download_list[i] = 'N'
        #time.sleep(1)
    wenshu.case['download'] = download_list

def get_case_info(wenshu):
    wenshu.getTotalItemNumber()
    print("Total case number is %s" % wenshu.total_items)
    wenshu.getCaseList(wenshu.total_items)


def write_2_csv(case):
    with open('case.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write(u'\ufeff')
        fieldnames = ['name', 'id', 'exist']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(case['name'])):
            writer.writerow({'name': case['name'][i],
                             'id': case['id1'][i],
                             'exist': case['exist'][i]})


def read_csv():
    name_list = []
    with open('case.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name_list.append(row['二审判决书名称'])
    return name_list


def get_case_1st_id(wenshu):
    id_1st_list = ['None'] * len(wenshu.case['name'])
    for i in range(len(wenshu.case['name'])):
        file_name = 'Download/' + wenshu.case['name'][i] + wenshu.case['date'][i] + '.docx'    
        if wenshu.case['download'][i] == 'Y':
            print('Processing document %s %s '%(i, wenshu.case['name'][i]))
            doc = read_doc(file_name)
            id_1st_list[i] = process_doc_data(doc)
    wenshu.case['id1'] = id_1st_list


def read_doc(doc_name=None):
    #   打开文档
    try:
        document = Document(doc_name) if doc_name else sys.exit(0)
    except docx.opc.exceptions.PackageNotFoundError:
        print("Document %s is invalid" % doc_name)
        s = 'NA'
        return s
    #   读取每段资料
    l = [paragraph.text for paragraph in document.paragraphs]
    s = ''.join(str(e) for e in l)

    return s


def process_doc_data(doc_data=None):
    #id_1st = re.search('.\d\d\d\d.\w+民.?初字第\d+号(?=民事判决)', doc_data)
    #if id_1st:
    #    return id_1st.group()
    #else:
    #    id_1st = re.search('.\d\d\d\d.\w+民.?初.?\d+号(?=民事)', doc_data)
    #    if id_1st:
    #        return id_1st.group()
    #    else:
    #        return 'None'
    id_1st = re.search('.\d\d\d\d.\w+?民.?初.+?号', doc_data)
    if id_1st:
        return id_1st.group()
    else:
        return 'None'
        
        
def search_and_download(case):
    doc_exist = []
    for id in case['id1']:
        print("Search document with id %s" % id)
        search_criteria = '全文检索:' + id + ',审判程序:一审'
        case_1 = get_case_info(search_criteria)
        if case_1['name']:
            download_case(search_criteria,
                          case_1['name'],
                          case_1['id'],
                          case_1['date'])
            doc_exist.append('Y')
        else:
            doc_exist.append('N')


def dump2csv(wenshu, surfix):
    with open('case' + surfix + '.csv', 'w', newline='', encoding='utf-8_sig') as csvfile:
        #csvfile.write(u'\ufeff')
        writer = csv.writer(csvfile)
        writer.writerow(wenshu.case.keys())
        writer.writerows(zip(*wenshu.case.values()))


def read_csv(wenshu, surfix):
    with open('case' + surfix + '.csv', encoding='utf-8_sig') as csvfile:
        reader = csv.DictReader(csvfile)
        case = dict.fromkeys(reader.fieldnames)
        for key in case:
            case[key] = []
        print(case)
        for row in reader:
            for key in case:
                case[key].append(row[key])
    #for key in case:
    #    if 'ufeff' in key:
    #        print(key)
    #case['name'] = case.pop('\ufeffname')            
    wenshu.case = case
            
# Phase 1: Search and get 2nd case list, download all of them,
#          dump case name list into a csv file.
def phase1(wenshu):
    # Get 2nd case list with search criteria.
    get_case_info(wenshu)
    dump2csv(wenshu, 'phase1')
    

def phase2(wenshu):
    # Read csv file and get case list.
    read_csv(wenshu, 'phase1')
    download_case(wenshu)
    dump2csv(wenshu,'phase2')

def phase3(wenshu):
    read_csv(wenshu, 'phase2')
    get_case_1st_id(wenshu)
    dump2csv(wenshu,'phase3')
    
    
def phase4(wenshu):
    file_name = 'Download/陈某与熊某离婚纠纷二审民事判决书2016-06-27.docx'
    doc = read_doc(file_name)
    print(doc)
    id_1st = re.search('.\d\d\d\d.\w+?民.?初.+?号', doc)
    print(id_1st)

    
def main():
    desc = "Select a phase to run"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-p', '--phase', action='store')
    args = parser.parse_args()
    search_criteria = "案件类型:民事案件,法院地域:四川省,四级案由:离婚纠纷,审判程序:二审"
    wenshu = Spider.WenShu()
    wenshu.setSearchCriteria(search_criteria)
    # Phase 1: Search 2nd case and document them into a csv file.
    # Phase 2: Read case list from csv file and download all of them.
    # Phase 3: Analyse 2nd case list and get 1st case id.
    # Phase 4: Search and download 1st case.
    if args.phase == 'all':
        print('phase 1')
        print('phase 2')
        print('phase 3')
    elif args.phase == '1':
        print('phase 1')
        phase1(wenshu)
    elif args.phase == '2':
        print('phase 2')
        phase2(wenshu)
    elif args.phase == '3':
        print('phase 3')
        phase3(wenshu)
    elif args.phase == '4':
        print('phase 4')
        phase4(wenshu)
    else:
        print('invalid')

    sys.exit(0)

# Get Search Criteria here
# 案件类型:民事案件,法院地域:四川省,四级案由:离婚纠纷,审判程序:二审
#    search_criteria = "案件类型:民事案件,法院地域:四川省,四级案由:离婚纠纷,审判程序:二审"

# Search and get case list
#    case = get_case_info(search_criteria)
#    print(case)

# Write case name to csv file
#    write_2_csv(case, u'二审判决书名称', 'name')

# Download all cases in the list
#    download_case(search_criteria, case['name'], case['id'], case['date'])

# Get 1st 初字第ID
#    case['id1'] = get_case_1st_id(case['name'])

# Search and Download 1st case
#    case['exist'] = search_and_download(case)

#    write_2_csv(case)

# Debug doc regression
     

if __name__ == "__main__":
    main()
