# -*- coding: utf-8 -*-
import re


def is_ans(ans):
    pattern = re.compile('[a-z,_]{1,100}[0-9]{1,3}-[0-9]{1,2}')
    m = pattern.match(ans)
    if m != None:
        return m.group() == ans
    return False

def split_ans(ans):
    pattern = re.compile('[a-z,_]{1,100}')
    topic = pattern.match(ans).group()
    num = ans[len(topic):]
    task, var = num.split('-')
    return (topic, task, var)
    
def increment(ans):
    topic, task, var = split_ans(ans)
    return topic+str(int(task)+1)

if __name__ == '__main__':
    print(split_ans('sss2-99'))