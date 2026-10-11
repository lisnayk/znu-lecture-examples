-- Виконати один раз від адміністратора MySQL 8.4.
-- CREATE USER поверне випадковий пароль; перенести його в Secrets Manager.
CREATE DATABASE IF NOT EXISTS infrastructure CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ec2_laravel_app'@'%' IDENTIFIED BY RANDOM PASSWORD REQUIRE SSL;
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES
ON infrastructure.* TO 'ec2_laravel_app'@'%';
