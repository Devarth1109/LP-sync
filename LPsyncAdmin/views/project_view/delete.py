from django.shortcuts import render,redirect
from LPsyncAdmin.models import Project
from django.urls import reverse

def delete(request,id):
	project = Project.objects.get(id=id)
	project.delete()
	return redirect(reverse('project-view', args=[project.user.pk]))