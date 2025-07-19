import json

#* cleans and parses the response to json
def clean_content(response):
    content = response.strip('```').replace('json', '')
    clean_content = content.replace('`','')
    return json.loads(clean_content)

