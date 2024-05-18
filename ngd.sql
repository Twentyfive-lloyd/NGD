-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 18, 2024 at 08:46 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ngdelivery`
--

-- --------------------------------------------------------

--
-- Table structure for table `abonnements`
--

CREATE TABLE `abonnements` (
  `abonnement_id` int(11) NOT NULL,
  `fournisseur_id` int(11) NOT NULL,
  `type` enum('hebdomadaire','mensuel') NOT NULL,
  `date_debut` date NOT NULL,
  `date_fin` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `email`, `password`) VALUES
(1, 'admin', 'admin@admin.com', 'f4e0e6fc8c0067366f1234c584a4d36f');

-- --------------------------------------------------------

--
-- Table structure for table `clients`
--

CREATE TABLE `clients` (
  `id_client` int(11) NOT NULL,
  `nom` varchar(255) DEFAULT NULL,
  `prenom` varchar(255) DEFAULT NULL,
  `quartier` varchar(255) DEFAULT NULL,
  `telephone` varchar(35) DEFAULT NULL,
  `email` varchar(235) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `clients`
--

INSERT INTO `clients` (`id_client`, `nom`, `prenom`, `quartier`, `telephone`, `email`) VALUES
(701187693, 'Llou', 'Tre', 'Tre', 'Ffg', 'Hhf');

-- --------------------------------------------------------

--
-- Table structure for table `commandes`
--

CREATE TABLE `commandes` (
  `id_commande` int(11) NOT NULL,
  `lieu_livraison` varchar(255) DEFAULT NULL,
  `prix` decimal(10,2) DEFAULT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `client_id` int(11) DEFAULT NULL,
  `etat_commande` varchar(20) DEFAULT NULL,
  `livreur_id` int(11) DEFAULT NULL,
  `qr_code` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `courses`
--

CREATE TABLE `courses` (
  `id_course` int(11) NOT NULL,
  `nom_expediteur` varchar(200) DEFAULT NULL,
  `numero_expediteur` varchar(200) DEFAULT NULL,
  `lieu_recuperation` varchar(200) DEFAULT NULL,
  `lieu_livraison` varchar(200) DEFAULT NULL,
  `description_colis` varchar(200) DEFAULT NULL,
  `heure_ramassage` varchar(25) NOT NULL,
  `photo_colis` varchar(300) DEFAULT NULL,
  `choix_livraison` varchar(200) DEFAULT NULL,
  `prix` int(11) NOT NULL,
  `qr_code` varchar(400) NOT NULL,
  `client_id` int(11) DEFAULT NULL,
  `livreur_id` int(11) DEFAULT NULL,
  `etat_course` varchar(25) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `courses`
--

INSERT INTO `courses` (`id_course`, `nom_expediteur`, `numero_expediteur`, `lieu_recuperation`, `lieu_livraison`, `description_colis`, `heure_ramassage`, `photo_colis`, `choix_livraison`, `prix`, `qr_code`, `client_id`, `livreur_id`, `etat_course`, `create_date`) VALUES
(2, 'Kiu', '63839033', 'Tref', 'Yaounde III', 'U73e', '', NULL, 'Livraison Standard', 2500, '', 701187693, NULL, 'en_cours', '2024-03-13 12:00:02'),
(3, 'Iurp', '63727273', 'Yeie', 'Yaounde IV', 'Yrep', '', 'app/uploads/coursePhoto/336cf10df5.', 'Livraison Standard', 2500, '', 701187693, 4, 'en_cours', '2024-03-04 11:00:02'),
(4, 'Retd', '652728222', 'Ytrz', 'Yaounde III', 'Trez', '', NULL, 'Livraison Standard', 2500, '', 701187693, NULL, 'en_cours', '2024-03-04 11:00:02'),
(5, 'John', '6282282', 'Tradex', 'Yaounde III', 'Trèfles', '', 'AgACAgQAAxkBAAIq_mXkq8c8d5IYENH6VNcocFLpolAoAAJ5wTEb0eYpUxOBn3MICMX5AQADAgADeQADNAQ', 'Livraison Standard', 2500, '', 701187693, NULL, 'en_cours', '2024-03-04 11:00:02'),
(6, 'Trafd', '65178181', 'Tzyz', 'Yaounde III', 'Yuuu', '', 'AgACAgQAAxkBAAIrGmXkrDF7wGm9Cp9kb-1natgeAAH4ZAACe8ExG9HmKVO4o6RBo1l7KwEAAwIAA3kAAzQE', 'Livraison Express', 2500, '', 701187693, NULL, 'non_livree', '2024-03-05 08:36:05'),
(7, 'Tririr', 'Jeue', 'Uzuee', 'Yaounde II', 'Eueue', '', 'AgACAgQAAxkBAAIrimXktYeK9Dx19w3uZYnlTWdGMGqvAAKTwTEb0eYpU03vpe7BV7bYAQADAgADeQADNAQ', 'Livraison Express', 2500, '', 701187693, NULL, 'non_livree', '2024-03-05 08:49:42'),
(8, 'Rtrff', 'Gtyuff', 'Ghuff', 'Ggf', 'Hhjff', '', 'app/uploads/coursePhoto/96f46e31a0.', 'livraison_express', 40000, '', 701187693, 5, 'livree', '2024-03-05 08:52:52'),
(9, 'John', '65680031', '627272', 'Yaounde III', 'Zuzuz', 'Suzu', 'AgACAgQAAxkBAAIr_WXm9v96qyCFouYevEAfCWuEdDJ-AAKAwDEbh_c5UxcwxdQoS3aSAQADAgADeQADNAQ', 'Livraison Express', 2500, '', 701187693, NULL, 'en_cours', '2024-03-05 10:42:31'),
(10, 'John', '5544004', 'Z7z88z', 'Yaounde II', '62ie8e', '6h45', 'AgACAgQAAxkBAAIsGWXm-T4osa58SbTnL5ib3V7yyuXtAAKEwDEbh_c5U3OKwzHiOjzhAQADAgADeQADNAQ', 'Livraison Express', 2500, '', 701187693, NULL, 'en_cours', '2024-03-05 10:52:33'),
(11, 'Juin', '6r93932', '839e3', 'Yaounde II', 'Yte', '6h43', 'app/uploads/coursePhoto/445b091f51.', 'Livraison Express', 2500, '', 701187693, 8, 'en_cours', '2024-03-05 10:55:52'),
(12, 'Red', '6569202182', '7383', 'Yaounde II', 'I1iiss', '6302', 'app/uploads/coursePhoto/361ac932ae.', 'Livraison Express', 2500, '', 701187693, 11, 'en_cours', '2024-03-05 11:00:47'),
(13, 'Joun', '649494', '72278e', 'Yaounde III', '62378', '6h36e', 'AgACAgQAAxkBAAIsbWXm_Vd8Hye3bYYRaCvLqcKdUdnaAAJ6wDEbh_c5U70i-sSHVQk5AQADAgADeQADNAQ', 'Livraison Express', 2500, '', 701187693, NULL, 'en_cours', '2024-03-05 11:09:28'),
(14, 'Juni', '537494', '727e', 'Yaounde III', '8282', '7282', NULL, 'Livraison Express', 2500, '', 701187693, NULL, 'en_cours', '2024-03-05 11:13:21'),
(509318, 'john', '656958696', 'greed', 'Yaounde IV', 'defs', '7h52', NULL, 'Livraison Express', 2500, 'V2\\qr_codes\\qr_code_commande_509318.png', 701187693, NULL, 'en_cours', '2024-03-06 14:50:22'),
(870747, 'Yup', 'Yup', 'Yup', 'Yaounde IV', 'Yup', 'Yup', NULL, 'Livraison Express', 2500, 'C:/Users/HP/Documents/NGD/V2/qr_codes/qr_code_commande_870747.png', 701187693, NULL, 'en_cours', '2024-03-06 01:04:21');

-- --------------------------------------------------------

--
-- Table structure for table `deleteduser`
--

CREATE TABLE `deleteduser` (
  `id` int(11) NOT NULL,
  `email` varchar(50) NOT NULL,
  `deltime` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `delivery`
--

CREATE TABLE `delivery` (
  `id_delivery` int(11) NOT NULL,
  `id_livreur` int(11) DEFAULT NULL,
  `id_course` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `delivery`
--

INSERT INTO `delivery` (`id_delivery`, `id_livreur`, `id_course`) VALUES
(1, 9, 870747),
(2, 12, 509318),
(3, 11, 12),
(4, 4, 3),
(5, 8, 11),
(6, 5, 8);

-- --------------------------------------------------------

--
-- Table structure for table `factures`
--

CREATE TABLE `factures` (
  `id_factures` int(11) NOT NULL,
  `montant` decimal(10,2) DEFAULT NULL,
  `date_paiement` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `qr_code` varchar(255) DEFAULT NULL,
  `commande_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `id` int(11) NOT NULL,
  `sender` varchar(50) NOT NULL,
  `reciver` varchar(50) NOT NULL,
  `title` varchar(100) NOT NULL,
  `feedbackdata` varchar(500) NOT NULL,
  `attachment` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `fournisseur`
--

CREATE TABLE `fournisseur` (
  `fournisseur_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `surname` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `gender` varchar(50) NOT NULL,
  `mobile` varchar(50) NOT NULL,
  `designation` varchar(50) NOT NULL,
  `image` varchar(50) NOT NULL,
  `status` int(10) NOT NULL,
  `rolename` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `fournisseur`
--

INSERT INTO `fournisseur` (`fournisseur_id`, `name`, `surname`, `email`, `password`, `gender`, `mobile`, `designation`, `image`, `status`, `rolename`) VALUES
(1, 'John', 'Free', 'sherrillwilhoit@protonmail.com', 'c7b3c2dcdafa4634df42c9c905357779', 'Male', '0656958696', 'blast', 'blackcat.jpg', 1, ''),
(3, 'Martin', 'Gold', 'defsmhf@gmail.com', 'cd8fc2597193b4c938e7ff50062936e3', 'Male', '656958696', 'defs', 'blackcat.jpg', 0, '');

-- --------------------------------------------------------

--
-- Table structure for table `livreurs`
--

CREATE TABLE `livreurs` (
  `id_livreur` int(11) NOT NULL,
  `nom` varchar(255) DEFAULT NULL,
  `prenom` varchar(255) DEFAULT NULL,
  `telephone` varchar(255) DEFAULT NULL,
  `profilePhoto` varchar(255) NOT NULL,
  `rolename` varchar(150) NOT NULL,
  `gendar` varchar(150) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(11) NOT NULL,
  `quartier` varchar(200) NOT NULL,
  `create_date` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `status` int(11) NOT NULL,
  `lastactivity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `livreurs`
--

INSERT INTO `livreurs` (`id_livreur`, `nom`, `prenom`, `telephone`, `profilePhoto`, `rolename`, `gendar`, `email`, `password`, `quartier`, `create_date`, `status`, `lastactivity`) VALUES
(1, 'Doe', 'John', '0123456789', '', 'Livreur', 'male', 'john.doe@example.com', '0', 'Quartier A', '2024-03-04 15:38:57', 0, 0),
(2, 'Smith', 'Alice', '0987654321', '', 'Livreur', 'female', 'alice.smith@example.com', '0', 'Quartier B', '2024-03-04 15:09:36', 1, 0),
(3, 'Garcia', 'Carlos', '0765432109', '', 'Livreur', 'male', 'carlos.garcia@example.com', '0', 'Quartier C', '2024-03-04 15:38:25', 0, 0),
(4, 'Nguyen', 'Anh', '0345678901', '', 'Livreur', 'male', 'anh.nguyen@example.com', '0', 'Quartier D', '2024-03-04 15:38:55', 0, 0),
(5, 'Lee', 'Ji-eun', '0890123456', '', 'Livreur', 'female', 'ji-eun.lee@example.com', '0', 'Quartier E', '2024-03-04 15:09:36', 1, 0),
(6, 'Wang', 'Wei', '0654321098', '', 'Livreur', 'male', 'wei.wang@example.com', '0', 'Quartier F', '2024-03-04 15:38:29', 0, 0),
(7, 'Kumar', 'Rajesh', '0567890123', '', 'Livreur', 'male', 'rajesh.kumar@example.com', '0', 'Quartier G', '2024-03-04 15:09:48', 1, 0),
(8, 'Martinez', 'Ana', '0456789012', '', 'Livreur', 'female', 'ana.martinez@example.com', '0', 'Quartier H', '2024-03-04 15:38:44', 0, 0),
(9, 'Kim', 'Min-ji', '0321098765', '', 'Livreur', 'female', 'min-ji.kim@example.com', '0', 'Quartier I', '2024-03-04 15:09:36', 1, 0),
(10, 'Chen', 'Yan', '0789012345', '', 'Livreur', 'female', 'yan.chen@example.com', '0', 'Quartier J', '2024-04-26 13:13:17', 0, 0),
(11, 'Gupta', 'Amit', '0213456789', '', 'Livreur', 'male', 'amit.gupta@example.com', '0', 'Quartier K', '2024-03-04 15:38:47', 0, 0),
(12, 'Müller', 'Hans', '0678901234', '', 'Livreur', 'male', 'hans.muller@example.com', '0', 'Quartier L', '2024-03-04 15:39:01', 0, 0),
(13, 'Smith', 'Emma', '0543210987', '', 'Livreur', 'female', 'emma.smith@example.com', '0', 'Quartier M', '2024-03-04 15:38:50', 0, 0),
(14, 'Park', 'Joon-ho', '0432109876', '', 'Livreur', 'male', 'joon-ho.park@example.com', '0', 'Quartier N', '2024-03-05 09:35:32', 0, 0),
(15, 'Silva', 'Maria', '0789012345', 'app/uploads/userAvatar/0b6ba953c9.', 'Livreur', 'male', 'maria.silva@example.com', '0', 'Quartier O', '2024-03-06 15:39:15', 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `notification`
--

CREATE TABLE `notification` (
  `id` int(11) NOT NULL,
  `notiuser` varchar(50) NOT NULL,
  `notireciver` varchar(50) NOT NULL,
  `notitype` varchar(50) NOT NULL,
  `time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `notification`
--

INSERT INTO `notification` (`id`, `notiuser`, `notireciver`, `notitype`, `time`) VALUES
(1, 'sherrillwilhoit@protonmail.com', 'Admin', 'Create Account', '2024-03-15 08:11:13'),
(2, 'sherrillwilhoit@protonmail.com', 'Admin', 'Create Account', '2024-03-15 08:16:31'),
(3, 'defsmhf@gmail.com', 'Admin', 'Create Account', '2024-04-26 13:36:41'),
(4, 'defsmhf@gmail.com', 'Admin', 'Create Account', '2024-04-26 13:42:00');

-- --------------------------------------------------------

--
-- Table structure for table `produits`
--

CREATE TABLE `produits` (
  `id_produit` int(11) NOT NULL,
  `nom` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `prix_unitaire` decimal(10,2) DEFAULT NULL,
  `quantite` int(11) NOT NULL,
  `image1` varchar(255) DEFAULT NULL,
  `image2` varchar(255) DEFAULT NULL,
  `image3` varchar(255) DEFAULT NULL,
  `categorie` varchar(255) DEFAULT NULL,
  `id_four` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `produits`
--

INSERT INTO `produits` (`id_produit`, `nom`, `description`, `prix_unitaire`, `quantite`, `image1`, `image2`, `image3`, `categorie`, `id_four`) VALUES
(20, 'Smartphone Android', 'Téléphone portable Android avec écran 6.5 pouces et 128GB de stockage', 150000.00, 20, 'smartphone1.jpg', 'smartphone2.jpg', 'smartphone3.jpg', 'Electronique', 1),
(21, 'Étui de protection', 'Étui en silicone pour smartphone', 5000.00, 20, 'etui1.jpg', 'etui2.jpg', 'etui3.jpg', 'Accessoires', 1),
(22, 'Écouteurs sans fil', 'Écouteurs Bluetooth avec réduction de bruit', 20000.00, 20, 'ecouteurs1.jpg', 'ecouteurs2.jpg', 'ecouteurs3.jpg', 'Electronique', 1),
(23, 'Réfrigérateur', 'Réfrigérateur double porte avec capacité de 300L', 250000.00, 20, 'refrigerateur1.jpg', 'refrigerateur2.jpg', 'refrigerateur3.jpg', 'Electroménager', 1),
(24, 'Cuisinière', 'Cuisinière à gaz avec four intégré', 180000.00, 20, 'cuisiniere1.jpg', 'cuisiniere2.jpg', 'cuisiniere3.jpg', 'Electroménager', 1),
(25, 'Mixeur', 'Mixeur 500W avec 3 vitesses', 50000.00, 20, 'mixeur1.jpg', 'mixeur2.jpg', 'mixeur3.jpg', 'Electroménager', 1),
(26, 'Robe de soirée', 'Robe de soirée élégante, taille M', 80000.00, 20, 'robe1.jpg', 'robe2.jpg', 'robe3.jpg', 'Vêtements', 1),
(27, 'Jeans', 'Jeans bleu slim fit', 40000.00, 20, 'jeans1.jpg', 'jeans2.jpg', 'jeans3.jpg', 'Vêtements', 1),
(28, 'Sneakers', 'Chaussures sneakers confortables, taille 42', 60000.00, 20, 'sneakers1.jpg', 'sneakers2.jpg', 'sneakers3.jpg', 'Chaussures', 1),
(29, 'Riz', 'Sac de riz de 25kg', 20000.00, 20, 'riz1.jpg', 'riz2.jpg', 'riz3.jpg', 'Alimentation', 1),
(30, 'Huile végétale', 'Bouteille de 5L d\'huile végétale', 10000.00, 20, 'huile1.jpg', 'huile2.jpg', 'huile3.jpg', 'Alimentation', 1),
(31, 'Lait', 'Pack de 12 bouteilles de lait de 1L', 24000.00, 20, 'lait1.jpg', 'lait2.jpg', 'lait3.jpg', 'Alimentation', 1),
(32, 'Crème hydratante', 'Crème hydratante pour peau sèche, 500ml', 15000.00, 20, 'creme1.jpg', 'creme2.jpg', 'creme3.jpg', 'Beauté', 1),
(33, 'Shampoing', 'Shampoing revitalisant, 1L', 8000.00, 20, 'shampoing1.jpg', 'shampoing2.jpg', 'shampoing3.jpg', 'Beauté', 1),
(34, 'Fond de teint', 'Fond de teint longue tenue, 30ml', 12000.00, 20, 'fond1.jpg', 'fond2.jpg', 'fond3.jpg', 'Beauté', 1),
(35, 'Télévision', 'Télévision LED 50 pouces, 4K UHD', 350000.00, 20, 'tv1.jpg', 'tv2.jpg', 'tv3.jpg', 'Electronique', 1),
(36, 'Ordinateur portable', 'Ordinateur portable 15.6 pouces, Intel i5, 8GB RAM', 450000.00, 20, 'laptop1.jpg', 'laptop2.jpg', 'laptop3.jpg', 'Electronique', 1),
(37, 'Tablette', 'Tablette Android 10 pouces, 64GB', 120000.00, 20, 'tablette1.jpg', 'tablette2.jpg', 'tablette3.jpg', 'Electronique', 1),
(38, 'Couches jetables', 'Pack de 100 couches jetables, taille M', 25000.00, 20, 'couches1.jpg', 'couches2.jpg', 'couches3.jpg', 'Bébé', 1),
(39, 'Jouet éducatif', 'Jouet éducatif pour enfants, âge 3+', 15000.00, 20, 'jouet1.jpg', 'jouet2.jpg', 'jouet3.jpg', 'Enfants', 1);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_app_autho`
--

CREATE TABLE `tbl_app_autho` (
  `id_autho` int(11) NOT NULL,
  `allow_email` int(11) NOT NULL DEFAULT 0,
  `fb_autho` int(11) NOT NULL DEFAULT 0,
  `tw_autho` int(11) NOT NULL DEFAULT 0,
  `gle_autho` int(11) NOT NULL DEFAULT 0,
  `git_autho` int(11) NOT NULL DEFAULT 0,
  `status` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_app_autho`
--

INSERT INTO `tbl_app_autho` (`id_autho`, `allow_email`, `fb_autho`, `tw_autho`, `gle_autho`, `git_autho`, `status`) VALUES
(143, 0, 0, 0, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_app_settings`
--

CREATE TABLE `tbl_app_settings` (
  `app_id` int(11) NOT NULL,
  `app_name` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `front_name` varchar(255) NOT NULL,
  `favicon` varchar(255) NOT NULL,
  `logo` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_app_settings`
--

INSERT INTO `tbl_app_settings` (`app_id`, `app_name`, `title`, `front_name`, `favicon`, `logo`) VALUES
(1, 'NGD - Admin Panel', 'NGD - Admin Panel', 'NGD - Login/User Management', 'app/uploads/logo/c604f443587379d.png', 'app/uploads/logo/c604f443587379d7e057.png');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_permissions`
--

CREATE TABLE `tbl_permissions` (
  `perid` int(11) NOT NULL,
  `per_access` varchar(255) NOT NULL,
  `per_create` varchar(255) NOT NULL,
  `per_show` varchar(255) NOT NULL,
  `per_edit` varchar(255) NOT NULL,
  `per_delete` varchar(255) NOT NULL,
  `ban_activ_user` varchar(255) NOT NULL,
  `per_onlyUser` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_permissions`
--

INSERT INTO `tbl_permissions` (`perid`, `per_access`, `per_create`, `per_show`, `per_edit`, `per_delete`, `ban_activ_user`, `per_onlyUser`) VALUES
(1, 'Access', 'Create', 'Show', 'Edit', 'Delete', 'Ban/Active user', 'User only');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_roles`
--

CREATE TABLE `tbl_roles` (
  `roleid` int(11) NOT NULL,
  `rolename` varchar(255) NOT NULL,
  `roledname` varchar(255) NOT NULL,
  `permission_items` varchar(255) NOT NULL,
  `status` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_roles`
--

INSERT INTO `tbl_roles` (`roleid`, `rolename`, `roledname`, `permission_items`, `status`) VALUES
(212, 'Author', 'Nababur', 'Access,Create,Show,Edit,Delete,Ban/Active user,User only', 0),
(213, 'Admin', 'Sabuj', 'Show,Edit', 0),
(215, 'Supper Admin', 'Nababur Rahaman', 'Create,Show,Edit,Delete,Ban/Active user,User only', 0),
(217, 'Contributor', 'Sujon ahmed', 'Create,Show,Edit,Delete,Ban/Active user', 0),
(219, 'Subscriber', 'Raju abir', 'Create,Show,Edit,Delete', 0),
(221, 'Only user', 'Sabuj', 'AccessCourse,ShowCourse,EditCourse,DeleteCourse', 0),
(222, 'Livreur', 'Livreur', 'Show', 0);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_users`
--

CREATE TABLE `tbl_users` (
  `userid` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `phone` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `information` text NOT NULL,
  `email` varchar(255) NOT NULL,
  `city` varchar(255) NOT NULL,
  `country` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `profilePhoto` varchar(255) NOT NULL,
  `rolename` varchar(255) NOT NULL,
  `status` int(11) NOT NULL DEFAULT 0,
  `gendar` varchar(255) NOT NULL,
  `create_date` datetime NOT NULL,
  `lastactivity` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_users`
--

INSERT INTO `tbl_users` (`userid`, `name`, `phone`, `address`, `information`, `email`, `city`, `country`, `password`, `profilePhoto`, `rolename`, `status`, `gendar`, `create_date`, `lastactivity`) VALUES
(96, 'Kabir khan', '01245786420', 'Thakurgaon, Baliadangi', 'This is Kabir khan', 'kabir@gmail.com', 'Thakurgaon', 'Bangladesh', '$2y$10$DlH1iFaVE1ib6itYvlIzbuIBJ/11NV5bmsf7iCW3U0jzSvLamilt2', 'app/uploads/userAvatar/c7e375639e.jpg', 'Only user', 0, 'male', '2020-01-13 09:53:30', 0),
(103, 'Md Nababur Rahaman', '01717090233', 'Thakurgaon, Baliadangi', 'This is Nababur Rahaman', 'nababurbd@gmail.com', 'Thakurgaon', 'Bangladesh', '$2y$10$BJ9u3IcTzJLhA0Jypm/lNuW/EOQt1.v5KqilCQPTlerWPt3ELP1Um', 'app/uploads/userAvatar/9f785a4605.jpg', 'Author', 0, 'male', '2015-01-13 09:51:15', 1),
(104, 'Rana ahmed', '01245786420', 'thakugfdf', 'diff', 'rasel@gmail.com', 'dfsdfsfddfdf', 'Barbados', '$2y$10$IkWzHpR.ponUxWLrj0il4uxIoON7mOhx3ShOuixpW02QMLQn2ZFYK', 'app/uploads/userAvatar/5b270dd3d9.png', 'Supper Admin', 0, 'male', '2018-12-11 01:20:29', 0),
(105, 'Sobuj ahmed', '01245786420', 'Ranisoinkol, horipur', '', 'sobujahmed@gmail.com', 'Ranisoinkol', 'Anguilla', '$2y$10$L58jypjrTRsuNpgrr71cAewBoPDmEThTFuB2uM1H6k4s58/zvUJk.', 'app/uploads/userAvatar/479e72eaca.jpg', 'Supper Admin', 0, 'male', '2020-01-09 03:06:26', 0),
(106, 'Humayun Kabir Munna', '01245786420', 'Pirgonj, Thakurgaon', 'This is Munna', 'munna@gmail.com', 'Pirgonj', 'Bangladesh', '$2y$10$rFrDMxUyk3oJpKXRmm2C4OvSiFeSDFNXf8VcqHPJgRMGLHIQggd7q', 'app/uploads/userAvatar/db5433f879.jpg', 'Supper Admin', 0, 'male', '2020-01-12 04:56:06', 0),
(107, 'Raihan Kabir', '019332154545', 'Mirpur, Dhaka', 'This is Raihan Kabir.', 'raihan@gmail.com', 'Mirpur', 'Belgium', '$2y$10$nmsSKVQM7ksgY2CxsmOfS.r1AB0sDx8wp2Se4y227fhggF9ONy.aW', 'app/uploads/userAvatar/ec6120cc76.png', 'Supper Admin', 0, 'male', '2020-01-12 04:57:48', 0),
(108, 'Saddam hossain', '01245786420', 'Ponchogor Boda', 'This is Saddam Hossain', 'saddam@gmail.com', 'Ponchogor', 'Bahamas', '$2y$10$5s4F9kzMgWc3S7YZLRf5H.BlF013LwLU60bt1B5Z7dGFG8/p8a8j6', 'app/uploads/userAvatar/c362c75f91.jpg', 'Admin', 0, 'male', '2020-01-12 08:08:41', 0),
(109, 'Shamim Rana', '', '', '', 'shamim@gmail.com', '', '', '$2y$10$t3.6b0lCUOb1ME9l2G1EKuLXg2m1lxKmghqUiePnChyM.rzqbmFDG', '', 'Admin	', 0, '', '2020-01-13 17:34:31', 0),
(110, 'Dalim Hossain', '', '', '', 'dalim@gmail.com', '', '', '$2y$10$fb4J4LEEUsinZF3RmutDkeyiNBECLA4MVpKgm24UiSGGPJFHHql0a', '', 'Admin	', 0, '', '2020-01-13 21:10:24', 0),
(111, 'Raju Abir', '', '', '', 'raju@gmail.com', '', '', '$2y$10$P2tOP3BgBWdIiKVCMsC5wO5fUBlcdK34etTHKSoOREltj3KCQBrbi', '', 'Admin	', 1, '', '2020-01-13 21:10:20', 0),
(113, 'Liton Dass', '01729793766', 'Mirpur, Dhaka', '', 'liton@gmail.com', 'Mirpur', 'Anguilla', '$2y$10$iQBuh00UcVB/2YIwDsNdj.Q3SL8SqH.av0NTYNLj5ChEFDtpE7TGu', 'app/uploads/userAvatar/72050401f6.jpg', 'Contributor', 0, 'male', '2020-01-13 17:34:28', 0),
(114, 'Harun Rashid', '01245786420', 'Thakurgaon,', 'This is Harun,', 'harun@gmail.com', 'Thakurgaon,', 'Angola', '$2y$10$7BPP9YhF8fPIywXGoNfc6.8688Rt.jlmzl0Y386wRj9wbilBrLO9S', 'app/uploads/userAvatar/edb274937c.png', 'Subscriber', 0, 'male', '2020-01-12 02:03:38', 0),
(115, 'Jasmin akhter', '01245786420', 'Thakurgaon, Baliadangi', '', 'jasmin@gmail.com', 'Thakurgaon', 'Antigua &amp; Barbuda', '$2y$10$fpmdreyUbOKB2B6adPgJjuarBrtLd/jPX3MKks0vexTfDYeCd6axG', 'app/uploads/userAvatar/25d37110db.png', 'Only user', 0, 'female', '2020-01-12 16:22:56', 0),
(116, 'Osman gony', '', '', '', 'osman@gmail.com', '', '', '$2y$10$5vGZpnQoJWkGotLtUEdxSOZLrFTFrfCf7u5MhHFwNebR6J0MNYLs2', '', 'Only user', 0, '', '2020-01-13 17:34:19', 0),
(118, 'Akhi akhter', '012458136', 'Thakurgaon, Balidadangi', 'This is Akhi akhter', 'akhi@gmail.com', 'Thakurgaon,Bangaldesh', 'Bangladesh', '$2y$10$duzCYAS32wBFSfr/J8BoN.OPQ52.hYAMcgygAIqGS1.nkJXdxQuvu', 'app/uploads/userAvatar/369187ff7a.png', 'Only user', 0, 'female', '2020-01-13 05:18:36', 0),
(120, 'Rony Ahmed', '', '', '', 'rony@gmail.com', '', '', '$2y$10$fVGdshQyyOTDk5yHRG5USueDUUq93f0Jj/EHPo0dffFnaWU.lpNDm', '', 'Only user', 1, '', '2020-01-13 21:10:51', 0),
(121, 'Moniruzzaman monir', '054542021', 'BEGUNGAO', '', 'connectionwifi33@gmail.com', 'Mojatibazar', 'Bangladesh', '$2y$10$vCnyqvxvLONi/4cDRti9Vua3HvAjLITARgXjvfokgE8icQ3SnfKNq', 'app/uploads/userAvatar/d656ca8a78.png', 'Supper Admin', 0, 'male', '2020-02-04 12:14:06', 0),
(122, 'John Free', '656958696', 'Dr house red', '', 'sherrillwilhoit@protonmail.com', 'adomaspomf', 'Cameroon', '$2y$10$BJ9u3IcTzJLhA0Jypm/lNuW/EOQt1.v5KqilCQPTlerWPt3ELP1Um', '', 'Livreur', 0, 'Select your gendar', '2024-05-15 07:56:02', 0),
(123, 'Martin Gold', '656958696', 'Dr house red', '', 'defsmhf@gmail.com', 'adomaspomf', 'Cameroon', '$2y$10$S1DU5Eqyiz7125Ny48wH3.xTiabHZ2ts3xM60OiQFXueK7qjevhsy', 'app/uploads/userAvatar/fb83bb55d7.jpg', 'Only user', 0, 'Select your gendar', '2024-05-16 10:57:21', 1);

-- --------------------------------------------------------

--
-- Table structure for table `vente`
--

CREATE TABLE `vente` (
  `id_vente` int(11) NOT NULL,
  `id_course` int(11) DEFAULT NULL,
  `id_produit` int(11) DEFAULT NULL,
  `quantite` int(11) DEFAULT NULL,
  `montant` decimal(10,2) DEFAULT NULL,
  `date_vente` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `abonnements`
--
ALTER TABLE `abonnements`
  ADD PRIMARY KEY (`abonnement_id`),
  ADD KEY `fournisseur_id` (`fournisseur_id`);

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`id_client`);

--
-- Indexes for table `commandes`
--
ALTER TABLE `commandes`
  ADD PRIMARY KEY (`id_commande`),
  ADD KEY `client_id` (`client_id`),
  ADD KEY `livreur_id` (`livreur_id`);

--
-- Indexes for table `courses`
--
ALTER TABLE `courses`
  ADD PRIMARY KEY (`id_course`),
  ADD KEY `FK_courses_livreurs` (`livreur_id`),
  ADD KEY `FK_courses_client` (`client_id`);

--
-- Indexes for table `deleteduser`
--
ALTER TABLE `deleteduser`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `delivery`
--
ALTER TABLE `delivery`
  ADD PRIMARY KEY (`id_delivery`),
  ADD KEY `FK_delivery_livreur` (`id_livreur`),
  ADD KEY `FK_delivery_course` (`id_course`);

--
-- Indexes for table `factures`
--
ALTER TABLE `factures`
  ADD PRIMARY KEY (`id_factures`),
  ADD KEY `commande_id` (`commande_id`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `fournisseur`
--
ALTER TABLE `fournisseur`
  ADD PRIMARY KEY (`fournisseur_id`);

--
-- Indexes for table `livreurs`
--
ALTER TABLE `livreurs`
  ADD PRIMARY KEY (`id_livreur`);

--
-- Indexes for table `notification`
--
ALTER TABLE `notification`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `produits`
--
ALTER TABLE `produits`
  ADD PRIMARY KEY (`id_produit`),
  ADD KEY `FK_produit_fournisseur` (`id_four`);

--
-- Indexes for table `tbl_app_autho`
--
ALTER TABLE `tbl_app_autho`
  ADD PRIMARY KEY (`id_autho`);

--
-- Indexes for table `tbl_app_settings`
--
ALTER TABLE `tbl_app_settings`
  ADD PRIMARY KEY (`app_id`);

--
-- Indexes for table `tbl_permissions`
--
ALTER TABLE `tbl_permissions`
  ADD PRIMARY KEY (`perid`);

--
-- Indexes for table `tbl_roles`
--
ALTER TABLE `tbl_roles`
  ADD PRIMARY KEY (`roleid`);

--
-- Indexes for table `tbl_users`
--
ALTER TABLE `tbl_users`
  ADD PRIMARY KEY (`userid`);

--
-- Indexes for table `vente`
--
ALTER TABLE `vente`
  ADD PRIMARY KEY (`id_vente`),
  ADD KEY `FK_vente_course` (`id_course`),
  ADD KEY `FK_vente_produit` (`id_produit`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `abonnements`
--
ALTER TABLE `abonnements`
  MODIFY `abonnement_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `clients`
--
ALTER TABLE `clients`
  MODIFY `id_client` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=701187694;

--
-- AUTO_INCREMENT for table `commandes`
--
ALTER TABLE `commandes`
  MODIFY `id_commande` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `delivery`
--
ALTER TABLE `delivery`
  MODIFY `id_delivery` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `factures`
--
ALTER TABLE `factures`
  MODIFY `id_factures` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `fournisseur`
--
ALTER TABLE `fournisseur`
  MODIFY `fournisseur_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `livreurs`
--
ALTER TABLE `livreurs`
  MODIFY `id_livreur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `notification`
--
ALTER TABLE `notification`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `produits`
--
ALTER TABLE `produits`
  MODIFY `id_produit` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT for table `tbl_app_autho`
--
ALTER TABLE `tbl_app_autho`
  MODIFY `id_autho` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=144;

--
-- AUTO_INCREMENT for table `tbl_app_settings`
--
ALTER TABLE `tbl_app_settings`
  MODIFY `app_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_permissions`
--
ALTER TABLE `tbl_permissions`
  MODIFY `perid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_roles`
--
ALTER TABLE `tbl_roles`
  MODIFY `roleid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=223;

--
-- AUTO_INCREMENT for table `tbl_users`
--
ALTER TABLE `tbl_users`
  MODIFY `userid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=124;

--
-- AUTO_INCREMENT for table `vente`
--
ALTER TABLE `vente`
  MODIFY `id_vente` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `abonnements`
--
ALTER TABLE `abonnements`
  ADD CONSTRAINT `abonnements_ibfk_1` FOREIGN KEY (`fournisseur_id`) REFERENCES `fournisseur` (`fournisseur_id`);

--
-- Constraints for table `commandes`
--
ALTER TABLE `commandes`
  ADD CONSTRAINT `commandes_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id_client`),
  ADD CONSTRAINT `commandes_ibfk_2` FOREIGN KEY (`livreur_id`) REFERENCES `livreurs` (`id_livreur`);

--
-- Constraints for table `courses`
--
ALTER TABLE `courses`
  ADD CONSTRAINT `FK_courses_client` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id_client`),
  ADD CONSTRAINT `FK_courses_livreurs` FOREIGN KEY (`livreur_id`) REFERENCES `livreurs` (`id_livreur`);

--
-- Constraints for table `delivery`
--
ALTER TABLE `delivery`
  ADD CONSTRAINT `FK_delivery_course` FOREIGN KEY (`id_course`) REFERENCES `courses` (`id_course`),
  ADD CONSTRAINT `FK_delivery_livreur` FOREIGN KEY (`id_livreur`) REFERENCES `livreurs` (`id_livreur`);

--
-- Constraints for table `factures`
--
ALTER TABLE `factures`
  ADD CONSTRAINT `factures_ibfk_1` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id_commande`);

--
-- Constraints for table `produits`
--
ALTER TABLE `produits`
  ADD CONSTRAINT `FK_produit_fournisseur` FOREIGN KEY (`id_four`) REFERENCES `fournisseur` (`fournisseur_id`);

--
-- Constraints for table `vente`
--
ALTER TABLE `vente`
  ADD CONSTRAINT `FK_vente_course` FOREIGN KEY (`id_course`) REFERENCES `courses` (`id_course`),
  ADD CONSTRAINT `FK_vente_produit` FOREIGN KEY (`id_produit`) REFERENCES `produits` (`id_produit`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
