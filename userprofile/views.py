from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from toptool.shortcuts import render
from .forms import ProfileForm

# edit user profile (allowed only by logged in users)
@login_required
def edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('editprofile')
    else:
        form = ProfileForm(instance=request.user.profile)

    context = {'form': form}
    return render(request, 'userprofile/edit.html', context)
