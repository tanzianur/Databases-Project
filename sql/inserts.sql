-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 07, 2025 at 03:54 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `project`
--

--
-- Dumping data for table `airline`
--

INSERT INTO `airline` (`name`) VALUES
('Jet Blue'),
('China Eastern'),
('Delta Airlines');

--
-- Dumping data for table `airline_staff`
--

INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`) VALUES
('jetblue_admin', 'passw0rd', 'Alice', 'Smith', '07042000', 'Jet Blue');

--
-- Dumping data for table `airplane`
--

INSERT INTO `airplane` (`airplane_ID`, `airline_name`, `num_seats`, `manufacturing_company`) VALUES
(1920, 'Jet Blue', 100, 'Plane Inc'),
(2012, 'Jet Blue', 180, 'Boeing'),
(8012, 'Jet Blue', 200, 'Plane Corp');

--
-- Dumping data for table `airport`
--

INSERT INTO `airport` (`code`, `name`, `city`, `country`) VALUES
('JFK', 'John F. Kennedy Airp', 'New York City', 'USA'),
('PVG', 'Shanghai Pudong Airp', 'Shanghai', 'China');

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('allie@gmail.com', 'Allie Marcu', 'Pass123', '444', 'Champion St', 'Brooklyn', 'New York', '7021892288', '000099992', '2025-11-18', 'USA', '1990-01-03'),
('jj@icloud.com', 'John James', 'blahblah', '2', 'Broadway', 'Los Angeles', 'California', '3892849829', '23892849', '2029-03-05', 'USA', '2000-01-01'),
('tanzia@yahoo.com', 'Tanzia Nur', 'Word0000', '123', 'Sesame St', 'Las Vegas', 'Nevada', '1902229999', '12290989', '2035-09-27', 'USA', '1980-12-30');

--
-- Dumping data for table `flight`
--

INSERT INTO `flight` (`airline_name`, `flight_number`, `departure_datetime`, `arrival_datetime`, `airplane_ID`, `departure_airport_code`, `arrival_airport_code`, `base_price`, `status`) VALUES
('Jet Blue', 'JB100', '2025-04-10 08:00:00', '2025-04-11 00:00:00', 2012, 'JFK', 'PVG', 500.00, 'Delayed'),
('Jet Blue', 'JB150', '2025-04-15 09:00:00', '2025-04-16 01:00:00', 8012, 'PVG', 'JFK', 890.00, 'On Time'),
('Jet Blue', 'JB202', '2025-03-25 07:00:00', '2025-03-25 23:00:00', 1920, 'JFK', 'PVG', 899.00, 'On Time'),
-- Return flights
('China Eastern', 'MU588', '2025-04-11 10:00:00', '2025-04-12 02:00:00', 2012, 'PVG', 'JFK', 550.00, 'On Time'),
('Delta Airlines', 'DL287', '2025-04-16 11:00:00', '2025-04-17 03:00:00', 8012, 'JFK', 'PVG', 950.00, 'On Time'),
('China Eastern', 'MU587', '2025-03-26 09:00:00', '2025-03-27 01:00:00', 1920, 'PVG', 'JFK', 950.00, 'On Time');

--
-- Dumping data for table `ticket`
--

INSERT INTO `ticket` (`ticket_ID`, `email`, `airline_name`, `flight_number`, `departure_datetime`, `sold_price`, `purchase_datetime`, `card_type`, `card_number`, `card_name`, `card_expiry`) VALUES
(1290, 'tanzia@yahoo.com', 'Jet Blue', 'JB150', '2025-04-15 09:00:00', 890.00, '2025-03-03 12:00:00', 'AmEx', '378282246310005', 'Tanzia Nur', '2026-11-01'),
(4902, 'allie@gmail.com', 'Jet Blue', 'JB150', '2025-04-15 09:00:00', 890.00, '2025-03-01 10:00:00', 'Visa', '4111111111111111', 'Allie Marcu', '2028-01-01'),
(28943, 'jj@icloud.com', 'Jet Blue', 'JB150', '2025-04-15 09:00:00', 890.00, '2025-03-02 11:00:00', 'MasterCard', '5555555555554444', 'John James', '2027-12-01');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
