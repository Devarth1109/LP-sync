from django.shortcuts import render, redirect, get_object_or_404
from LPsyncAdmin.models import Sitemap, Project, User

def addsitemap(request, pk):
    user = get_object_or_404(User, pk=pk)
    projects = Project.objects.all()
    if request.method == 'POST':
        url = request.POST.get('url')
        sitemap_name = request.POST.get('sitemap_name')
        category = request.POST.get('category')
        project_id = request.POST.get('project_name')

        # Retrieve the selected project from the database
        project = Project.objects.get(id=project_id)

        # Create a new instance of the Sitemap model and assign the form data
        instance = Sitemap(
            url=url,
            sitemap_name=sitemap_name,
            category=category,
            project_id=project_id,
            user=user  # <-- Add this line
        )
        instance.save()
        return redirect('/sitemap/%s' % project.id) 

    return render(request, 'sitemap/addsitemap.html', {'projects': projects, 'user': user})