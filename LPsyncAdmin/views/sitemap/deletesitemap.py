from django.shortcuts import redirect
from django.urls import reverse
from LPsyncAdmin.models import Sitemap
from django.http import HttpResponse

def delete(request, id):
    try:
        sitemap = Sitemap.objects.get(id=id)
        project_id = sitemap.project_id  # Save project id before deleting
        sitemap.delete()
        return redirect(reverse('site_map', args=[project_id]))  # Redirect to project sitemaps
    except Sitemap.DoesNotExist:
        return HttpResponse(f"Sitemap with ID {id} does not exist.", status=404)