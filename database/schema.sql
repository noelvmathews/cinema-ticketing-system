-- Database creation
CREATE DATABASE IF NOT EXISTS cts;
USE cts;

-- 1. Movies Table
CREATE TABLE IF NOT EXISTS Movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    category VARCHAR(50),
    price INT NOT NULL
);

-- 2. Showtimes Table
CREATE TABLE IF NOT EXISTS Showtimes (
    show_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT,
    screen_number INT NOT NULL,
    show_date DATE NOT NULL,
    show_time TIME NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE
);

-- 3. Seats Table
CREATE TABLE IF NOT EXISTS Seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    show_id INT,
    movie_id INT,
    seat_row CHAR(1) NOT NULL,
    seat_num INT NOT NULL,
    booked TINYINT(1) DEFAULT 0,
    FOREIGN KEY (show_id) REFERENCES Showtimes(show_id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE
);

-- 4. Bill Table
CREATE TABLE IF NOT EXISTS Bill (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    movie_name VARCHAR(255) NOT NULL,
    seat VARCHAR(10) NOT NULL,
    category VARCHAR(50),
    total_price INT NOT NULL,
    show_date DATE NOT NULL,
    show_time TIME NOT NULL,
    screen_number INT NOT NULL
);
