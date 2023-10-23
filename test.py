

from Sdks.baiduCloudDiskSdk import BaiduDiskSdk

cookieText='''newlogin=1; PSTM=1697075780; BIDUPSID=2E69D044C5CA88F6D0976DC48B7DDDD2; BAIDUID=20082437DDAA4A9082832F585A1F4A6A:FG=1; '''
baiduDisk=BaiduDiskSdk(cookieText)
print(baiduDisk.getDirInfo("/tests"))




