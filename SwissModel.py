import requests
import time
import sys
import argparse
import os
import gzip


# 参数
time_start=time.time()
token = 'bb27eebd3c3308ebfcd84fcab4284465c837d9ad' # 注册SwissModel账号可获取
local_path = './static/SwissModel/' # 输出路径，请自行修改
parser = argparse.ArgumentParser()
parser.add_argument('--project',type=str,default='Automodel')    # project 取值 Automodel，Alignment,User_Template
parser.add_argument('--test',type=str,default='TEST')            # test 取值 TEST 时跑测试样例，else跑自己的输入（还没写）
parser.add_argument('--output_type',type=str,default='')         # 取值 ALL 则下载历史全部输出文件 否则只输出当次结果
parser.add_argument('--pdb_file',type=str,default='pdb3l9y.pdb') # User_Template 的输入pdb文件
args=parser.parse_args()
# test cases
Automodel_test_target_sequences = [
                        "VLSPADKTNVKAAWAKVGNHAADFGAEALERMFMSFPSTKTYFSHFDLGHNSTQVKGHGKKVADALTKAVGHLDTLPDALSDLSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPGDFTPSVHASLDKFLASVSTVLTSKYR",
                        "VHLTGEEKSGLTALWAKVNVEEIGGEALGRLLVVYPWTQRFFEHFGDLSTADAVMKNPKVKKHGQKVLASFGEGLKHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVVVLARHFGKEFTPELQTAYQKVVAGVANALAHKYH"
                    ]
Automodel_test_project_title = "This is an example using multiple targets for hemoglobin"


# 创建项目 Automodel，Alignment,User_Template
if args.project == "Automodel" :
    if args.test == "TEST":
        response = requests.post(
            "https://swissmodel.expasy.org/automodel",
            headers={ "Authorization": f"Token {token}" },
            json={ 
                "target_sequences": 
                    Automodel_test_target_sequences,
                "project_title":
                    Automodel_test_project_title
            })
    else :
        print("default: invalid input")
        print("Please use the test cases")
        sys.exit(0)
    filename = "Automodel"
elif args.project == "Alignment":
    if args.test == "TEST":
        response = requests.post(
        "https://swissmodel.expasy.org/alignment",
        headers={ "Authorization": f"Token {token}" },
        json={ 
            "target_sequences":  "KSCCPTTAARNQYNICRLPGTPRPVCAALSGCKIISGTGCPPGYRH",
            "template_sequence": "TTCCPSIVARSNFNVCRLPGTPEAICATYTGCIIIPGATCPGDYAN",
            "template_seqres_offset": 0,
            "pdb_id": "1crn",
            "auth_asym_id": "A",
            "assembly_id": 1,
            "project_title": "This is an example of Aligment mode based on 1crn"
            })
    else :
        print("default: invalid input")
        print("Please use the test cases")
        sys.exit(0)
    filename = "Alignment"
elif args.project == "User_Template":
    if args.test == "TEST":
        with open(args.pdb_file) as f:
            template_coordinates = f.read()
        response = requests.post(
            "https://swissmodel.expasy.org/user_template",
            headers={ "Authorization": f"Token {token}" },
            json={
                "target_sequences": "MVVKAVCVINGDAKGTVFFEQESSGTPVKVSGEVCGLAKGLHGFHVHEFGDNTNGCMSSGPHFNPYGKEHGAPVDENRHLGDLGNIEATGDCPTKVNITDSKITLFGADSIIGRTVVVHADADDLGQGGHELSKSTGNAGARIGCGVIGIAKV",
                "template_coordinates": template_coordinates,
                "project_title":"This is an example of User Template based on SODC_DROME"
                })
    else :
        print("default: invalid input")
        print("Please use the test cases")
        sys.exit(0)
    filename = "User_Template"
else :
    print("default: invalid input")
    print("valid inputs are Automodel, Alignment, User_Template")
    sys.exit(0)
project_id = response.json()["project_id"]
print("project_id =",project_id)


# 获取结果
while True:
    time.sleep(10)
    response = requests.get(
        f"https://swissmodel.expasy.org/project/{ project_id }/models/summary/", 
        headers={ "Authorization": f"Token {token}" })
    status = response.json()["status"]
    print('Job status is now', status)
    if status in ["COMPLETED", "FAILED"]:
        break
response_object = response.json()
if response_object['status']=='COMPLETED':
    for model in response_object['models']:
        coordinates_url = model['coordinates_url']
        print("coordinates_url =",coordinates_url)
# Start a new job which will package all modelling jobs in a single zip archive
# If any jobs are still running, a download_id will not be available and the status code will be 400
response = requests.post(f"https://swissmodel.expasy.org/projects/download/", 
    headers={ "Authorization": f"Token {token}" })
# check that the status_code of the response is either 200 or 202 before proceeding
if response.status_code not in [200, 202]:
    print("response.text =",response.text)
    import sys
    sys.exit()
# Obtain the download_id for the packaged file
download_id = response.json()['download_id']


# 获取URL和本地路径
if args.output_type == 'ALL':
    while True:
        time.sleep(5)
        response = requests.get(
            f"https://swissmodel.expasy.org/projects/download/{ download_id }/", 
            headers={ "Authorization": f"Token {token}" })
        # Wait for the response status to be COMPLETED
        if response.json()['status'] in ['COMPLETED', 'FAILED']:
            break
    print("Fetch the results from", response.json()["download_url"])
    url = response.json()["download_url"]
    file = str(local_path)+'All_works.zip'
else: 
    print("Fetch the results from", coordinates_url)
    url = coordinates_url
    file = str(local_path)+'Structure_Prediction_Result.gz'
# 下载文件
r = requests.get(url)
if(os.path.exists(local_path) == False):
    os.makedirs(local_path)
with open(file, "wb") as code:
    code.write(r.content)
f_name = file.replace('.gz', '.pdb')
g_file = gzip.GzipFile(file)
open(f_name, "wb").write(g_file.read())
f_name = file.replace('.gz', '.txt')
open(f_name, "wb").write(g_file.read())
g_file.close()
time_end=time.time()
time_sum=time_end-time_start
print("runtime =",time_sum)

