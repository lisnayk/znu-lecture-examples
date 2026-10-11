<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Service extends Model
{
    use HasFactory;

    public const ENVIRONMENTS = ['development' => 'Розробка', 'staging' => 'Тестове', 'production' => 'Робоче'];

    public const STATUSES = ['healthy' => 'Працює', 'maintenance' => 'Обслуговування', 'incident' => 'Збій'];

    protected $fillable = ['name', 'environment', 'status', 'description'];
}
