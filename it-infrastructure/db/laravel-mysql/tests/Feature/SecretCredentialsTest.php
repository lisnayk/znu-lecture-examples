<?php

namespace Tests\Feature;

use App\Exceptions\InfrastructureUnavailable;
use App\Services\SecretCredentials;
use Aws\Command;
use Aws\Exception\AwsException;
use Aws\Exception\CredentialsException;
use Aws\MockHandler;
use Aws\Result;
use Aws\SecretsManager\SecretsManagerClient;
use Tests\TestCase;

class SecretCredentialsTest extends TestCase
{
    private function client(MockHandler $handler): SecretsManagerClient
    {
        return new SecretsManagerClient(['region' => 'us-east-1', 'version' => 'latest', 'credentials' => ['key' => 'fixture', 'secret' => 'fixture'], 'handler' => $handler]);
    }

    public function test_reads_current_secret_without_changing_database_config(): void
    {
        config(['infrastructure.secret_arn' => 'arn:aws:secretsmanager:us-east-1:123456789012:secret:fixture']);
        $value = bin2hex(random_bytes(16));
        $handler = new MockHandler;
        $handler->append(new Result(['SecretString' => json_encode(['username' => 'ec2_laravel_app', 'password' => $value])]));
        $credentials = (new SecretCredentials($this->client($handler)))->get();
        $this->assertSame($value, $credentials['password']);
        $command = $handler->getLastCommand();
        $this->assertSame('GetSecretValue', $command->getName());
        $this->assertSame('AWSCURRENT', $command['VersionStage']);
        $this->assertNotSame($value, config('database.connections.mysql.password'));
    }

    public function test_bad_json_returns_safe_error(): void
    {
        config(['infrastructure.secret_arn' => 'arn:aws:secretsmanager:us-east-1:123456789012:secret:fixture']);
        $handler = new MockHandler([new Result(['SecretString' => 'private malformed secret'])]);
        try {
            (new SecretCredentials($this->client($handler)))->get();
            $this->fail('Expected safe error');
        } catch (InfrastructureUnavailable $error) {
            $this->assertStringNotContainsString('private malformed secret', $error->getMessage());
            $this->assertNull($error->getPrevious());
        }
    }

    public function test_missing_fields_are_rejected(): void
    {
        config(['infrastructure.secret_arn' => 'arn:aws:secretsmanager:us-east-1:123456789012:secret:fixture']);
        $handler = new MockHandler([new Result(['SecretString' => '{"username":"app"}'])]);
        $this->expectException(InfrastructureUnavailable::class);
        (new SecretCredentials($this->client($handler)))->get();
    }

    public function test_aws_error_does_not_leak_to_http(): void
    {
        config(['database.default' => 'mysql', 'infrastructure.auth_mode' => 'secrets', 'infrastructure.ca_file' => '/etc/ssl/certs/ca-certificates.crt',
            'infrastructure.secret_arn' => 'arn:aws:secretsmanager:us-east-1:123456789012:secret:fixture']);
        $handler = new MockHandler([new AwsException('private credential content', new Command('GetSecretValue'))]);
        $this->app->instance(SecretsManagerClient::class, $this->client($handler));
        $this->get('/')->assertStatus(503)->assertSee('тимчасово недоступний')->assertDontSee('private credential content');
    }

    public function test_known_aws_error_codes_are_preserved_without_response_content(): void
    {
        config(['infrastructure.secret_arn' => 'arn:aws:secretsmanager:us-east-1:123456789012:secret:fixture']);
        foreach (['AccessDeniedException', 'ResourceNotFoundException', 'DecryptionFailure', 'InvalidRequestException'] as $code) {
            $original = new AwsException('private-credentials', new Command('GetSecretValue'), ['code' => $code]);
            $handler = new MockHandler([$original]);
            try {
                (new SecretCredentials($this->client($handler)))->get();
                $this->fail('Expected safe infrastructure failure.');
            } catch (InfrastructureUnavailable $error) {
                $this->assertStringContainsString($code, $error->getMessage());
                $this->assertStringNotContainsString('private-credentials', $error->getMessage());
                $this->assertNull($error->getPrevious());
            }
        }
    }

    public function test_missing_instance_credentials_have_a_separate_safe_diagnostic(): void
    {
        config(['infrastructure.secret_arn' => 'arn:aws:secretsmanager:us-east-1:123456789012:secret:fixture']);
        $handler = new MockHandler([new CredentialsException('private-credentials')]);
        try {
            (new SecretCredentials($this->client($handler)))->get();
            $this->fail('Expected safe infrastructure failure.');
        } catch (InfrastructureUnavailable $error) {
            $this->assertStringContainsString('EC2 credentials:', $error->getMessage());
            $this->assertStringNotContainsString('private-credentials', $error->getMessage());
            $this->assertNull($error->getPrevious());
        }
    }

    public function test_unknown_aws_error_code_does_not_reach_the_diagnostic(): void
    {
        config(['infrastructure.secret_arn' => 'arn:aws:secretsmanager:us-east-1:123456789012:secret:fixture']);
        $handler = new MockHandler([new AwsException('private-response', new Command('GetSecretValue'), ['code' => 'private-code'])]);
        try {
            (new SecretCredentials($this->client($handler)))->get();
            $this->fail('Expected safe infrastructure failure.');
        } catch (InfrastructureUnavailable $error) {
            $this->assertStringContainsString('Secrets Manager:', $error->getMessage());
            $this->assertStringNotContainsString('private-response', $error->getMessage());
            $this->assertStringNotContainsString('private-code', $error->getMessage());
        }
    }
}
