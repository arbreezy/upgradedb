# upgradedb
Upgrade MySql Database running migrations sql scripts ~ PoC

Setting DB and *.sql files:  

Fedora 28:
  dnf install https://dev.mysql.com/get/mysql80-community-release-fc28-1.noarch.rpm
  dnf --disablerepo=mysql80-community --enablerepo=mysql57-community install mysql-communi    ty-server
  
  systemctl start mysqld.service . 
  $ grep 'A temporary password is generated for root@localhost' /var/log/mysqld.log |tail -1 . 
  secure installation -> new root pass: th3m0stS3cur3_  
  Create/Confidure example DB:  
  CREATE DATABASE ecsexample;  
  CREATE USER 'breezy'@'localhost' IDENTIFIED BY 'th3s3condMostsecure_';  
  Give access to user breezy for the example DB:  
  GRANT ALL ON ecsexample.* TO 'breezy'@'localhost'; FlUSH PRIVILEGES;  
 
  breezy passw : th3s3condMostsecure_ . 
  
  POC:  
  
  use ecsexample .  
  CREATE TABLE versionTable( version int NOT NULL PRIMARY KEY);    
  INSERT INTO versionTable VALUES("050");   
  CREATE TABLE Persons ( LastName varchar(255), FirstName varchar(255) );  
  
  create example sql scripts
  $ mkdir sqldir && touch 79.test.sql 30.test.sql 055\ test.sql
  
 $ cat 79.test.sql
 INSERT INTO Persons VALUES ("Hamm" , "John");
 
 $ git clone https://github.com/arbreezy/upgradedb.git && cd upgradedb && python setup.py install
 
 $ sqlupgrade.py /home/fedora/sqldir breezy  localhost  ecsexample  th3s3condMostsecure_
 
PS: Log file lives under the dirpath you provide as an argument
