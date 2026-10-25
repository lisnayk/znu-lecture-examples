<?php

namespace App\Database;

use App\Exceptions\InfrastructureUnavailable;
use App\Services\SecretCredentials;
use Illuminate\Database\Connectors\MySqlConnector;
use PDO;
use PDOException;
use Throwable;

class SecretsMySqlConnector extends MySqlConnector
{
    public function connect(array $config): PDO
    {
        $mode = config('infrastructure.auth_mode');
        if ($mode === 'secrets') {
            $ca = config('infrastructure.ca_file');
            if (! is_string($ca) || ! is_file($ca)) {
                throw new InfrastructureUnavailable('Файл довірених CA не знайдено. Перевірте DB_SSL_CA.');
            }
            $credentials = app(SecretCredentials::class)->get();
            $config['username'] = $credentials['username'];
            $config['password'] = $credentials['password'];
            $config['url'] = null;
            $config['unix_socket'] = '';
            $config['options'][PDO::MYSQL_ATTR_SSL_CA] = $ca;
            $config['options'][PDO::MYSQL_ATTR_SSL_VERIFY_SERVER_CERT] = true;
        } elseif ($mode !== 'local' || ! app()->environment(['local', 'testing'])) {
            throw new InfrastructureUnavailable('У production потрібен DB_AUTH_MODE=secrets.');
        }
        $config['options'][PDO::ATTR_TIMEOUT] = 5;
        $config['options'][PDO::ATTR_EMULATE_PREPARES] = false;
        try {
            return parent::connect($config);
        } catch (PDOException $error) {
            throw InfrastructureUnavailable::fromPdo($error);
        } catch (Throwable) {
            throw new InfrastructureUnavailable('MySQL-з’єднання відхилено. Перевірте endpoint, target проксі, порт 3306, SG, CA та облікові дані.');
        }
    }
}
