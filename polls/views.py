from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the form without committing it to the database yet
            user = form.save(commit=False)
            
            # Set the user's password (hashed automatically)
            user.set_password(form.cleaned_data['password'])
            
            # Save the user object with hashed password
            user.save()
            
            # Authenticate and log in the user
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {user.first_name}! Your account has been successfully created.')
                return redirect('home')  # Redirect to a 'home' page or another view
            else:
                messages.error(request, 'Authentication failed. Please try logging in manually.')
                return redirect('login')  # Redirect to login if authentication fails
    else:
        form = UserRegistrationForm()
    
    return render(request, 'polls/registration.html', {'form': form})
