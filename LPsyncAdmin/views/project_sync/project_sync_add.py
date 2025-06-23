from django.shortcuts import render, redirect
from LPsyncAdmin.models import ProjectSyncing, User, Project

# ...existing code...
def project_sync_add(request, pk):
    if 'email' not in request.session:
        return redirect('login')

    current_user = User.objects.get(email=request.session['email'])
    try:
        project = Project.objects.get(pk=pk, user=current_user)
    except Project.DoesNotExist:
        return redirect('401_forbidden')

    # Try to get the existing ProjectSyncing for this project and user
    project_sync = ProjectSyncing.objects.filter(project=project, user=current_user).first()

    if request.method == "POST":
        platform = request.POST.get('platform')
        endpoint_url = request.POST.get('endpoint')
        token_url = request.POST.get('token')
        admin_username = request.POST.get('admin_username')
        admin_email = request.POST.get('admin_email')
        admin_password = request.POST.get('admin_password')

        # Update or create ProjectSyncing
        ProjectSyncing.objects.update_or_create(
            user=current_user,
            project=project,
            defaults={
                'platform': platform,
                'endpoint_url': endpoint_url,
                'token_url': token_url,
                'admin_username': admin_username,
                'admin_email': admin_email,
                'admin_password': admin_password,
            }
        )
        return redirect('project_sync_card')

    return render(request, "project_syncing/project_sync_add.html", {
        'project_sync': project_sync,
        'user': current_user,
        'project': project
    })
# ...existing code...