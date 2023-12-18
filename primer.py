import subprocess
from flask import Flask, request, jsonify
from flask import render_template, url_for
import urllib

app = Flask(__name__)

pri_output_path="./primer_output.txt"#输出的路径
pri_input_path="./primer_input.txt"#输入的路径
pri_exe_path="./primer3/src/primer3_core"

@app.route('/')
def primer():
    return render_template('primer_design.html')

@app.route('/submit', endpoint='submit', methods=['GET', 'POST'])
def recordList():
    requestDict=request.form
    SEQUENCE_ID = str(request.form.get('id'))
    SEQUENCE_TEMPLATE = str(request.form.get('template'))
    PRIMER_TASK = str(request.form.get('task'))
    PRIMER_PICK_LEFT_PRIMER = str(request.form.get('left_primer'))
    PRIMER_PICK_INTERNAL_OLIGO = str(request.form.get('internal_oligo'))
    PRIMER_PICK_RIGHT_PRIMER = str(request.form.get('right_primer'))
    PRIMER_OPT_SIZE = str(request.form.get('opt_size'))
    PRIMER_MIN_SIZE = str(request.form.get('min_size'))
    PRIMER_MAX_SIZE = str(request.form.get('max_size'))
    PRIMER_PRODUCT_SIZE_RANGE_FROM = str(request.form.get('range_from'))
    PRIMER_PRODUCT_SIZE_RANGE_TO = str(request.form.get('range_to'))
    PRIMER_EXPLAIN_FLAG = str(request.form.get('explain_flag'))

    with open(f'{pri_input_path}','w') as f:
        f.write("SEQUENCE_ID="+SEQUENCE_ID+'\n')
        f.write("SEQUENCE_TEMPLATE="+SEQUENCE_TEMPLATE+'\n')
        f.write("PRIMER_TASK="+PRIMER_TASK+'\n')
        f.write("PRIMER_PICK_LEFT_PRIMER="+PRIMER_PICK_LEFT_PRIMER+'\n')
        f.write("PRIMER_PICK_INTERNAL_OLIGO="+PRIMER_PICK_INTERNAL_OLIGO+'\n')
        f.write("PRIMER_PICK_RIGHT_PRIMER="+PRIMER_PICK_RIGHT_PRIMER+'\n')
        f.write("PRIMER_OPT_SIZE="+PRIMER_OPT_SIZE+'\n')
        f.write("PRIMER_MIN_SIZE="+PRIMER_MIN_SIZE+'\n')
        f.write("PRIMER_MAX_SIZE="+PRIMER_MAX_SIZE+'\n')
        f.write("PRIMER_PRODUCT_SIZE_RANGE="+PRIMER_PRODUCT_SIZE_RANGE_FROM+'-'+PRIMER_PRODUCT_SIZE_RANGE_TO+'\n')
        f.write("PRIMER_EXPLAIN_FLAG="+PRIMER_EXPLAIN_FLAG+'\n')
        f.write("=")

    subprocess.run([f'{pri_exe_path}','--output',f'{pri_output_path}',f'{pri_input_path}'])
    
    blast_left_path="./blast_input/blast_left.fasta"
    blast_right_path="./blast_input/blast_right.fasta"
    blast_template_path="./blast_input/blast_template.fasta"
    blast_lr_path="./blast_input/blast_lr.fasta"
    blast_db_path="./blast_input/blast_db.fasta"
    match1="LEFT"
    match2="RIGHT"
    match3="SEQUENCE_TEMPLATE"
    left=[]
    right=[]
    i=0
    j=0

    from Bio.Blast.Applications import NcbiblastnCommandline
    from Bio.Blast.Applications import NcbimakeblastdbCommandline
    from Bio.Blast import NCBIXML

    with open(f'{pri_output_path}', 'r') as f2:
        line = f2.readline()
        while line:
            if ((line[14:21] == match3[0:7]) & ((line[7:10]) == match1[0:3])) : 
                left.insert(i,line[24:])
            elif((line[15:22] == match3[0:7]) & (line[7:11] == match2[0:4])): 
                right.insert(i,line[25:])
                i=i+1
            elif(line[0:16] == match3[0:16]): template=line[18:]
            line=f2.readline()
        while(j<i):
            f1=open(f'{blast_left_path}', 'w')
            f1.write(">LEFT"+str(j)+'\n')
            f1.write(left[j])
            f1.close()

            f1=open(f'{blast_right_path}', 'w')
            f1.write(">RIGHT"+str(j)+'\n')
            f1.write(right[j])
            f1.close()

            f1=open(f'{blast_template_path}', 'w')
            f1.write(">TEMPLATE"+str(j)+'\n')
            f1.write(template)
            f1.close()

            f1=open(f'{blast_lr_path}', 'w')
            f1.write(">LEFT"+str(j)+'\n')
            f1.write(left[j])
            f1.write(">RIGHT"+str(j)+'\n')
            f1.write(right[j])
            f1.close()

            f1=open(f'{blast_db_path}', 'w')
            f1.write(">LEFT"+str(j)+'\n')
            f1.write(left[j])
            f1.write(">RIGHT"+str(j)+'\n')
            f1.write(right[j])
            f1.write(">TEMPLATE"+str(j)+'\n')
            f1.write(template)
            f1.close()

            makedb=NcbimakeblastdbCommandline(input_file="./blast_input/blast_db.fasta", dbtype="nucl", out="./blast_input/template.fasta")
            stdout, stderr = makedb()

            # 设置BLAST程序的路径和参数
            blastn_cline = NcbiblastnCommandline(query="./blast_input/blast_lr.fasta", db="./blast_input/template.fasta", outfmt=1, out="blast_db_results"+str(j)+".txt", dust="no", word_size="11")
            stdout, stderr = blastn_cline()
            
            print("BLAST finished")

            # 读取BLAST结果文件
            #with open("blast_lr_results0.xml") as blast_file:
                #blast_records = NCBIXML.parse(blast_file)

                #for record in blast_records:
                    # 在这里处理每个比对结果
                    # 可以检查引物与模板的匹配位置、匹配得分等信息
                    # record.query, record.subject, record.query_start, record.query_end, record.subject_start, record.subject_end, record.score, 等等
                    #print(record)

            j=j+1

    response = jsonify({'ret': True, 'msg': '登录成功!'})
    response.status_code = 200

    return response
    

if __name__ == "__main__":
    app.config["JSON_AS_ASCII"] = False
    app.run(host='0.0.0.0', port='8080')
