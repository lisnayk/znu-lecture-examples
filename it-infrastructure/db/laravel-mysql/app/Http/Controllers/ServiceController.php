<?php

namespace App\Http\Controllers;

use App\Http\Requests\ServiceRequest;
use App\Models\Service;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;
use Illuminate\View\View;

class ServiceController extends Controller
{
    public function index(Request $request): View
    {
        $filters = $request->validate(['q' => ['nullable', 'string', 'max:120'], 'status' => ['nullable', Rule::in(array_keys(Service::STATUSES))]]);
        $query = Service::query();
        if (! empty($filters['q'])) {
            $query->where('name', 'like', '%'.$filters['q'].'%');
        }
        if (! empty($filters['status'])) {
            $query->where('status', $filters['status']);
        }
        $services = $query->orderByDesc('id')->paginate(12)->withQueryString();
        $counts = Service::query()->selectRaw('status, COUNT(*) AS total')->groupBy('status')->pluck('total', 'status');

        return view('services.index', compact('services', 'counts', 'filters'));
    }

    public function create(): View
    {
        return view('services.form', ['service' => new Service(['environment' => 'staging', 'status' => 'healthy'])]);
    }

    public function store(ServiceRequest $request): RedirectResponse
    {
        $service = Service::create($request->validated());

        return redirect()->route('services.show', $service)->with('notice', 'Сервіс додано.');
    }

    public function show(Service $service): View
    {
        return view('services.show', compact('service'));
    }

    public function edit(Service $service): View
    {
        return view('services.form', compact('service'));
    }

    public function update(ServiceRequest $request, Service $service): RedirectResponse
    {
        $service->update($request->validated());

        return redirect()->route('services.show', $service)->with('notice', 'Зміни збережено.');
    }

    public function confirmDelete(Service $service): View
    {
        return view('services.delete', compact('service'));
    }

    public function destroy(Service $service): RedirectResponse
    {
        $service->delete();

        return redirect()->route('services.index')->with('notice', 'Сервіс видалено.');
    }
}
