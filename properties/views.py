from django.shortcuts import render, redirect
import json
from .forms import PropertyForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Property
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404

def property_detail(request, id):
    property = get_object_or_404(Property, id=id)
    return render(request, 'properties/property_detail.html', {'property': property})

@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            return redirect('home_page')
    else:
        form = PropertyForm()

    return render(request, 'properties/add_property.html', {'form': form})

@login_required
def property_home(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        property_id = data.get('property_id')
        property = get_object_or_404(Property, id=property_id)

        if property in request.user.favorites.all():
            request.user.favorites.remove(property)
            status = 'removed'
        else:
            request.user.favorites.add(property)
            status = 'added'

        return JsonResponse({'status': status})

    properties = Property.objects.all()
    favorite_properties = request.user.favorites.values_list('id', flat=True)

    return render(request, 'properties/home_page.html', {
        'properties': properties,
        'favorite_properties': favorite_properties
    })

@require_http_methods(["DELETE"])
@login_required
def remove_favorite(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    request.user.favorites.remove(property)
    return JsonResponse({'success': True})