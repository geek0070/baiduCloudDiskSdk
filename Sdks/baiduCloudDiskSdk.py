

'''
event: baidu网盘的SDK
envs:
@eg:
from tools.Sdks.baiduCloudDiskSdk import BaiduDiskSdk
if __name__=="__main__":
    cookieText="xx"
    baiduDisk=BaiduDiskSdk(cookieText)
    # # 调用案例
    # # >> path>包括目录和文件, dir>只包括文件
    # 获取目录信息
    print(baiduDisk.getDirInfo("/AC_TempDownloads"))
    # 获取路径信息
    print(baiduDisk.getPathInfo("/AE_test/demo05_component.zip"))
    # 获取目录下的文件生成器
    for file in baiduDisk.getFilepathGeneratorUnderDir("/AC_TempDownloads",slice=3):
        print(file)
    # 创建目录
    baiduDisk.createDir("/AE_test/test1")
    # 重命名路径
    baiduDisk.renamePath("/AE_test/test1","test999")
    # 删除路径
    baiduDisk.deletePaths(["/AE_test/test999"])
    # 复制路径
    baiduDisk.copyPath(srcPath="/AE_test/test1",dstPath="/AE_test/test2")
    # 移动路径
    print(baiduDisk.movePath(srcPath="/AE_test/transferUrl.har",dstPath="/AE_test/test3/transferUrl.har"))
    # 获取路径的分享链接
    print(baiduDisk.getShareLink(paths=["/AE_test/test2","/AE_test/demo05_component.zip"],passwd="we87"))
    # 转存分享链接
    print(baiduDisk.transferShareLink(url="https://pan.baidu.com/s/1FeDbTaOoqpO_Rh87Fx_SuA",pwd="yymp",targetDir="/AE_test"))
    # 检测链接的有效性
    print(BaiduDiskSdk.checkShareUrl("https://pan.baidu.com/s/1MC0aUuL4Y26NlOtL8dR7yA",pwd="ljws")
'''



import json
import os
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from requests import session
from urllib.parse import urlencode
from tools import funcs
import re


DEFAULT_HEADERS={
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "pan.baidu.com",
    "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Referer":"https://pan.baidu.com/disk/main?from=homeFlow",
    "X-Requested-With":"XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}

# 百度SDK相关URL的模板,{{}}使用的是Django的模板字符串
BAIDU_URLS_TEMPLATES={
    "getTemplateUrl":"https://pan.baidu.com/api/gettemplatevariable" \
                "?clienttype=0" \
                "&app_id=250528" \
                "&web=1" \
                "&fields=%5B%22bdstoken%22%2C%22token%22%2C%22uk%22%2C%22isdocuser%22%2C%22servertime%22%5D",
    "getUserInfoUrl": "https://pan.baidu.com/rest/2.0/membership/user/info" \
                 "?method=query" \
                 "&clienttype=0" \
                 "&app_id=250528" \
                 "&web=1",
    "dirUrl": "https://pan.baidu.com/api/list" \
                 "?clienttype=0" \
                 "&app_id=250528" \
                 "&web=1" \
                 "&order=time" \
                 "&desc=1" \
                 "&{{ dirEncodeStr }}" \
                 "&num=100" \
                 "&page=1",
    "createUrl": "https://pan.baidu.com/api/create" \
                  "?a=commit" \
                  "&bdstoken={{ bdstoken }}" \
                  "&clienttype=0" \
                  "&app_id=250528" \
                  "&web=1",
    "deleteUrl": "https://pan.baidu.com/api/filemanager" \
                "?async=2" \
                "&onnest=fail" \
                "&opera=delete" \
                "&bdstoken={{ bdstoken }}" \
                "&newVerify=1" \
                "&clienttype=0" \
                "&app_id=250528" \
                "&web=1",
    "renameUrl": "https://pan.baidu.com/api/filemanager" \
                "?async=2" \
                "&onnest=fail" \
                "&opera=rename" \
                "&bdstoken={{ bdstoken }}" \
                "&clienttype=0" \
                "&app_id=250528" \
                "&web=1",
    "copyUrl": "https://pan.baidu.com/api/filemanager" \
                "?async=2" \
                "&onnest=fail" \
                "&opera=copy" \
                "&bdstoken={{ bdstoken }}" \
                "&clienttype=0" \
                "&app_id=250528" \
                "&web=1",
    "moveUrl": "https://pan.baidu.com/api/filemanager" \
                "?async=2" \
                "&onnest=fail" \
                "&opera=move" \
                "&bdstoken={{ bdstoken }}" \
                "&clienttype=0" \
                "&app_id=250528" \
                "&web=1" \
                "&dp-logid=82696300181613300051",
    "createShareUrl": "https://pan.baidu.com/share/set" \
                 "?channel=chunlei" \
                 "&bdstoken={{ bdstoken }}" \
                 "&clienttype=0" \
                 "&app_id=250528" \
                 "&web=1",
    "verifyUrl": "https://pan.baidu.com/share/verify" \
                "?t={{ t }}" \
                "&surl={{ surl }}" \
                "&channel=chunlei" \
                "&web=1" \
                "&app_id=250528" \
                "&bdstoken=" \
                "&logid={{ logid }}" \
                "&clienttype=0",
    "transferUrl": "https://pan.baidu.com/share/transfer" \
                "?shareid={{ shareid }}" \
                "&from={{ share_uk }}" \
                "&sekey={{ sekey }}" \
                "&channel=chunlei" \
                "&web=1" \
                "&app_id=250528" \
                "&bdstoken={{ bdstoken }}" \
                "&logid={{ logid }}" \
                "&clienttype=0",
}


class BaiduDiskSdk():
    def __init__(self,cookieText,headers=None):
        self.cookieText=cookieText.strip()
        self.headers=DEFAULT_HEADERS if headers==None else headers
        # 初始化用户信息
        self.setUser()

    # 获取用户相关信息
    # >> baiduDisk=BaiduDisk(headers,cookieText)
    # >> result: bdstoken / token / uk / username / photo
    def setUser(self):
        self.session = session()
        self.headers["Referer"]="https://pan.baidu.com/disk/main?from=homeFlow"
        self.headers["X-Requested-With"]="XMLHttpRequest"
        self.session.headers = self.headers
        _,_,self.session.cookies=funcs.getRequestCookiejarFromText(self.cookieText)
        self.user = {}
        # 获取template变量信息
        getTemplateUrl=BAIDU_URLS_TEMPLATES["getTemplateUrl"]
        templateResponse=self.session.get(getTemplateUrl)
        if not templateResponse.ok:
            raise Exception("template信息获取失败,bdstoken等数据获取失败!")
        else:
            templateResponseJsonDict=json.loads(templateResponse.text)
            # print(templateResponseJsonDict)
            self.user["bdstoken"]=templateResponseJsonDict["result"]["bdstoken"]
            self.user["token"]=templateResponseJsonDict["result"]["token"]
            self.user["uk"]=templateResponseJsonDict["result"]["uk"]
        # 获取用户信息
        getUserInfoUrl=BAIDU_URLS_TEMPLATES["getUserInfoUrl"]
        userResponse=self.session.get(getUserInfoUrl)
        if not userResponse.ok:
            raise Exception("获取用户信息失败!")
        else:
            userResponseJsonDict=json.loads(userResponse.text)
            # print(userResponseJsonDict)
            self.user["username"]=userResponseJsonDict["user_info"]["username"]
            self.user["photo"]=userResponseJsonDict["user_info"]["photo"]
        # 解析获取logid变量
        baiduId=self.session.cookies.get("BAIDUID")
        _,_,self.user["logid"]=funcs.getDjangoTemplateContent("{{baiduId|base64Encode}}",{"baiduId":baiduId})
        # print(self.user)
        return self.user

    # 获取目录的信息
    # >> baiduDisk.getDirInfo("/AC_TempDownloads")
    def getDirInfo(self,dirStr:str):
        dirDictInfo={"path":dirStr,"exist":True,"listdir":[]}

        self.session.headers.update(self.headers)
        dirUrl=BAIDU_URLS_TEMPLATES["dirUrl"]
        dirEncodeStr=urlencode({"dir":dirStr})
        _,_,dirUrl=funcs.getDjangoTemplateContent(dirUrl,{"dirEncodeStr":dirEncodeStr})
        dirInfoResponse=self.session.get(dirUrl)
        if not dirInfoResponse.ok:
            raise Exception(f"获取目录的路径信息失败,详情如下:\n {dirInfoResponse.text}")
        else:
            dirInfoResponseJsonDict=json.loads(dirInfoResponse.text)
            # print(dirInfoResponseJsonDict)
            if dirInfoResponseJsonDict["errno"]==0:
                allowFileKeys=["category","fs_id","dir_empty","isdir","share","path","empty","server_filename"]
                dirDictInfo["listdir"]=[{item[0]:item[1] for item in file.items() if item[0] in allowFileKeys}
                                     for file in dirInfoResponseJsonDict["list"]]
            else:
                dirDictInfo["listdir"]=[]
                dirDictInfo["exist"]=False
        # print(dirDictInfo)
        return dirDictInfo

    # 获取目录下的指定层数的文件的生成器,默认为0层,即获取所有文件的生成器
    # >> baiduDisk.getFilepathGeneratorUnderDir("/AC_TempDownloads/20230720/CE加速",slice=3)
    def getFilepathGeneratorUnderDir(self,dirStr:str,slice:int=0):
        def getFilepathGeneratorUnderDir_(dirStr_:str,slice_=1):
            dirDictInfo=self.getDirInfo(dirStr=dirStr_)
            for path in dirDictInfo["listdir"]:
                if path["isdir"]:
                    if slice<=0 or 0<slice_<slice:
                        yield from getFilepathGeneratorUnderDir_(dirStr_=path["path"],slice_=slice_+1)
                else:
                    if slice<=0 or slice_==slice:
                        yield path
        filepathGenerator=getFilepathGeneratorUnderDir_(dirStr)
        return filepathGenerator

    def getPathInfo(self,pathStr:str):
        pathInfo={"path":pathStr,"exist":True,"fileItems":[],"type":""}

        dirWherePath=os.path.dirname(pathStr)
        pathName=os.path.basename(pathStr)
        dirInfo=self.getDirInfo(dirWherePath)
        if dirInfo["exist"]:
            filterFiles=[file for file in dirInfo["listdir"] if file["server_filename"]==pathName]
            pathInfo["fileItems"]=filterFiles
            if len(filterFiles)==0:
                pathInfo["exist"]=False
            elif len(filterFiles)==1:
                pathInfo["exist"]=True
                if filterFiles[0]["isdir"]:
                    pathInfo["type"]="dir"
                else:
                    pathInfo["type"]="file"
            else:
                pathInfo["type"]="dir-file"
        else:
            pathInfo["exist"]=False
        # print(pathInfo)
        return pathInfo

    # 创建目录
    def createDir(self,dirStr:str):
        success,rdata=True,{}
        self.session.headers.update(self.headers)

        bdstoken=self.user["bdstoken"]
        createUrlTemplate = BAIDU_URLS_TEMPLATES["createUrl"]
        _,_,createUrl=funcs.getDjangoTemplateContent(createUrlTemplate,varsMap={"bdstoken":bdstoken})
        data={
            "path": dirStr,
            "isdir": 1,
            "block_list": [],
        }
        createDirResponse=self.session.post(createUrl,data)
        createDirResponseJsonDict = json.loads(createDirResponse.text)
        rdata=createDirResponseJsonDict.copy()
        # print(createDirResponseJsonDict)
        if not createDirResponse.ok:
            raise Exception(f"目录创建失败,返回的ok!=True,详情 => {createDirResponseJsonDict} !!!")
        if createDirResponseJsonDict["errno"]!=0:
            success=False
        return success,rdata

    # 删除路径
    def deletePaths(self,paths:list[str]):
        success,rdata=True,{}

        bdstoken = self.user["bdstoken"]
        deleteUrlTemplate=BAIDU_URLS_TEMPLATES["deleteUrl"]
        _,_,deleteUrl=funcs.getDjangoTemplateContent(deleteUrlTemplate,varsMap={"bdstoken":bdstoken})
        data={
            "filelist":json.dumps(paths,ensure_ascii=False)
        }
        deleteReponse=self.session.post(deleteUrl,data=data)
        deleteReponseJsonDict = json.loads(deleteReponse.text)
        if not deleteReponse.ok:
            raise Exception(f"删除路径失败,详情 => {deleteReponseJsonDict}")
        if deleteReponseJsonDict["errno"]!=0:
            success=False
            rdata=deleteReponseJsonDict
        return success,rdata

    # 重命名 路径<pathStr>的名字为<newName>
    def renamePath(self,pathStr:str,newName:str):
        success, rdata = True, {}

        bdstoken = self.user["bdstoken"]
        renameUrlTemplate=BAIDU_URLS_TEMPLATES["renameUrl"]
        _,_,renameUrl=funcs.getDjangoTemplateContent(renameUrlTemplate,varsMap={"bdstoken":bdstoken})
        data = {
            "filelist": json.dumps([
                {
                    "path":pathStr,
                    "newname":newName
                }
            ])
        }
        renameReponse = self.session.post(renameUrl, data=data)
        renameReponseJsonDict = json.loads(renameReponse.text)
        # print(renameReponseJsonDict)
        if not renameReponse.ok:
            raise Exception(f"重命名路径失败,详情 => {renameReponseJsonDict}")
        if renameReponseJsonDict["errno"] != 0:
            success = False
            rdata = renameReponseJsonDict
        return success, rdata

    # 复制路径,可以复制目录
    def copyPath(self,srcPath,dstPath):
        success,rdata=True,{}

        bdstoken = self.user["bdstoken"]
        copyUrlTemplate=BAIDU_URLS_TEMPLATES["copyUrl"]
        _,_,copyUrl=funcs.getDjangoTemplateContent(copyUrlTemplate,varsMap={"bdstoken":bdstoken})
        data={
            "filelist": json.dumps([
                {
                    "path": srcPath,
                    "dest": os.path.dirname(dstPath),
                    "newname": os.path.basename(dstPath)
                }
            ],ensure_ascii=False)
        }
        copyResponse=self.session.post(copyUrl,data=data)
        copyResponseJsonDict=json.loads(copyResponse.text)
        if not copyResponse.ok:
            raise Exception(f"复制路径失败,详情 => {copyResponseJsonDict}")
        if copyResponseJsonDict["errno"]!=0:
            success=False
            rdata=copyResponseJsonDict
        return success,rdata

    # 移动路径,目录失败
    def movePath(self,srcPath:str,dstPath:str):
        success, rdata = True, {}

        bdstoken = self.user["bdstoken"]
        moveUrlTemplate=BAIDU_URLS_TEMPLATES["moveUrl"]
        _,_,moveUrl=funcs.getDjangoTemplateContent(moveUrlTemplate,varsMap={"bdstoken":bdstoken})
        data={
            "filelist": json.dumps([
                {
                    "path": srcPath,
                    "dest": os.path.dirname(dstPath),
                    "newname": os.path.basename(dstPath)
                }
            ],ensure_ascii=False)
        }
        moveResponse=self.session.post(moveUrl,data=data)
        moveResponseJsonDict=json.loads(moveResponse.text)
        print(moveResponseJsonDict)
        if not moveResponse.ok:
            raise Exception(f"移动路径失败,详情 => {moveResponseJsonDict}")
        if moveResponseJsonDict["errno"]!=0:
            success=False
            rdata=moveResponseJsonDict
        return success,rdata

    # 根据路径字符串集合和四位数验证码获取分享链接信息; period: 分享的有效期,分为 永久/30/7/1
    def getShareLink(self,paths:list[str],passwd:str,period:str="永久"):
        success,detail,rdata=True,"",{"link":"","pwd":""}

        periodsMap={"永久":0,"7":7,"1":1,"30":30}
        bdstoken = self.user["bdstoken"]
        createShareUrlTemplate=BAIDU_URLS_TEMPLATES["createShareUrl"]
        _,_,createShareUrl=funcs.getDjangoTemplateContent(createShareUrlTemplate,varsMap={"bdstoken":bdstoken})
        allSuccessGetIds=True
        allFileIds=[]
        for pathStr in paths:
            pathInfo=self.getPathInfo(pathStr=pathStr)
            if not pathInfo["exist"]:
                success=False
                allSuccessGetIds=False
                detail+=f"路径不存在 => {pathStr}\n"
                break
            else:
                allFileIds.append(pathInfo["fileItems"][0]["fs_id"])
        if allSuccessGetIds:
            data={
                "period":periodsMap[period],
                "pwd":passwd,
                "eflag_disable":True,
                "channel_list":[],
                "schannel":4,
                "fid_list":json.dumps(allFileIds,ensure_ascii=False)
            }
            createShareUrlResponse=self.session.post(createShareUrl,data=data)
            createShareUrlResponseJsonDict=json.loads(createShareUrlResponse.text)
            # print(createShareUrlResponse.text)
            if not createShareUrlResponse.ok:
                raise Exception(f"创建分享链接失败,详情 => {createShareUrlResponse.text}")
            else:
                rdata["link"]=createShareUrlResponseJsonDict["link"]
                rdata["pwd"]=passwd
        # print(success,detail,rdata)
        return success,detail,rdata

    # 转存分享链接到目标目录<targetDir>中,目录不存在将自动创建
    def transferShareLink(self,url:str,pwd:str,targetDir:str):
        success,detail=True,""
        
        dirInfo=self.getDirInfo(targetDir)
        if not dirInfo["exist"]:
            self.createDir(targetDir)
            print(f"目录不存在,创建完成 => {targetDir}")

        logid=self.user['logid']
        bdstoken=self.user['bdstoken']

        # 验证请求
        surl=url.rsplit("/")[-1][1:]
        t=int(time.time()*1000)
        # print(surl,t)
        verifyUrlTemplate=BAIDU_URLS_TEMPLATES["verifyUrl"]
        _,_,verifyUrl=funcs.getDjangoTemplateContent(verifyUrlTemplate,varsMap={"t":t,"surl":surl,"logid":logid})
        verifyData={
            "pwd": pwd,
            "vcode": "",
            "vcode_str": "",
        }
        success_verift=True
        verifyResponse=self.session.post(verifyUrl,data=verifyData)
        verifyResponseJsonDict=json.loads(verifyResponse.text)
        if verifyResponseJsonDict["errno"]==0:
            self.session.cookies.set("BDCLND",verifyResponseJsonDict["randsk"])
        else:
            success=False
            success_verift=False
            detail+="url验证失败,verity url返回的errno!=0"

        if success_verift:
            # 分享链接
            mergeSharedUrl=f"{url}?pwd={pwd}"
            response=self.session.get(mergeSharedUrl)
            # print(response.text)
            match=re.search(r'locals\.mset\((.+?)\);.+?window\.BadSDK',response.text,flags=re.DOTALL)
            extractShareInfoDict={}
            success_get_share_info=True
            if match!=None:
                shareInfoJsonDict = json.loads(match.groups()[0])
                # print(json.dumps(shareInfoJsonDict))
                if shareInfoJsonDict["errno"]==0:
                    extractShareInfoDict["uk"]=shareInfoJsonDict["uk"]
                    extractShareInfoDict["share_uk"]=shareInfoJsonDict["share_uk"]
                    extractShareInfoDict["shareid"]=shareInfoJsonDict["shareid"]
                    extractFileKeys=["fs_id","isdir","oper_id"]
                    extractShareInfoDict["file_list"]=[{item[0]:item[1] for item in file.items()
                                                        if item[0] in extractFileKeys} for file
                                                       in shareInfoJsonDict["file_list"]]
                    # print(extractShareInfoDict)
                else:
                    success_get_share_info=False
                    # print("匹配的信息的errno!=0")
                    detail+="匹配的信息的errno!=0 \n"
            else:
                success_get_share_info = False
                # print("没有匹配到分享信息")
                detail += "没有匹配到分享信息 \n"

            # transfer api进行转存
            if success_get_share_info:
                shareid=extractShareInfoDict["shareid"]
                share_uk=extractShareInfoDict["share_uk"]
                sekey=self.session.cookies.get_dict()["BDCLND"]
                transferUrlTemplate=BAIDU_URLS_TEMPLATES["transferUrl"]
                _,_,transferUrl=funcs.getDjangoTemplateContent(transferUrlTemplate,varsMap={"shareid":shareid,"share_uk":share_uk,"sekey":sekey,"bdstoken":bdstoken,"logid":logid})
                data={
                    "fsidlist": json.dumps([int(file["fs_id"]) for file in extractShareInfoDict["file_list"]]),
                    "path": targetDir
                }
                transferResponse=self.session.post(transferUrl,data=data)
                transferResponseJsonDict=json.loads(transferResponse.text)
                if transferResponseJsonDict["errno"]==4:
                    success = False
                    # print(f"转存失败,文件已经转存过了,请勿重复!")
                    detail+=f"转存失败,文件已经转存过了,请勿重复! \n"
                elif transferResponseJsonDict["errno"]!=0:
                    success = False
                    # print(f"转存失败,详情如下 => {transferResponseJsonDict['show_msg']}")
                    detail+=f"转存失败,详情如下 => {transferResponseJsonDict['show_msg']} \n"
            else:
                success=False
        return success,detail

    # 检测链接的有效性
    @staticmethod
    def checkShareUrl(url:str,pwd:str):
        valid=True

        shareUrl=f"{url}?pwd={pwd}"
        thisSession = session()
        resp=thisSession.get(shareUrl)
        match=re.search(r'<div id="submitBtn" class="submit-btn-text">提取文件</div>',resp.text)
        # print(match)
        if match == None:
            valid = False
            # print(resp.text)

        return valid
















