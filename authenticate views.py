from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


# Create your views here.



def register_user(request):

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('authentication:login')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            if user is not None:
                login(request, user)
                if user.is_superuser or user.role == 2:
                    return redirect('super_admin_dashboard:super_admin_dashboard')
                elif user.role == 1:
                    return redirect('waste_collector:waste_collector_dashboard')
                elif user.role == 3:
                    return redirect('admin_dashboard:admin_dashboard')
                else:
                    return redirect('customer:customer_dashboard')
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})




@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('authentication:login')
