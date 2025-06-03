from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Max
from chat.models import Chat
from django.contrib import messages
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt


def property_detail(request, id):
    property = Property.objects.get(id=id)
    if request.method == 'POST' and 'create_chat' not in request.POST:
        if property.owner == request.user:
            messages.warning(request, 'Вы не можете начать чат с самим собой.')
            return redirect('property_detail', id=property.id)
    if request.method == 'POST' and 'create_chat' in request.POST:
        buyer = request.user
        seller = property.owner
        chat, created = Chat.objects.get_or_create(
            property=property,
            buyer=buyer,
            seller=seller
        )
        return redirect('chat_detail', chat_id=chat.id)

    return render(request, 'properties/property_detail.html', {'property': property})

def about_us(request):
    return render(request, 'properties/about.html')

@login_required
def update_property(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        location = request.POST.get('location')
        size = request.POST.get('size')
        
        property_instance.title = title
        property_instance.description = description
        property_instance.price = price
        property_instance.location = location
        property_instance.size = size
        
        property_instance.save()

        return redirect('property_detail', id=property_instance.id)
    
    return render(request, 'properties/update_property.html', {'property': property_instance})

@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.owner = request.user
            property_instance.save()

            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(property=property_instance, image=image)

            messages.success(request, 'Объявление отправлено на модерацию.')
            return redirect('property_detail', id=property_instance.id)
        else:
            messages.error(request, 'Не удалось загрузить объявление. Проверьте правильность заполнения всех полей.')
    else:
        form = PropertyForm()

    return render(request, 'properties/add_property.html', {'form': form})

def main_view(request):
    return render(request, 'properties/main.html') 

from django.core.paginator import Paginator

def home_page(request):
    tags = Tag.objects.all()
    max_price = Property.objects.aggregate(max_price=Max('price'))['max_price'] or 0

    price_min = request.GET.get('price_min', 0)
    price_max = request.GET.get('price_max', max_price)
    query = request.GET.get('query', '')
    order_by = request.GET.get('order_by', '')
    selected_tags = request.GET.getlist('tags')

    try:
        price_min = float(price_min)
        price_max = float(price_max)
        if price_min > price_max:
            price_min, price_max = price_max, price_min
    except ValueError:
        price_min = 0
        price_max = max_price

    properties = Property.objects.filter(
        price__gte=price_min,
        price__lte=price_max,
        approved=True  
    )

    if query:
        properties = properties.filter(title__icontains=query)

    if selected_tags:
        properties = properties.filter(tags__id__in=selected_tags).distinct()

    if order_by == 'price_asc':
        properties = properties.order_by('price')
    elif order_by == 'price_desc':
        properties = properties.order_by('-price')

    paginator = Paginator(properties, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    favorite_properties = request.user.favorites.values_list('id', flat=True) if request.user.is_authenticated else []

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            property_id = data.get('property_id')

            if request.user.is_authenticated:
                try:
                    property = Property.objects.get(id=property_id)
                except Property.DoesNotExist:
                    return JsonResponse({'status': 'not_found'}, status=404)

                if property in request.user.favorites.all():
                    request.user.favorites.remove(property)
                    status = 'removed'
                else:
                    request.user.favorites.add(property)
                    status = 'added'

                return JsonResponse({'status': status})
            else:
                return JsonResponse({'status': 'unauthenticated'}, status=403)
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'status': 'bad_request'}, status=400)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = ""
        for property in page_obj:
            html += f"""
                <div class="property-card">
                    <h3>{property.title}</h3>
                    <p>{property.price} USD</p>
                    <p>{property.description[:100]}...</p>
                </div>
            """
        return JsonResponse({'html': html})

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_string = query_params.urlencode()

    return render(request, 'properties/home_page.html', {
        'properties': page_obj.object_list,
        'page_obj': page_obj,
        'favorite_properties': favorite_properties,
        'query': query,
        'price_min': price_min,
        'price_max': price_max,
        'max_price': max_price,
        'order_by': order_by,
        'tags': tags,
        'selected_tags': list(map(int, selected_tags)),
        'query_string': query_string,
    })

@require_http_methods(["DELETE"])
@login_required
def remove_favorite(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    request.user.favorites.remove(property)
    return JsonResponse({'success': True})