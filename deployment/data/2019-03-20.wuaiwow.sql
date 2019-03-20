-- MySQL dump 10.13  Distrib 5.7.24, for Linux (x86_64)
--
-- Host: localhost    Database: wuaiwow
-- ------------------------------------------------------
-- Server version	5.7.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('fcb94762f144');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `character`
--

DROP TABLE IF EXISTS `character`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `character` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guid` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `level` int(11) NOT NULL,
  `_race` varchar(255) NOT NULL,
  `race_id` varchar(50) NOT NULL,
  `_job` varchar(255) NOT NULL,
  `side` varchar(40) DEFAULT NULL,
  `gender` varchar(255) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `played_time` varchar(100) NOT NULL,
  `money` varchar(256) NOT NULL,
  `alive` tinyint(1) DEFAULT NULL,
  `update` datetime DEFAULT NULL,
  `isSuccess` tinyint(1) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guid` (`guid`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `character_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `character`
--

LOCK TABLES `character` WRITE;
/*!40000 ALTER TABLE `character` DISABLE KEYS */;
/*!40000 ALTER TABLE `character` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `info_donate`
--

DROP TABLE IF EXISTS `info_donate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `info_donate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `info` text,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `info_donate`
--

LOCK TABLES `info_donate` WRITE;
/*!40000 ALTER TABLE `info_donate` DISABLE KEYS */;
/*!40000 ALTER TABLE `info_donate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `info_guild`
--

DROP TABLE IF EXISTS `info_guild`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `info_guild` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `info` text,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `info_guild`
--

LOCK TABLES `info_guild` WRITE;
/*!40000 ALTER TABLE `info_guild` DISABLE KEYS */;
/*!40000 ALTER TABLE `info_guild` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log` (
  `Created` text,
  `Name` text,
  `LogLevel` int(11) DEFAULT NULL,
  `LogLevelName` text,
  `Message` text,
  `Args` text,
  `Module` text,
  `FuncName` text,
  `LineNo` int(11) DEFAULT NULL,
  `Exception` text,
  `Process` int(11) DEFAULT NULL,
  `Thread` text,
  `ThreadName` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
/*!40000 ALTER TABLE `log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(512) NOT NULL,
  `content` text,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message`
--

LOCK TABLES `message` WRITE;
/*!40000 ALTER TABLE `message` DISABLE KEYS */;
/*!40000 ALTER TABLE `message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `news`
--

DROP TABLE IF EXISTS `news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(256) NOT NULL,
  `summary` varchar(256) NOT NULL,
  `image_url` varchar(256) NOT NULL,
  `content` text,
  `created` datetime DEFAULT NULL,
  `update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `news`
--

LOCK TABLES `news` WRITE;
/*!40000 ALTER TABLE `news` DISABLE KEYS */;
/*!40000 ALTER TABLE `news` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permission`
--

DROP TABLE IF EXISTS `permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `value` (`value`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permission`
--

LOCK TABLES `permission` WRITE;
/*!40000 ALTER TABLE `permission` DISABLE KEYS */;
INSERT INTO `permission` VALUES (1,10),(2,15),(3,20),(4,25),(5,30),(6,35),(7,40),(8,98),(9,99),(10,100);
/*!40000 ALTER TABLE `permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permission_role_association`
--

DROP TABLE IF EXISTS `permission_role_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permission_role_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) DEFAULT NULL,
  `permission_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `permission_id` (`permission_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `permission_role_association_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `permission` (`id`),
  CONSTRAINT `permission_role_association_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permission_role_association`
--

LOCK TABLES `permission_role_association` WRITE;
/*!40000 ALTER TABLE `permission_role_association` DISABLE KEYS */;
INSERT INTO `permission_role_association` VALUES (1,1,1),(2,2,2),(3,1,2),(4,3,3),(5,1,3),(6,2,3),(7,4,4),(8,1,4),(9,2,4),(10,3,4),(11,5,5),(12,1,5),(13,2,5),(14,3,5),(15,4,5),(16,6,6),(17,1,6),(18,2,6),(19,3,6),(20,4,6),(21,5,6),(22,7,7),(23,1,7),(24,2,7),(25,3,7),(26,4,7),(27,5,7),(28,6,7),(29,8,8),(30,1,8),(31,2,8),(32,3,8),(33,4,8),(34,5,8),(35,6,8),(36,7,8),(37,9,9),(38,1,9),(39,2,9),(40,3,9),(41,4,9),(42,5,9),(43,6,9),(44,7,9),(45,8,9),(46,10,10),(47,1,10),(48,2,10),(49,3,10),(50,4,10),(51,5,10),(52,6,10),(53,7,10),(54,8,10),(55,9,10);
/*!40000 ALTER TABLE `permission_role_association` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prompt_alive`
--

DROP TABLE IF EXISTS `prompt_alive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prompt_alive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prompt` varchar(256) NOT NULL,
  `alive` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prompt_alive`
--

LOCK TABLES `prompt_alive` WRITE;
/*!40000 ALTER TABLE `prompt_alive` DISABLE KEYS */;
/*!40000 ALTER TABLE `prompt_alive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prompt_gender`
--

DROP TABLE IF EXISTS `prompt_gender`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prompt_gender` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prompt` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prompt_gender`
--

LOCK TABLES `prompt_gender` WRITE;
/*!40000 ALTER TABLE `prompt_gender` DISABLE KEYS */;
/*!40000 ALTER TABLE `prompt_gender` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prompt_job`
--

DROP TABLE IF EXISTS `prompt_job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prompt_job` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prompt` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prompt_job`
--

LOCK TABLES `prompt_job` WRITE;
/*!40000 ALTER TABLE `prompt_job` DISABLE KEYS */;
/*!40000 ALTER TABLE `prompt_job` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prompt_level`
--

DROP TABLE IF EXISTS `prompt_level`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prompt_level` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prompt` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prompt_level`
--

LOCK TABLES `prompt_level` WRITE;
/*!40000 ALTER TABLE `prompt_level` DISABLE KEYS */;
/*!40000 ALTER TABLE `prompt_level` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prompt_money`
--

DROP TABLE IF EXISTS `prompt_money`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prompt_money` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prompt` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prompt_money`
--

LOCK TABLES `prompt_money` WRITE;
/*!40000 ALTER TABLE `prompt_money` DISABLE KEYS */;
/*!40000 ALTER TABLE `prompt_money` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prompt_race`
--

DROP TABLE IF EXISTS `prompt_race`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prompt_race` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prompt` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prompt_race`
--

LOCK TABLES `prompt_race` WRITE;
/*!40000 ALTER TABLE `prompt_race` DISABLE KEYS */;
/*!40000 ALTER TABLE `prompt_race` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recruit`
--

DROP TABLE IF EXISTS `recruit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recruit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recruit`
--

LOCK TABLES `recruit` WRITE;
/*!40000 ALTER TABLE `recruit` DISABLE KEYS */;
/*!40000 ALTER TABLE `recruit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role` varchar(50) NOT NULL,
  `label` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'CHRACE','变种族'),(2,'CUSTOMIZE','性别'),(3,'UPLEVEL','升级'),(4,'GETMONEY','金币'),(5,'GETITEMS','套装'),(6,'PORTAL','传送门'),(7,'MOUNTS','座机'),(8,'GM','游戏管理员'),(9,'UPGRADE','站点管理员'),(10,'ADMIN','超级管理员');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sidebar`
--

DROP TABLE IF EXISTS `sidebar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sidebar` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `image_url` varchar(256) NOT NULL,
  `content` text,
  `created` datetime DEFAULT NULL,
  `update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sidebar`
--

LOCK TABLES `sidebar` WRITE;
/*!40000 ALTER TABLE `sidebar` DISABLE KEYS */;
/*!40000 ALTER TABLE `sidebar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_result`
--

DROP TABLE IF EXISTS `task_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` varchar(50) NOT NULL,
  `task_name` varchar(50) NOT NULL,
  `create_time` datetime DEFAULT NULL,
  `args` varchar(256) DEFAULT NULL,
  `kwargs` varchar(256) DEFAULT NULL,
  `err_code` varchar(50) DEFAULT NULL,
  `exc_msg` varchar(256) DEFAULT NULL,
  `status` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_result`
--

LOCK TABLES `task_result` WRITE;
/*!40000 ALTER TABLE `task_result` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_agreement`
--

DROP TABLE IF EXISTS `user_agreement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_agreement` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` text,
  `update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_agreement`
--

LOCK TABLES `user_agreement` WRITE;
/*!40000 ALTER TABLE `user_agreement` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_agreement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_ip`
--

DROP TABLE IF EXISTS `user_ip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_ip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login_time` datetime DEFAULT NULL,
  `province` varchar(256) DEFAULT NULL,
  `city` varchar(250) DEFAULT NULL,
  `district` varchar(256) DEFAULT NULL,
  `street` varchar(256) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_ip_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_ip`
--

LOCK TABLES `user_ip` WRITE;
/*!40000 ALTER TABLE `user_ip` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_ip` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_message_association`
--

DROP TABLE IF EXISTS `user_message_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_message_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `has_read` tinyint(1) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `message_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `message_id` (`message_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_message_association_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `message` (`id`),
  CONSTRAINT `user_message_association_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_message_association`
--

LOCK TABLES `user_message_association` WRITE;
/*!40000 ALTER TABLE `user_message_association` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_message_association` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_online`
--

DROP TABLE IF EXISTS `user_online`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_online` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `member` text,
  `online_user_num` int(11) DEFAULT NULL,
  `interval` int(11) DEFAULT NULL,
  `occ_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_online`
--

LOCK TABLES `user_online` WRITE;
/*!40000 ALTER TABLE `user_online` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_online` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `reset_password_token` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `confirmed_at` datetime DEFAULT NULL,
  `_online_time` int(11) NOT NULL,
  `update_time` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `avatar` varchar(255) NOT NULL,
  `money` int(11) NOT NULL,
  `permission_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `permission` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'luffy222','$2b$12$lIJhOfVoLMARAcYXZjpmbOspOyWlY8AUhjEAkNA0rrWeXmIjuNQpG','','wuaiwow@gmail.com','2019-03-20 09:38:14',10,1,1,'/static/images/avatar/default.png',100,10),(2,'gm','$2b$12$etSIw02p1OJtXlmt5eBLXO8maIkrLsgHikc6fKNKi.LaOWi30SKE6','','xxxxxx@qq.com','2019-03-20 09:38:14',10,1,1,'/static/images/avatar/default.png',100,8),(3,'Zoro','$2b$12$pxc2YgrCUvK6FlMn9Vo4a.miuuSJqjGR.j5NyiGKD3rXPPYc6GBUu','','xxxxxx@sina.com','2019-03-20 09:38:14',10,1,1,'/static/images/avatar/default.png',100,1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-03-20  9:45:01
