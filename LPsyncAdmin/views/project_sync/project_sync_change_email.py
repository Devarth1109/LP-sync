from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from LPsyncAdmin.models import User

def project_sync_change_email(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        try:
            new_email = request.POST['email']
            if new_email:
                user.email = new_email
                user.save()
                
                # Update the session email if it exists
                if 'email' in request.session:
                    request.session['email'] = new_email
                
                # Add success message (optional)
                messages.success(request, 'Email updated successfully.')
                
                # Redirect to project_sync_card
                return redirect('project_sync_card')
            else:
                return render(request, 'project_syncing/project_sync_change_email.html', {
                    'error': 'Please enter a valid email.',
                    'user': user
                })
        except KeyError:
            return render(request, 'project_syncing/project_sync_change_email.html', {
                'error': 'Email field is required.',
                'user': user
            })

    return render(request, 'project_syncing/project_sync_change_email.html', {
        'user': user
    })