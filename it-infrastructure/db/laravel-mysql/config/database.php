<?php

return ['default' => env('DB_CONNECTION', 'mysql'), 'connections' => [
    'mysql' => ['driver' => 'mysql', 'host' => env('DB_HOST', '127.0.0.1'), 'port' => env('DB_PORT', '3306'),
        'database' => env('DB_DATABASE', 'infrastructure'), 'username' => env('DB_USERNAME', ''), 'password' => env('DB_PASSWORD', ''),
        'unix_socket' => '', 'charset' => 'utf8mb4', 'collation' => 'utf8mb4_unicode_ci', 'prefix' => '', 'prefix_indexes' => true,
        'strict' => true, 'engine' => null, 'options' => extension_loaded('pdo_mysql') ? array_filter([
            PDO::ATTR_TIMEOUT => 5,
            PDO::MYSQL_ATTR_SSL_CA => env('DB_TLS_REQUIRED', false) ? env('DB_SSL_CA') : null,
            PDO::MYSQL_ATTR_SSL_VERIFY_SERVER_CERT => true,
        ]) : []],
    'sqlite' => ['driver' => 'sqlite', 'database' => env('DB_DATABASE', database_path('database.sqlite')),
        'prefix' => '', 'foreign_key_constraints' => true]],
    'migrations' => ['table' => 'migrations', 'update_date_on_publish' => true]];
