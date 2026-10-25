<?php

namespace Tests\Feature;

use App\Database\SecretsMySqlConnector;
use App\Exceptions\InfrastructureUnavailable;
use Illuminate\Support\Facades\Artisan;
use LogicException;
use Mockery;
use PDO;
use PDOException;
use RuntimeException;
use Tests\TestCase;

class PrepareDatabaseTest extends TestCase
{
    public function test_disabled_preparation_does_not_open_a_connection(): void
    {
        config(['infrastructure.create_database' => false]);
        $this->app->bind('db.connector.mysql', function (): never {
            throw new LogicException('A database connection must not be opened.');
        });
        $this->artisan('infra:prepare-database')->assertSuccessful();
    }

    public function test_invalid_name_is_rejected_before_any_connection(): void
    {
        config(['infrastructure.create_database' => true, 'database.default' => 'mysql',
            'database.connections.mysql.database' => 'database; injected SQL']);
        $this->app->bind('db.connector.mysql', function (): never {
            throw new LogicException('A database connection must not be opened.');
        });
        $this->artisan('infra:prepare-database')->assertFailed();
    }

    public function test_known_infrastructure_failure_is_visible_in_console(): void
    {
        config(['infrastructure.create_database' => true, 'database.default' => 'mysql',
            'database.connections.mysql.database' => 'demo-db']);
        $connector = Mockery::mock(SecretsMySqlConnector::class);
        $connector->shouldReceive('connect')->once()->andThrow(
            new InfrastructureUnavailable('EC2 credentials: перевірте IAM instance profile.')
        );
        $this->app->instance('db.connector.mysql', $connector);

        $this->assertSame(1, Artisan::call('infra:prepare-database'));
        $this->assertStringContainsString('EC2 credentials:', Artisan::output());
    }

    public function test_create_database_failure_reports_codes_without_raw_sql_details(): void
    {
        config(['infrastructure.create_database' => true, 'database.default' => 'mysql',
            'database.connections.mysql.database' => 'demo-db']);
        $error = new PDOException('private-password-and-query');
        $error->errorInfo = ['42000', 1044, 'private-password-and-query'];
        $pdo = Mockery::mock(PDO::class);
        $pdo->shouldReceive('exec')->once()->andThrow($error);
        $connector = Mockery::mock(SecretsMySqlConnector::class);
        $connector->shouldReceive('connect')->once()->andReturn($pdo);
        $this->app->instance('db.connector.mysql', $connector);

        $this->assertSame(1, Artisan::call('infra:prepare-database'));
        $this->assertStringContainsString('CREATE DATABASE: SQLSTATE=42000; MySQL=1044.', Artisan::output());
        $this->assertStringNotContainsString('private-password-and-query', Artisan::output());
    }

    public function test_pdo_diagnostic_does_not_retain_the_original_exception(): void
    {
        $original = new PDOException('private-credentials');
        $original->errorInfo = ['HY000', 2026, 'private-credentials'];
        $safe = InfrastructureUnavailable::fromPdo($original);

        $this->assertStringContainsString('MySQL connection: SQLSTATE=HY000; MySQL=2026.', $safe->getMessage());
        $this->assertStringContainsString('TLS', $safe->getMessage());
        $this->assertStringNotContainsString('private-credentials', $safe->getMessage());
        $this->assertNull($safe->getPrevious());

        $original->errorInfo = ['private-credentials', 0, 'private-credentials'];
        $this->assertStringNotContainsString('private-credentials', InfrastructureUnavailable::fromPdo($original)->getMessage());
    }

    public function test_unexpected_failure_does_not_expose_its_message(): void
    {
        config(['infrastructure.create_database' => true, 'database.default' => 'mysql',
            'database.connections.mysql.database' => 'demo-db']);
        $connector = Mockery::mock(SecretsMySqlConnector::class);
        $connector->shouldReceive('connect')->once()->andThrow(new RuntimeException('private-credentials'));
        $this->app->instance('db.connector.mysql', $connector);

        $this->assertSame(1, Artisan::call('infra:prepare-database'));
        $this->assertStringContainsString('Не вдалося підготувати MySQL-базу.', Artisan::output());
        $this->assertStringNotContainsString('private-credentials', Artisan::output());
    }
}
