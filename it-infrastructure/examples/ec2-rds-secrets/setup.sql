-- Виконати один раз через psql від адміністратора у базі infrastructure.
-- Пароль вводиться інтерактивно; він має збігатися зі значенням у Secrets Manager.
\set ON_ERROR_STOP on
CREATE ROLE ec2_rds_app LOGIN;
\password ec2_rds_app
CREATE SCHEMA demo;
CREATE TABLE demo.messages (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    message text NOT NULL
);
INSERT INTO demo.messages (message) VALUES
    ('Застосунок EC2 прочитав цей рядок із RDS.'),
    ('Роль EC2 дозволяє отримати секрет; SQL-права дозволяють читати таблицю.');
SELECT format('GRANT CONNECT ON DATABASE %I TO ec2_rds_app', current_database()) \gexec
GRANT USAGE ON SCHEMA demo TO ec2_rds_app;
GRANT SELECT ON demo.messages TO ec2_rds_app;
