from Crypto.Cipher import AES
import requests
import re
import m3u8
import time
import threading
import os

# 动态区域
url_list=[
    'http://hls.videocc.net/b034527feb/3/b034527feb419e934e4f8788ac04c2b3_3.m3u8?pid=1676627864962X1711228&device=desktop'
]#在这里天上你要下载的m3u8文件的URL
token_list=[
    '?token=41b188c4-64bf-4cd2-b092-6728fc19da84-50'
]
path_list=[
    '高数/第二章 一元函数微分学(2022)/考点四 导数的应用/',
]
title_list=[
    '导数的应用',
]
# 动态区域

key_list=['']
def get_file(url,count):
    resp=requests.request('GET',url)
    # print(resp.content)
    with open('./m3u8_link/'+str(title_list[count])+'.m3u8','wb') as f:
        f.write(resp.content)

def get_key(path,count):
    with open(path, 'rb') as f:
        file_content=str(f.read())
    print(file_content)
    key_link = re.search('URI=\"(.*?)\"', file_content).group(1)
    key=requests.request('GET',key_link + token_list[count]).content
    return key

def get_ts_list(path):
    m3u8_obj = m3u8.load(path)
    ts_urls = []
    for i, seg in enumerate(m3u8_obj.segments):
        # if i<=100:
            ts_urls.append(seg.uri)
    # print(ts_urls)
    return ts_urls

def download(ts_urls,key,iv,count,path):
    name=path
    print("视频",count,"需要下载的文件长度为", len(ts_urls))
    for i in range(len(ts_urls)):
        ts_url=ts_urls[i]
        if i%10==0:
            print("视频",count,"当前下载进度：",str(i/len(ts_urls)*100)[:4],'%')
        # 如果连接末尾没有.ts手动加上
        ts_name = ts_url.split("/")[-1] + '.ts'  # ts文件名
        # print(ts_name)

        # 解密，new有三个参数，
        # 第一个是秘钥（key）的二进制数据，
        # 第二个使用下面这个就好
        # 第三个IV在m3u8文件里URI后面会给出，如果没有，可以尝试把秘钥（key）赋值给IV
        sprytor = AES.new(key, AES.MODE_CBC,iv)

        # 获取ts文件二进制数据
        # print("正在下载：" + ts_name)

        ts = requests.get(ts_url).content
        # 密文长度不为16的倍数，则添加b"0"直到长度为16的倍数
        while len(ts) % 16 != 0:
            ts += b"0"
        # 写入mp4文件
        with open(name, "ab") as file:
            # # decrypt方法的参数需要为16的倍数，如果不是，需要在后面补二进制"0"
            file.write(sprytor.decrypt(ts))
            # print("保存成功：" + ts_name)
    print(name, "下载完成")


def main(count):
    url=url_list[count]
    get_file(url,count)
    key=get_key('./m3u8_link/'+str(title_list[count])+'.m3u8', count)
    key_list.append(key)
    print('下载完成！！密钥生成完成！！')
    ts_urls=get_ts_list('./m3u8_link/'+str(title_list[count])+'.m3u8')
    iv=key
    save_path = './video/' + path_list[count]
    if os.path.exists(save_path):
        print(f'文件夹{save_path}已存在！')
    else:
        os.makedirs(save_path)
    path=save_path + str(title_list[count])+'.mp4'
    download(ts_urls,key,iv,title_list[count],path)
    print("视频",title_list[count],"下载完成!!")

if __name__=="__main__":
    start=time.time()
    threading_list=[]
    start_time = time.time()
    for i in range(len(url_list)):
    # for i in range(0,2):
        # time.sleep(0.05)
        t = threading.Thread(target=main, args=(i,))
        t.start()
        threading_list.append(t)
    for t in threading_list:
        t.join()
    end=time.time()
    print("程序运行结束！！！用时：",end-start,"s")