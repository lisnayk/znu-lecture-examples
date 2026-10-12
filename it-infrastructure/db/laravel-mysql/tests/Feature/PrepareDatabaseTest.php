<?php

namespace Tests\Feature;

use LogicException;
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
}
