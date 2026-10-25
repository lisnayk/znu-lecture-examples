<?php

namespace App\Console\Commands;

use App\Exceptions\InfrastructureUnavailable;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use PDOException;
use Throwable;

#[Signature('infra:prepare-database')]
#[Description('Створити відсутню MySQL-базу, якщо це ввімкнено в конфігурації')]
class PrepareDatabase extends Command
{
    public function handle(): int
    {
        if (! config('infrastructure.create_database')) {
            return self::SUCCESS;
        }

        $connectionName = config('database.default');
        $settings = config('database.connections.'.$connectionName);
        if (! is_array($settings) || ($settings['driver'] ?? null) !== 'mysql') {
            $this->error('Створення бази при старті підтримується лише для MySQL.');

            return self::FAILURE;
        }

        $name = $settings['database'] ?? '';
        if (! is_string($name) || preg_match('/\A[A-Za-z0-9_-]{1,64}\z/', $name) !== 1) {
            $this->error('Перевірте DB_DATABASE. Дозволено літери, цифри, дефіс і підкреслення; до 64 символів.');

            return self::FAILURE;
        }

        $settings['database'] = null;
        try {
            $connection = app('db.connector.mysql')->connect($settings);
            $connection->exec('CREATE DATABASE IF NOT EXISTS '.$this->quoteName($name).' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
        } catch (InfrastructureUnavailable $error) {
            $this->error($error->getMessage());

            return self::FAILURE;
        } catch (PDOException $error) {
            $this->error(InfrastructureUnavailable::fromPdo($error, 'CREATE DATABASE')->getMessage());

            return self::FAILURE;
        } catch (Throwable) {
            $this->error('Не вдалося підготувати MySQL-базу. Перевірте роль, секрет, target проксі, TLS та право CREATE DATABASE.');

            return self::FAILURE;
        }

        $this->info('SQL-база готова до міграцій.');

        return self::SUCCESS;
    }

    private function quoteName(string $name): string
    {
        return chr(96).$name.chr(96);
    }
}
