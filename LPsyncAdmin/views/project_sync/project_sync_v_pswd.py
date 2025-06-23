from django.shortcuts import render, redirect, get_object_or_404
from LPsyncAdmin.models import User

def project_sync_v_pswd(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        try:
            v_password = request.POST['v_password']
            if v_password == user.pswd:
                return redirect('project_sync_change_email', user_id=user.id)  
            else:
                return render(request, 'project_syncing/project_sync_v_pswd.html', {'error': 'Incorrect password.', 'user': user})
        except KeyError:
            return render(request, 'project_syncing/project_sync_v_pswd.html', {'error': 'Please fill in the password.', 'user': user})
    return render(request, 'project_syncing/project_sync_v_pswd.html', {'error': '', 'user': user})
