
from django import template

register = template.Library()

@register.filter(name='test_addtext')
def test_filter(text,add_part):
    return text+f"_{add_part}"+"_test_filter"








'''
@event: 将文本字符串编码成base64字符串
@envs:
@params:
    - text:str 需要进行base64编码的文本内容
    - encoding:str text的编码方式
@return:
    - result:str text的base64编码字符串
'''
import base64
@register.filter(name='base64Encode')
def base64Encode(text:str,encoding:str="utf-8"):
    byte_string = text.encode(encoding)
    # 进行Base64编码
    base64_string = base64.b64encode(byte_string)
    result = base64_string.decode(encoding)
    return result







'''
@event: 将base64文本字符串解码成普通字符串
@envs:
@params:
    - base64String:str 需要进行base64解码的文本内容
    - encoding:str 编码方式
@return:
    - result:str base64字符串解码的字符串
'''
import base64
@register.filter(name='base64Decode')
def base64Decode(base64String:str,encoding="utf-8"):
    byte_string = base64.b64decode(base64String)
    # 将字节流转换为字符串
    result = byte_string.decode(encoding)
    return result







'''
@event: 计算文本的hash值
@envs: 
@params:
    - text:str 进行hash的文本对象
    - type:str 计算的hash值得类型,可以取 md5/sha1/sha256 几个类型
@return:
    - result:text hash值
@warning:
@eg: 
if __name__ == '__main__':
    from tools import funcs
    text="123"
    res=funcs.getDjangoTemplateContent("{{text|hash:'md5'}}",{"text":text})
    print(res)
    res=funcs.getDjangoTemplateContent("{{text|hash:'sha1'}}",{"text":text})
    print(res)
    res=funcs.getDjangoTemplateContent("{{text|hash:'sha256'}}",{"text":text})
    print(res)
'''
import hashlib
@register.filter(name='hash')
def hash(text:str,type:str="md5"):
    if type=="md5":
        # 创建一个MD5对象
        md5_hash = hashlib.md5()
        # 将变量转换为字节串并更新MD5对象
        md5_hash.update(text.encode("utf-8"))
        # 计算MD5值并返回结果
        result = md5_hash.hexdigest()
    elif type=="sha1":
        # 创建一个SHA-1对象
        sha1_hash = hashlib.sha1()
        # 将变量转换为字节串并更新SHA-1对象
        sha1_hash.update(text.encode("utf-8"))
        # 计算SHA-1值并返回结果
        result = sha1_hash.hexdigest()
    elif type=="sha256":
        # 创建一个SHA-256对象
        sha256_hash = hashlib.sha256()
        # 更新SHA-256对象以包含data的字节表示形式
        sha256_hash.update(text.encode('utf-8'))
        # 计算SHA-256哈希值
        result = sha256_hash.hexdigest()
    else:
        result=""
    return result














