## 一.本地开发  
### 1.初始化环境,此命令需为第一条运行的命令
./develop.sh init

### 2.更新本地镜像
./develop.sh upgrade [serverName1, [serverName2]...]

### 3.更新远程镜像  
./develop.sh commit [serverName1, [serverName2]...]

### 4.重构  
./develop.sh rebuild

## 二.服务端部署  
### 1.启动主服务(www、database)
./deploy.sh start

### 2.停止 
./deploy.sh stop

### 3.重启  
./deploy.sh restart

### 4.更新  
./deploy.sh pull serverName1, [serverName2]...

## 备份和恢复
### 1. 备份
备份任务由cron定期执行(cron脚本位于conf/cronjobs), 备份路径映射到本机的volume/backup下。备份最多不超过30天的数据。备份文件名格式为 timestamp.scheme_name.sql.gz

### 2. 恢复
将从volume/backup路径下获取到的备份文件移到volume/restore文件夹下，当启动服务后会自动执行sql脚本恢复数据。
注：恢复数据的时候可能会有重复的数据，会导致数据库启动失败。

