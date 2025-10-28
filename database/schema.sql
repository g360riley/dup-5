-- Database Schema for Equipment Rental Management System
-- Run this file to create the required database structure

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS rental_detail;
DROP TABLE IF EXISTS rental;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS employee;

-- Create employee table for authentication and staff management
CREATE TABLE employee (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    position VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create customer table
CREATE TABLE customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    drivers_license VARCHAR(50),
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create equipment table
CREATE TABLE equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL,
    description TEXT,
    daily_rate DECIMAL(10, 2) NOT NULL,
    condition_status ENUM('Excellent', 'Good', 'Fair', 'Poor') DEFAULT 'Good',
    availability_status ENUM('Available', 'Rented', 'Maintenance', 'Retired') DEFAULT 'Available',
    purchase_date DATE,
    serial_number VARCHAR(100) UNIQUE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create rental table
CREATE TABLE rental (
    rental_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    employee_id INT NOT NULL,
    rental_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status ENUM('Active', 'Completed', 'Overdue') DEFAULT 'Active',
    subtotal DECIMAL(10, 2) NOT NULL,
    late_fee DECIMAL(10, 2) DEFAULT 0.00,
    total_cost DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE RESTRICT
);

-- Create rental_detail table (junction table for rental and equipment)
CREATE TABLE rental_detail (
    rental_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT NOT NULL,
    equipment_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    daily_rate DECIMAL(10, 2) NOT NULL,
    days_rented INT NOT NULL,
    line_total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rental_id) REFERENCES rental(rental_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE RESTRICT
);

-- Create indexes for performance optimization
CREATE INDEX idx_employee_username ON employee(username);
CREATE INDEX idx_employee_email ON employee(email);
CREATE INDEX idx_customer_name ON customer(last_name, first_name);
CREATE INDEX idx_customer_email ON customer(email);
CREATE INDEX idx_customer_archived ON customer(is_archived);
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_status ON equipment(availability_status);
CREATE INDEX idx_equipment_archived ON equipment(is_archived);
CREATE INDEX idx_rental_customer ON rental(customer_id);
CREATE INDEX idx_rental_employee ON rental(employee_id);
CREATE INDEX idx_rental_status ON rental(status);
CREATE INDEX idx_rental_dates ON rental(rental_date, due_date);
CREATE INDEX idx_rental_detail_rental ON rental_detail(rental_id);
CREATE INDEX idx_rental_detail_equipment ON rental_detail(equipment_id);