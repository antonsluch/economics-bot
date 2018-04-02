import pandas as pd
import requests
import json


def save_to_img(token, file_path, file_name):
    link = 'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_path)
    r = requests.get(link)
    f = open('img/'+file_name, 'wb+')
    f.write(r.content)
    f.close()


def get_src(link):
    r = requests.get(link)
    page = r.text
    start = page.index('<script id="models-client" type="application/json">')
    page1 = page[start+51:]
    end = page1.index('</script>')

    f = open('data.json', 'w+')
    f.write(page1[:end])
    f.close()
    x = json.load(open('data.json', 'r'))
    answer = 'https:'+x[5]['data']['meta']['sizes'][0]['url']
    return answer

if __name__ == '__main__':
    #link = 'https://yadi.sk/i/TUMmWyQE3RFzfc'
    #print(get_src(link))
    pass