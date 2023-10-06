-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server-Version:               8.1.0 - MySQL Community Server - GPL
-- Server-Betriebssystem:        Win64
-- HeidiSQL Version:             12.5.0.6677
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Exportiere Datenbank-Struktur für rezeptdb
CREATE DATABASE IF NOT EXISTS `rezeptdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `rezeptdb`;

-- Exportiere Struktur von Tabelle rezeptdb.labels
CREATE TABLE IF NOT EXISTS `labels` (
  `id` int NOT NULL AUTO_INCREMENT,
  `label` tinytext NOT NULL,
  PRIMARY KEY (`id`),
  FULLTEXT KEY `label` (`label`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle rezeptdb.rezepte
CREATE TABLE IF NOT EXISTS `rezepte` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT NULL,
  `titel` tinytext,
  `rezept` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `label` text,
  `pdf` longblob,
  PRIMARY KEY (`id`),
  KEY `timestamp` (`timestamp`),
  FULLTEXT KEY `titel` (`titel`),
  FULLTEXT KEY `rezept` (`rezept`),
  FULLTEXT KEY `label` (`label`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
