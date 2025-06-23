from django.shortcuts import render, redirect
from LPsyncAdmin.models import ProjectSyncing
from django.shortcuts import get_object_or_404

def project_sync_delete(request, id):
    project_sync = get_object_or_404(ProjectSyncing, id=id)
    project_sync.delete()
    return redirect('project_sync_card') 