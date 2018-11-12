### 启动 FTP 服务的两种方式
## 1. 通过脚本启动
```
./start.sh
```
这种方式会读取config.json配置文件，修改该配置文件指向对应的ceph服务和ftp服务所开的端口。

## 2. 直接通过python启动ftp服务：
```
python ossftp/ftpserver.py --listen_address=0.0.0.0 --port=2048 --bucket_endpoints=192.168.32.200
```
