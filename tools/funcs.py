




'''
@event: 将Cookie文本装换为 requests.cookies.RequestsCookieJar 对象
@envs:
@params:
    - cookieText:str cookie文本
@return:
    - success:bool 函数是否执行成功
    - detail:str 函数执行详情
    - cookieJar:requests.cookies.RequestsCookieJar 转换出来的cookiejar对象
@warning:
@eg:
'''
import requests.utils
def getRequestCookiejarFromText(cookieText):
    success,detail,cookieJar=True,"",None

    try:
        cookieText=cookieText.strip()
        cookieItems=[item for item in cookieText.split(";")]
        cookieDict={}
        for item in cookieItems:
            slice=item.split("=",1)
            cookieDict[slice[0].strip()]=slice[1].strip()
        cookieJar=requests.utils.cookiejar_from_dict(cookieDict)
    except Exception as e:
        success=False
        detail+=f"cookie获取失败,详情如下: {e}\n"
    return success,detail,cookieJar







'''
@event: 获取django的模板的内容,支持在 ./templatetags 中自定义 filters、tags 等过滤器或者标签
@envs:
    - pip install django==4.2.6 -i https://pypi.tuna.tsinghua.edu.cn/simple
@params:
    - templateText:str 模板字符串
    - map:dict 模板字符串中的变量
@return: 
    - success:bool 函数执行是否成功
    - detail:str 函数执行详情
    - text:str django模板字符串转换后的文本内容
@warning:
    - 如果使用自定义的过滤器或者标签,必须在templateText前面添加{% load filters %},filters为templatestags中的文件名
@eg:
if __name__ == '__main__':
    # filter测试
    from tools import funcs
    templateText="_{{ name|test_addtext:text }}"
    varsMap={"name":"geek007","text":"fasdfhkajsd"}
    success,detail,res=funcs.getDjangoTemplateContent(templateText,varsMap)
    print(success,detail,res)
    # simple_tag测试
    templateText = "_{% test_tag name pwd %}"
    varsMap = {"name":"geek007","pwd":"11"}
    success,detail,res=funcs.getDjangoTemplateContent(templateText, varsMap)
    print(success, detail, res)
'''
import os
import django
from django.conf import settings
from django.template import engines
# 初始化设置django配置
base_dir = os.path.dirname(os.path.dirname(__file__))
app_name = os.path.basename(os.path.dirname(__file__))
try:
    settings.configure(
        BASE_DIR=base_dir,DEBUG=True,INSTALLED_APPS=[app_name],APP_DIRS=True,
        TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates'}]
    )
    django.setup()
    django_engine = engines['django']
except Exception as e:
    print(f"django配置问题 => {e}")
def getDjangoTemplateContent(
        templateText:str,
        varsMap:dict,
):
    success,detail,text=True,"",""

    try:
        templateText="{% load filters %}{% load simple_tags %}"+templateText
        # 获取默认模板引擎
        template = django_engine.from_string(templateText)
        # 渲染模板
        text = template.render(varsMap)
    except Exception as e:
        success=False
        detail+=f"模板字符串解析错误,详情如下:\n {e}"
    # print(text)
    return success,detail,text



















