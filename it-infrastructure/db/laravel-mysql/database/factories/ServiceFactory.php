<?php

namespace Database\Factories;

use App\Models\Service;
use Illuminate\Database\Eloquent\Factories\Factory;

/** @extends Factory<Service> */
class ServiceFactory extends Factory
{
    public function definition(): array
    {
        return ['name' => fake()->unique()->word(), 'environment' => 'staging', 'status' => 'healthy', 'description' => null];
    }
}
