from django.shortcuts import render

def forbidden_view(request):
    return render(request, '401_forbidden.html')