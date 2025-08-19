-- MySQL dump 10.13  Distrib 8.0.43, for Linux (x86_64)
--
-- Host: localhost    Database: appdb
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `healthcheck`
--

LOCK TABLES `healthcheck` WRITE;
/*!40000 ALTER TABLE `healthcheck` DISABLE KEYS */;
/*!40000 ALTER TABLE `healthcheck` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `parts`
--

LOCK TABLES `parts` WRITE;
/*!40000 ALTER TABLE `parts` DISABLE KEYS */;
INSERT INTO `parts` VALUES (1,'Brake Pads - Front','Set of front brake pads, lightly used',30,'Austin, TX','/static/images/brake.png','parts@example.com','512-555-0100','2025-08-18 16:09:45',NULL,1),(2,'Oil Filter','New OEM oil filter',8,'Austin, TX','/static/images/oil.png','parts@example.com','512-555-0101','2025-08-18 16:09:45',NULL,1),(3,'Alternator','Rebuilt alternator for 2005-2010 models',120,'San Marcos, TX','/static/images/alternator.png','rebuilt@example.com','512-555-0102','2025-08-18 16:09:45',NULL,1),(4,'Headlight Assembly','Left headlight, clear lens',45,'Round Rock, TX','/static/images/headlight.png','lights@example.com','512-555-0103','2025-08-18 16:09:45',NULL,1),(5,'Tires - All Season (4)','195/65R15, good tread',200,'Pflugerville, TX','/static/images/tires.png','tires@example.com','512-555-0104','2025-08-18 16:09:45',NULL,1),(6,'Air Intake Filter','Reusable performance filter',25,'Georgetown, TX','/static/images/airfilter.png','filter@example.com','512-555-0105','2025-08-18 16:09:45',NULL,1);
/*!40000 ALTER TABLE `parts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-19 13:18:32
