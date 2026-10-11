<?php

namespace App\Http\Requests;

use App\Models\Service;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class ServiceRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return ['name' => ['required', 'string', 'max:120'], 'environment' => ['required', Rule::in(array_keys(Service::ENVIRONMENTS))],
            'status' => ['required', Rule::in(array_keys(Service::STATUSES))], 'description' => ['nullable', 'string', 'max:2000']];
    }

    public function messages(): array
    {
        return ['name.required' => 'Укажіть назву сервісу.', 'name.max' => 'Назва має містити до 120 символів.',
            'environment.required' => 'Виберіть середовище.', 'environment.in' => 'Виберіть середовище зі списку.',
            'status.required' => 'Виберіть стан сервісу.', 'status.in' => 'Виберіть стан зі списку.',
            'description.max' => 'Опис має містити до 2000 символів.'];
    }
}
