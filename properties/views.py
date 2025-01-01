from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.http import require_http_methods
from django.db.models import Max
from chat.models import Chat

def property_detail(request, id):
    property = get_object_or_404(Property, id=id)

    if request.method == 'POST' and 'create_chat' in request.POST:
        chat, created = Chat.objects.get_or_create(
            property=property
        )
        chat.participants.add(request.user, property.owner)
        return redirect('chat_detail', chat_id=chat.id)

    return render(request, 'properties/property_detail.html', {'property': property})
def about_us(request):
    return render(request, 'properties/about.html')

@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.owner = request.user 
            property_instance.save()

            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(property=property_instance, image=image)

            return redirect('property_detail', id=property_instance.id)
    else:
        form = PropertyForm()

    return render(request, 'properties/add_property.html', {'form': form})

def main_view(request):
    return render(request, 'properties/main.html') 

def home_page(request):
    max_price = Property.objects.all().aggregate(max_price=Max('price'))['max_price'] or 0

    price_min = request.GET.get('price_min', 0)
    price_max = request.GET.get('price_max', max_price)
    query = request.GET.get('query', '') 

    properties = Property.objects.all()
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
    if query: 
        properties = properties.filter(title__icontains=query)

    if price_min:
        try:
            price_min = float(price_min)
            properties = properties.filter(price__gte=price_min)
        except ValueError:
            pass
        
    if price_max:
        try:
            price_max = float(price_max)
            properties = properties.filter(price__lte=price_max)
        except ValueError:
            pass

    favorite_properties = request.user.favorites.values_list('id', flat=True)

    return render(request, 'properties/home_page.html', {
        'properties': properties,
        'favorite_properties': favorite_properties,
        'query': query, 
        'price_min': price_min,
        'price_max': price_max,
        'max_price': max_price,
    })



@require_http_methods(["DELETE"])
@login_required
def remove_favorite(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    request.user.favorites.remove(property)
    return JsonResponse({'success': True})