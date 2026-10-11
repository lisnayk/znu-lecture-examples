<?php

namespace Tests\Feature;

use App\Models\Service;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ServiceCrudTest extends TestCase
{
    use RefreshDatabase;

    public function test_complete_crud_flow(): void
    {
        $this->post('/services', ['name' => 'Навчальний API', 'environment' => 'staging', 'status' => 'healthy', 'description' => 'Перша версія'])->assertRedirect();
        $service = Service::firstOrFail();
        $this->get('/services/'.$service->id)->assertOk()->assertSee('Навчальний API');
        $this->put('/services/'.$service->id, ['name' => 'Оновлений API', 'environment' => 'production', 'status' => 'maintenance', 'description' => 'Оновлення'])->assertRedirect('/services/'.$service->id);
        $this->assertDatabaseHas('services', ['id' => $service->id, 'name' => 'Оновлений API', 'status' => 'maintenance']);
        $this->get('/services/'.$service->id.'/remove')->assertOk()->assertSee('Видалити');
        $this->delete('/services/'.$service->id)->assertRedirect('/services');
        $this->assertDatabaseMissing('services', ['id' => $service->id]);
        $this->get('/services/'.$service->id)->assertNotFound();
    }

    public function test_validation_rejects_unknown_status_and_missing_name(): void
    {
        $this->from('/services/create')->post('/services', ['name' => '', 'environment' => 'other', 'status' => 'unknown'])
            ->assertRedirect('/services/create')->assertSessionHasErrors(['name', 'environment', 'status']);
        $this->assertDatabaseCount('services', 0);
    }

    public function test_mass_assignment_cannot_replace_identifier(): void
    {
        $this->post('/services', ['id' => 900, 'name' => 'API', 'environment' => 'staging', 'status' => 'healthy'])->assertRedirect();
        $this->assertNotEquals(900, Service::firstOrFail()->id);
    }

    public function test_search_and_filter_are_combined(): void
    {
        Service::factory()->create(['name' => 'Portal API', 'status' => 'incident']);
        Service::factory()->create(['name' => 'Portal UI', 'status' => 'healthy']);
        Service::factory()->create(['name' => 'Jobs', 'status' => 'incident']);
        $this->get('/services?q=Portal&status=incident')->assertOk()->assertSee('Portal API')->assertDontSee('Portal UI')->assertDontSee('Jobs');
    }

    public function test_user_content_is_escaped(): void
    {
        $service = Service::factory()->create(['name' => '<script>alert(1)</script>', 'description' => '<img src=x onerror=alert(2)>']);
        $this->get('/services/'.$service->id)->assertOk()->assertSee('&lt;script&gt;', false)->assertDontSee('<script>alert(1)</script>', false)->assertDontSee('<img src=x onerror=alert(2)>', false);
    }

    public function test_pagination_preserves_filter(): void
    {
        Service::factory()->count(14)->create(['status' => 'incident']);
        $this->get('/services?status=incident')->assertOk()->assertSee('page=2', false)->assertSee('status=incident', false);
    }

    public function test_confirmation_page_does_not_delete_record(): void
    {
        $service = Service::factory()->create();
        $this->get('/services/'.$service->id.'/remove')->assertOk();
        $this->assertDatabaseHas('services', ['id' => $service->id]);
    }
}
