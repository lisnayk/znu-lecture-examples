@extends('layout')
@section('title',$service->exists ? 'Редагування сервісу' : 'Новий сервіс')
@section('content')
<div class="page-heading"><a class="back" href="{{ route('services.index') }}">← До каталогу</a><p class="eyebrow">{{ $service->exists ? 'Оновлення запису' : 'Новий запис' }}</p><h1>{{ $service->exists ? 'Редагувати сервіс' : 'Додати сервіс' }}</h1><p class="lead">Укажіть середовище та поточний стан. Примітка допоможе пояснити зміни.</p></div>
<div class="form-layout"><form class="editor" method="post" action="{{ $service->exists ? route('services.update',$service) : route('services.store') }}">
@csrf @if($service->exists) @method('PUT') @endif
@if($errors->any())<div class="error-summary" role="alert"><p>Перевірте поля форми.</p><ul>@foreach($errors->all() as $error)<li>{{ $error }}</li>@endforeach</ul></div>@endif
<div class="field"><label for="name">Назва сервісу <span class="required">обов’язково</span></label><input id="name" name="name" maxlength="120" required value="{{ old('name',$service->name) }}" @error('name') aria-invalid="true" aria-describedby="name-error" @enderror>@error('name')<p class="error" id="name-error">{{ $message }}</p>@enderror</div>
<div class="field-pair"><div class="field"><label for="environment">Середовище</label><select id="environment" name="environment" required>@foreach(\App\Models\Service::ENVIRONMENTS as $key=>$label)<option value="{{ $key }}" @selected(old('environment',$service->environment)===$key)>{{ $label }}</option>@endforeach</select></div>
<div class="field"><label for="status">Стан сервісу</label><select id="status" name="status" required>@foreach(\App\Models\Service::STATUSES as $key=>$label)<option value="{{ $key }}" @selected(old('status',$service->status)===$key)>{{ $label }}</option>@endforeach</select></div></div>
<div class="field"><label for="description">Примітка <span class="optional">необов’язково</span></label><textarea id="description" name="description" rows="5" maxlength="2000">{{ old('description',$service->description) }}</textarea><p class="hint">До 2000 символів. Наприклад, призначення сервісу або причина обслуговування.</p></div>
<div class="form-actions"><button class="button" type="submit">{{ $service->exists ? 'Зберегти зміни' : 'Додати сервіс' }}</button><a class="text-link" href="{{ $service->exists ? route('services.show',$service) : route('services.index') }}">Скасувати</a></div></form>
<aside class="aside-note"><span class="note-number">01</span><h2>Один сервіс.<br>Один запис.</h2><p>Для різних середовищ створюйте окремі записи. Так тестовий збій не змінить стан робочого сервісу.</p></aside></div>
@endsection
