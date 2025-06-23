from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from LPsyncAdmin.models import Sitemap, User, Project

def deleteall_sitemap(request, project_id):
    user = User.objects.get(email=request.session['email'])
    project = get_object_or_404(Project, id=project_id, user=user)
    Sitemap.objects.filter(user=user, project=project).delete()
    return redirect(reverse('site_map', args=[project.id]))