from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1 
    fields = ('image',) 
    max_num = 10 

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'location', 'size', 'owner', 'pcreated_at')
    search_fields = ('title', 'location', 'owner__email')
    list_filter = ('owner', 'price', 'location')
    ordering = ('-pcreated_at',)
    list_per_page = 10
    inlines = [PropertyImageInline] 

admin.site.register(Property, PropertyAdmin)
