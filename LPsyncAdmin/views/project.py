def project_index(request, pk=None):
    project = None
    if pk:
        project = get_object_or_404(Project, pk=pk)
    return render(request, 'project/project-index.html', {
        'project': project,
        'user': request.user,
    })