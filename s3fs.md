### vsftp + s3fs

## s3fs 安装
```
apt-get install s3fs
mkdir /app/s3fs
radosgw-admin user info --uid=jitstack
echo '0X68CBIN3DQOYZJUFD9W:rIqjQdPiyEHGScBwunisAO2ADPW2X1vGOb6gP94x' > /etc/passwd-s3fs
```

## s3fs 手动挂载
```
s3fs kevin /app/s3fs -o url=http://192.168.32.200:80 -o passwd_file=/etc/passwd-s3fs -o use_path_request_style
# mount | grep s3fs
# umount /app/s3fs
```

## s3fs 自动挂载
```
cat /etc/fstab
...

s3fs#kevin /app/s3fs fuse _netdev,allow_other,use_path_request_style,url=http://192.168.32.200:80/ 0 0
# mount | grep s3fs
```

## ftp安装
```
useradd -m -d /app/s3fs/ftpuser001 -k /etc/skel -s /bin/bash ftpuser001
```

## ftp 配置
```
# cat /etc/vsftpd.conf
write_enable=YES

systemctl restart vsftpd.service
```
