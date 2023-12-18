import requests
import gzip

search = "GFP" # 搜索词条

response = requests.get("https://rest.uniprot.org/uniprotkb/search?compressed=true&format=fasta&query=%28"+search+"%29&size=10")

contents = gzip.decompress(response.content)

# with open('test.txt', 'wb') as f:
#     f.write(data)

# print(data.decode('utf-8'))
contents = contents.decode('utf-8')
contents = contents.split('>')[1:]

new_contents = ""

for item in contents:
    item = ">" + item
    withhead = item.split('\n',1)
    # item = withhead[0] + "\n" + withhead[1][:200] + "\n"
    if len(withhead[1]) <= 305:
        new_contents += item
    
with open('input.txt', "w") as f:
    f.write(new_contents)
