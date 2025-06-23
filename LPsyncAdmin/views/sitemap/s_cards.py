from django.shortcuts import render, redirect
from LPsyncAdmin.models import Project, User

def s_cards(request):
    if 'email' in request.session:
        current_user = User.objects.get(email=request.session['email'])
        projects = Project.objects.filter(user=current_user)
        return render(request, 'sitemap/sitemap_card.html', {'projects': projects, 'user': current_user})
    else:
        return redirect('login')