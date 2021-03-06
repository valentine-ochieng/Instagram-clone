from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from .forms import RegistrationForm, NewImageForm, UpdateUserProfile, ImageCommentForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .email import send_welcome_email
from .models import Image, Profile, User, Comment
from django.contrib.auth.decorators import login_required

def welcome(request):
    images=Image.objects.all()
    users=User.objects.all()
    # print(images)

    return render(request, "index.html", {"images":images, "users":users})


def registerUser(request):
    form=RegistrationForm()
    if request.method == "POST":
        form=RegistrationForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('index')

    else:
        form=RegistrationForm()
    title="Register New User"
    return render(request, 'registration/signup.html', {"title":title, "form":form})

def loginUser(request):
    if request.method =="POST":
        username = request.POST.get('username')
        # print(username)
        password = request.POST.get('password')
        # print(password)

        if username and password:
            user=authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                return redirect('welcome')

            else:
                messages.error(request, "Username or Password is incorrect")

        else:
            messages.error(request, "Field is empty. Enter Username and Password")

    title="Instaclone.com"
    return render(request, 'registration/login.html', {"success":messages, "title":title})


def logoutUser(request):
    logout(request)
    return redirect('index')

@login_required
def new_image(request):
    current_user = request.user
    if request.method=="POST":
        form=NewImageForm(request.POST, request.FILES)
        if form.is_valid():
            image=form.save(commit=False)
            image.profile=current_user
            image.save()

        return redirect('welcome')

    else:
        form=NewImageForm()
    return render(request, 'new_image.html', {"form":form})

def likes(request, pk):
    imagelike=get_object_or_404(Image, id=request.POST.get('likebutton'))
    imagelike.likes.add(request.user)
    return HttpResponseRedirect(reverse('viewphoto', args=[str(pk)]))

def followers(request, pk):
    follow=get_object_or_404(Profile, id=request.POST.get('follow'))
    follow.followers.add(request.user)
    return HttpResponseRedirect(reverse('userprofile', args=[str(pk)]))

@login_required
def viewPhoto(request, pk):
    image=Image.objects.get(id=pk)  
    form=ImageCommentForm()
    
    all_comments=Comment.objects.all()
    print(all_comments)

    likesonimage=get_object_or_404(Image, id=pk)
    total_likes=likesonimage.total_likes()
   
    if request.method == "POST":
        form=ImageCommentForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('viewphoto', args=[str(pk)]))

    else:
        form=ImageCommentForm()
    return render(request, 'oneimage.html', {"image": image, "form":form, "all_comments": all_comments,"total_likes": total_likes})

@login_required
def profile_view(request, pk):
    user=Profile.objects.filter(id=pk)
    images=Image.objects.filter(profile_id=pk)
    # print(user)

    user_followers=get_object_or_404(Profile, id=pk)
    total_followers=user_followers.total_followers()
    

    return render(request, "profile.html", {"user":user,"images":images, "total_followers":total_followers})

@login_required
def editpage(request, pk):
    form=UpdateUserProfile()
    user=Profile.objects.filter(id=pk)
    print(user)

    if request.method =="POST":
        form=UpdateUserProfile(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('userprofile', args=[str(pk)]))

    else:
        form=UpdateUserProfile()

    return render(request, "editprofile.html", {"form":form, "user":user})



def search_profile(request):
    if 'article' in request.GET and request.GET['article']:
        profile=request.GET.get('article')
        searched_profile=Image.search_by_user(profile)
        message=f"{profile}"

        return render(request, "search.html", {"message":message, "articles":searched_profile})

    else:
        message="You have not searched for any profile"
        return render(request, "search.html", {"message":message})

