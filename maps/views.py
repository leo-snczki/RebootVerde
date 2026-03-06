from django.shortcuts import render

# Create your views here.

def recycle_map_view(request):
    return render(request, "maps/recycle_map.html")