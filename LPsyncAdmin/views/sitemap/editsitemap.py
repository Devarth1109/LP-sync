from django.shortcuts import render, redirect, get_object_or_404
from LPsyncAdmin.models import Sitemap, Project, User

def editsitemap(request, id):
    sitemap = get_object_or_404(Sitemap, id=id)
    projects = Project.objects.all()
    user = User.objects.get(email=request.session['email'])

    if request.method == 'POST':
        sitemap.url = request.POST.get('url')
        sitemap.sitemap_name = request.POST.get('sitemap_name')
        sitemap.category = request.POST.get('category')
        project_id = request.POST.get('project_name')
        sitemap.project_id = project_id
        sitemap.save()
        return redirect('site_map', pk=sitemap.project_id)  # Use project id here

    return render(request, "sitemap/editsitemap.html", {'sitemap': sitemap, 'projects': projects, 'user': user})