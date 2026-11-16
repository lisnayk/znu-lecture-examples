CREATE TABLE products (
  id INT PRIMARY KEY,
  name VARCHAR(80) NOT NULL
);

INSERT INTO products (id, name) VALUES
  (1, 'USB-C cable'),
  (2, 'HDMI adapter');
