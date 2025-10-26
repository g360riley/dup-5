-- Seed Data for Equipment Rental Management System
-- Run this file to populate the database with sample data
-- Password for all employees: password123

-- Insert employee data
-- Password hash for 'password123' using Werkzeug's generate_password_hash
INSERT INTO employee (username, password_hash, first_name, last_name, email, phone, position, hire_date, is_active) VALUES
('admin', 'pbkdf2:sha256:600000$randomsalt1234$8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'John', 'Admin', 'admin@rentalshop.com', '555-0100', 'Manager', '2023-01-15', TRUE),
('jsmith', 'pbkdf2:sha256:600000$randomsalt5678$8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Jane', 'Smith', 'jsmith@rentalshop.com', '555-0101', 'Rental Agent', '2023-03-20', TRUE),
('mjones', 'pbkdf2:sha256:600000$randomsalt9012$8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Mike', 'Jones', 'mjones@rentalshop.com', '555-0102', 'Rental Agent', '2023-06-10', TRUE);

-- Insert customer data
INSERT INTO customer (first_name, last_name, email, phone, address, city, state, zip_code, drivers_license) VALUES
('Robert', 'Johnson', 'robert.j@email.com', '555-1001', '123 Main St', 'Atlanta', 'GA', '30301', 'GA12345678'),
('Sarah', 'Williams', 'sarah.w@email.com', '555-1002', '456 Oak Ave', 'Atlanta', 'GA', '30302', 'GA23456789'),
('Michael', 'Brown', 'michael.b@email.com', '555-1003', '789 Pine Rd', 'Marietta', 'GA', '30060', 'GA34567890'),
('Emily', 'Davis', 'emily.d@email.com', '555-1004', '321 Elm St', 'Roswell', 'GA', '30075', 'GA45678901'),
('David', 'Miller', 'david.m@email.com', '555-1005', '654 Maple Dr', 'Decatur', 'GA', '30030', 'GA56789012'),
('Jessica', 'Wilson', 'jessica.w@email.com', '555-1006', '987 Cedar Ln', 'Alpharetta', 'GA', '30004', 'GA67890123'),
('Christopher', 'Moore', 'chris.m@email.com', '555-1007', '147 Birch Ct', 'Sandy Springs', 'GA', '30328', 'GA78901234'),
('Amanda', 'Taylor', 'amanda.t@email.com', '555-1008', '258 Spruce Way', 'Kennesaw', 'GA', '30144', 'GA89012345');

-- Insert equipment data
INSERT INTO equipment (equipment_name, equipment_type, description, daily_rate, condition_status, availability_status, purchase_date, serial_number) VALUES
('Power Drill - DeWalt 20V', 'Power Tools', 'Cordless drill with battery and charger', 25.00, 'Excellent', 'Available', '2024-01-15', 'SN-DRILL-001'),
('Chainsaw - Stihl MS 271', 'Power Tools', 'Gas-powered chainsaw, 16 inch bar', 45.00, 'Good', 'Available', '2023-11-20', 'SN-SAW-001'),
('Pressure Washer - 3000 PSI', 'Cleaning Equipment', 'Gas-powered pressure washer with hose', 55.00, 'Good', 'Available', '2024-02-10', 'SN-WASH-001'),
('Lawn Mower - Commercial', 'Lawn Equipment', 'Self-propelled commercial mower', 40.00, 'Excellent', 'Available', '2024-03-05', 'SN-MOWER-001'),
('Table Saw - 10 inch', 'Power Tools', 'Professional grade table saw', 60.00, 'Good', 'Available', '2023-09-15', 'SN-SAW-002'),
('Floor Sander - Drum', 'Floor Equipment', 'Heavy duty drum sander for hardwood floors', 75.00, 'Good', 'Available', '2023-10-20', 'SN-SAND-001'),
('Tile Cutter - Wet Saw', 'Masonry Tools', 'Electric wet saw for tile cutting', 35.00, 'Excellent', 'Available', '2024-01-25', 'SN-TILE-001'),
('Extension Ladder - 24ft', 'Ladders', 'Aluminum extension ladder', 20.00, 'Good', 'Available', '2023-08-10', 'SN-LADDER-001'),
('Air Compressor - 20 Gal', 'Power Tools', 'Electric air compressor with hose', 30.00, 'Excellent', 'Available', '2024-02-28', 'SN-COMP-001'),
('Concrete Mixer - 5 Cu Ft', 'Concrete Equipment', 'Electric concrete mixer', 50.00, 'Good', 'Available', '2023-12-05', 'SN-MIX-001'),
('Carpet Cleaner - Commercial', 'Cleaning Equipment', 'Heavy duty carpet cleaning machine', 65.00, 'Excellent', 'Available', '2024-01-10', 'SN-CARPET-001'),
('Generator - 5000W', 'Power Equipment', 'Portable gas generator', 80.00, 'Good', 'Available', '2023-11-15', 'SN-GEN-001');

-- Insert rental data
-- Mix of Active, Completed, and Overdue rentals
INSERT INTO rental (customer_id, employee_id, rental_date, due_date, return_date, status, subtotal, late_fee, total_cost, notes) VALUES
-- Completed rentals
(1, 1, '2025-01-05', '2025-01-08', '2025-01-08', 'Completed', 75.00, 0.00, 75.00, 'Customer picked up on time'),
(2, 2, '2025-01-10', '2025-01-13', '2025-01-13', 'Completed', 165.00, 0.00, 165.00, 'Multiple items rented'),
(3, 1, '2025-01-15', '2025-01-18', '2025-01-18', 'Completed', 120.00, 0.00, 120.00, 'Weekend project'),
(4, 2, '2025-01-20', '2025-01-23', '2025-01-23', 'Completed', 200.00, 0.00, 200.00, 'Commercial job'),

-- Active rentals
(5, 3, '2025-01-22', '2025-01-27', NULL, 'Active', 150.00, 0.00, 150.00, 'Currently out'),
(6, 1, '2025-01-23', '2025-01-28', NULL, 'Active', 100.00, 0.00, 100.00, 'Home renovation'),
(7, 2, '2025-01-24', '2025-01-29', NULL, 'Active', 180.00, 0.00, 180.00, 'Large project'),

-- Overdue rentals (for testing late fees)
(8, 3, '2025-01-10', '2025-01-15', NULL, 'Overdue', 200.00, 20.00, 220.00, 'Customer notified of overdue status'),
(1, 1, '2025-01-12', '2025-01-17', NULL, 'Overdue', 150.00, 15.00, 165.00, 'Equipment still out'),
(2, 2, '2025-01-08', '2025-01-13', NULL, 'Overdue', 240.00, 24.00, 264.00, 'Follow up needed'),

-- Completed with late fee
(3, 3, '2025-01-05', '2025-01-08', '2025-01-11', 'Completed', 90.00, 9.00, 99.00, 'Returned late, fee applied'),
(4, 1, '2025-01-07', '2025-01-10', '2025-01-12', 'Completed', 120.00, 12.00, 132.00, 'Late return');

-- Insert rental_detail data
-- Rental 1: Power Drill for 3 days
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(1, 1, 1, 25.00, 3, 75.00);

-- Rental 2: Multiple items
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(2, 2, 1, 45.00, 3, 135.00),
(2, 8, 1, 20.00, 3, 60.00);

-- Rental 3: Pressure Washer for 3 days
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(3, 3, 1, 55.00, 3, 165.00);

-- Rental 4: Table Saw for 5 days
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(4, 5, 1, 60.00, 5, 300.00);

-- Rental 5: Floor Sander for 5 days (Active)
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(5, 6, 1, 75.00, 5, 375.00);

-- Rental 6: Lawn Mower for 5 days (Active)
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(6, 4, 1, 40.00, 5, 200.00);

-- Rental 7: Multiple items (Active)
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(7, 7, 1, 35.00, 5, 175.00),
(7, 9, 1, 30.00, 5, 150.00);

-- Rental 8: Concrete Mixer for 5 days (Overdue)
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(8, 10, 1, 50.00, 5, 250.00);

-- Rental 9: Pressure Washer for 3 days (Overdue)
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(9, 3, 1, 55.00, 3, 165.00);

-- Rental 10: Generator for 3 days (Overdue)
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(10, 12, 1, 80.00, 3, 240.00);

-- Rental 11: Air Compressor for 3 days (Completed with late fee)
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(11, 9, 1, 30.00, 3, 90.00);

-- Rental 12: Lawn Mower for 3 days (Completed with late fee)
INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total) VALUES
(12, 4, 1, 40.00, 3, 120.00);