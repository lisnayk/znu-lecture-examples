<?php
declare(strict_types=1);

$config = parse_ini_file('/etc/demo/app.ini');
$secret = file_get_contents('/run/secrets/db_password');

if ($config === false || $secret === false || trim($secret) === '') {
    fwrite(STDERR, "Не вдалося прочитати конфігурацію або секрет.\n");
    exit(1);
}

try {
    $dsn = sprintf('mysql:host=%s;dbname=%s;charset=utf8mb4', $config['host'], $config['database']);
    $db = new PDO($dsn, $config['user'], trim($secret));
    $database = $db->query('SELECT DATABASE()')->fetchColumn();
} catch (PDOException) {
    fwrite(STDERR, "Не вдалося під’єднатися до MySQL.\n");
    exit(1);
}

printf("MySQL: %s\n", $database);
