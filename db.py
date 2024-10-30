CREATE DATABASE recibos_db;
USE recibos_db;

CREATE TABLE recibos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    contenido TEXT NOT NULL
);
