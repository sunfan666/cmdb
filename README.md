# cmdb
Django Rest Framework 实现 CMDB 后端

```
在DEV环境下搭建 phoenix_cmdb_api
install on Centos 7
安装python 3.6
1 安装依赖
yum -y install gcc gcc-c++ ncurses ncurses-devel unzip zlib-devel zlib openssl-devel openssl readline-devel 

2 下载并安装python
wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
tar -xzf Python-3.6.6.tgz 
cd Python-3.6.6
./configure --prefix=/usr/local/python36
sudo make
sudo make install

3 配置pip
sudo tee /etc/pip.conf <<EOF
[global]
index-url = http://pypi.douban.com/simple
trusted-host = pypi.douban.com
[list]
format=columns
EOF

4 安装与初始化virtualenv
sudo /usr/local/python36/bin/pip3 install virtualenv
/usr/local/python36/bin/virtualenv ~/python36env

安装数据库
安装mariadb
sudo yum -y install mariadb mariadb-server mariadb-devel

配置mariadb
修改/etc/my.cnf，在[mysqld]下面增加如下几行配置
[mysqld]
default-storage-engine = innodb
innodb_file_per_table           
collation-server = utf8_general_ci
init-connect = 'SET NAMES utf8'
character-set-server = utf8

启动服务
sudo systemctl start mariadb
sudo systemctl enable mariadb

初始化mariadb
这里设置root密码为 123456
mysql_secure_installation

创建 phoenix_cmdb_api 数据库
mysql -uroot -p123456 -e "create database phoenix CHARACTER SET utf8;"

部署 phoenix_cmdb_api
下载源码
cd ~
git clone git@github.com:sunfan666/cmdb.git phoenix_cmdb_api

安装依赖包
cd phoenix_cmdb_api/
pip install -r requirements.txt 

另外：需要安装所需要的其他包，例如ldap,aliyunsdk等。
也可将所需包以及版本写入到requirement.txt文件中。
若安装包出现问题请自行百度。
pip install django-cors-headers
pip install django-filter
yum install openldap
yum install openldap-devel -y
yum install openssl-devel -y
pip install python-ldap
pip install django-auth-ldap
pip install aliyun-python-sdk-core-v3
pip install aliyun-python-sdk-ecs


修改配置文件
配置文件路径在 phoenix_cmdb_api/ops/settings.py

配置mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "phoenix",
        'USER': 'root',
        'PASSWORD': "123456",
        'HOST': "127.0.0.1",
        'PORT': "3306",
        'OPTIONS': {
            'init_command': "SET storage_engine=INNODB;SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

同步phoenix_cmdb_api表结果
在操作之前需要在phoenix_cmdb_api目录下创建一个logs的目录用于存放日志
mkdir logs

先生成user的迁移文件，然后同步
source ~/python36env/bin/activate
python manage.py makemigrations users
python manage.py migrate

接下来同步其它app的表结构
python manage.py makemigrations cabinet idcs manufacturers menu products servers vpcs zabbix
python manage.py migrate idcs
python manage.py migrate cabinet
python manage.py migrate manufacturers
python manage.py migrate products
python manage.py migrate menu
python manage.py migrate servers
python manage.py migrate vpcs
python manage.py migrate zabbix

创建管理员用户
python manage.py createsuperuser --username admin --email admin@domain.com

同步菜单
python scripts/import_menu.py

启动服务
python manage.py runserver 0.0.0.0:8000

接下来就可以访问啦：
http://your-ip:8000/ api root
http://your-ip:8000/docs/ api 文档
```
