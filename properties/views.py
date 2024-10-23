from django.shortcuts import render

def property_list(request):
    return render(request, "properties/home_page.html")