<?php

namespace Tests\Feature;

use App\Exceptions\InfrastructureUnavailable;
use App\Models\Service;
use Aws\MockHandler;
use Aws\Result;
use Aws\SecretsManager\SecretsManagerClient;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

class MySqlIntegrationTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        if (getenv('RUN_MYSQL_INTEGRATION') !== '1') {
            $this->markTestSkipped('Потрібен тимчасовий MySQL TLS-стенд.');
        }
        config(['database.default' => 'mysql', 'database.connections.mysql.database' => 'lecture_test', 'infrastructure.auth_mode' => 'secrets',
            'infrastructure.secret_arn' => 'arn:aws:secretsmanager:us-east-1:123456789012:secret:fixture',
            'infrastructure.ca_file' => getenv('MYSQL_TEST_CA')]);
        $result = new Result(['SecretString' => json_encode(['username' => getenv('DB_USERNAME'), 'password' => getenv('DB_PASSWORD')])]);
        $handler = new MockHandler([$result, $result, $result, $result]);
        $client = new SecretsManagerClient(['region' => 'us-east-1', 'version' => 'latest',
            'credentials' => ['key' => 'fixture', 'secret' => 'fixture'], 'handler' => $handler]);
        $this->app->instance(SecretsManagerClient::class, $client);
        DB::purge('mysql');
    }

    public function test_migrations_are_idempotent_and_tls_is_used(): void
    {
        $this->artisan('migrate', ['--force' => true])->assertSuccessful();
        Service::create(['name' => 'Migration fixture', 'environment' => 'staging', 'status' => 'healthy']);
        $this->artisan('migrate', ['--force' => true])->assertSuccessful();
        $this->assertSame(1, Service::where('name', 'Migration fixture')->count());
        $this->assertSame(1, DB::table('migrations')->count());
        $tls = DB::select("SHOW SESSION STATUS LIKE 'Ssl_cipher'");
        $this->assertNotEmpty($tls[0]->Value);
        Service::where('name', 'Migration fixture')->delete();
    }

    public function test_crud_with_secret_credentials_and_real_mysql(): void
    {
        $this->artisan('migrate', ['--force' => true])->assertSuccessful();
        $this->post('/services', ['name' => 'TLS CRUD fixture', 'environment' => 'staging', 'status' => 'healthy'])->assertRedirect();
        $service = Service::where('name', 'TLS CRUD fixture')->firstOrFail();
        $this->get('/services/'.$service->id)->assertOk()->assertSee('TLS CRUD fixture');
        $this->put('/services/'.$service->id, ['name' => 'TLS CRUD fixture', 'environment' => 'production', 'status' => 'incident'])->assertRedirect();
        $this->assertSame('incident', $service->fresh()->status);
        $this->delete('/services/'.$service->id)->assertRedirect('/services');
        $this->assertNull(Service::find($service->id));
    }

    public function test_untrusted_ca_prevents_connection(): void
    {
        config(['infrastructure.ca_file' => getenv('MYSQL_TEST_WRONG_CA')]);
        DB::purge('mysql');
        $this->expectException(InfrastructureUnavailable::class);
        DB::connection('mysql')->getPdo();
    }

    public function test_local_auth_mode_is_rejected_in_production(): void
    {
        $this->app->instance('env', 'production');
        config(['infrastructure.auth_mode' => 'local']);
        DB::purge('mysql');
        $this->expectException(InfrastructureUnavailable::class);
        DB::connection('mysql')->getPdo();
    }
}
