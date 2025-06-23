from django.shortcuts import render, redirect
from LPsyncAdmin.models import Project, User

def project_sync_card(request):
    if 'email' in request.session:
        current_user = User.objects.get(email=request.session['email'])
        projects = Project.objects.filter(user=current_user) 
        return render(request, 'project_syncing/project_sync_card.html', {'projects': projects, 'user': current_user})
    else:
        return redirect('login')