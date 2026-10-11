<?php

namespace Database\Seeders;

use App\Models\Service;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        foreach ([
            ['Навчальний портал', 'production', 'healthy', 'Матеріали курсів і завдання для студентів.'],
            ['API каталогу', 'staging', 'maintenance', 'Тестове середовище перед наступним релізом.'],
            ['Сервіс повідомлень', 'development', 'incident', 'Перевірка відновлення після збою.'],
        ] as [$name,$environment,$status,$description]) {
            Service::firstOrCreate(['name' => $name], compact('environment', 'status', 'description'));
        }
    }
}
