from django.shortcuts import render
from myapp.forms import UserLoginModelForm, UserRegistrationModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.contrib.auth.models import User
from myapp.models import UserInfoModel, AdsInfoModel, AdsPhotosModel, FavouriteAdsModel
from django.urls import reverse
from django.utils import timezone
import random

# Create your views here.

@login_required
def UserLogoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('user_login'))


def UserLoginView(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('loginhome', kwargs={'username': username}))
        else:
            return HttpResponse("YOU MADE A BLUNDER")
    else:
        return render(request, 'myapp/UserLogin.html')


def UserRegistrationView(request):
    if request.method=="POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password == confirm_password:
            user = User.objects.create(username=username, email=email, password=password)
            user.set_password(user.password)
            user.save()
            user_info = UserInfoModel.objects.create(user=user)
            user_info.save()
            
            login(request, user)

            return HttpResponseRedirect(reverse('loginhome', kwargs={'username': username}))
        else:
            return HttpResponse("INVALID CREDENTIALS!")
    else:
        return render(request, 'myapp/UserRegistration.html')


@login_required
def UserProfileView(request, username):
    profile_user = User.objects.get(username=username)  #The user whose profile is to be viewed can be the current user or any other user.
    info = UserInfoModel.objects.get(user=profile_user)
    var_dict = {"profile_user": profile_user, "info": info}
    return render(request, "myapp/profile.html", context=var_dict)


@login_required
def UserEditProfileView(request, username):
    user = User.objects.get(username=username)
    info = UserInfoModel.objects.get(user=user)
    if request.method == "POST":
        name = str(request.POST.get("name"))
        #checking whether the user has entered the full name of just the first name and inserting the data accordingly in the table.
        if " " in name:
            user.first_name, user.last_name = name.split(" ")
        else:
            user.first_name = name
            user.last_name = ""
        user.email = request.POST.get("email")
        info.gender = request.POST.get("gender")
        info.college = request.POST.get("college")
        info.branch = request.POST.get("course")
        info.description = request.POST.get("description")
        info.phone_number = request.POST.get("phone_number")
        info.address = request.POST.get("address")
        if "profile_pic" in request.FILES:
            info.profile_pic = request.FILES.get("profile_pic")
        user.save()
        info.save()
        return HttpResponseRedirect(reverse("user:profile", kwargs={"username":username}))

    else:
        var_dict = {"user":user, "info":info}
        return render(request, "myapp/edit_profile.html", context=var_dict)


def HomePageView(request, username=None):
    ads = AdsInfoModel.objects.all().order_by("posted_date")[:14]
    books = AdsInfoModel.objects.filter(category="book")[:6]
    stationary = AdsInfoModel.objects.filter(category="stationary")[:6]
    costumes = AdsInfoModel.objects.filter(category="costume")[:6]
    others = AdsInfoModel.objects.filter(category="other")[:6]
    if (username != None):
        cur = User.objects.get(username=username)   # Getting the user from user model
        cur_user = UserInfoModel.objects.get(user=cur)  # Getting the user from userinfomodel
        temp_favourites = FavouriteAdsModel.objects.filter(user=cur_user)
        favourites = []
        for favourite in temp_favourites:
            favourites.append(favourite.ad.pk)
        return render(request, "myapp/home.html", context={"ads": ads, "books": books, "stationary": stationary, "costumes": costumes, "others": others, "favourites": favourites})
    else:
        return render(request, "myapp/home.html", context={"ads": ads, "books": books, "stationary": stationary, "costumes": costumes, "others": others})


@login_required
def PostAdView(request, username):
    user = User.objects.get(username=username)
    info = UserInfoModel.objects.get(user=user)
    if request.method == "POST":
        category = request.POST.get("category")
        title = request.POST.get("title")
        description = request.POST.get("description")
        purpose = request.POST.get("purpose")
        price = request.POST.get("price")
        posted_date = timezone.now()
        # Price in case of donation is a null string so filtering that out.
        if price=="":
            price = 0
        ad = AdsInfoModel.objects.create(title=title, category=category, description=description, purpose=purpose, price=price, user=info, posted_date=posted_date)
        ad.save()
        for pic in request.FILES:
            pic_instance = AdsPhotosModel.objects.create(pic_parent=ad, photo=request.FILES['ad_pic'])
            pic_instance.save()
        return HttpResponseRedirect(reverse("ad_description", kwargs={"pk":ad.pk}))

    else:
        return render(request, "myapp/postad.html", context={"user": user, "info": info})


@login_required
def AdDescriptionView(request, pk):
    ad = AdsInfoModel.objects.get(id=pk)
    var_dict = {'ad': ad}
    return render(request, "myapp/ad_description.html", context=var_dict)


@login_required
def ViewBookAds(request, username):
    books = AdsInfoModel.objects.filter(category="book")
    cur = User.objects.get(username=username)   # Getting the user from user model
    cur_user = UserInfoModel.objects.get(user=cur)  # Getting the user from userinfomodel
    temp_favourites = FavouriteAdsModel.objects.filter(user=cur_user)
    favourites = []
    for favourite in temp_favourites:
        favourites.append(favourite.ad.pk)
    return render(request, "myapp/booksads.html", context={"books": books, "favourites": favourites})


@login_required
def ViewStationaryAds(request, username):
    stationary = AdsInfoModel.objects.filter(category="stationary")
    cur = User.objects.get(username=username)   # Getting the user from user model
    cur_user = UserInfoModel.objects.get(user=cur)  # Getting the user from userinfomodel
    temp_favourites = FavouriteAdsModel.objects.filter(user=cur_user)
    favourites = []
    for favourite in temp_favourites:
        favourites.append(favourite.ad.pk)
    return render(request, "myapp/stationaryads.html", context={"stationary": stationary, "favourites": favourites})


@login_required
def ViewUniformAds(request, username):
    costumes = AdsInfoModel.objects.filter(category="costume")
    cur = User.objects.get(username=username)   # Getting the user from user model
    cur_user = UserInfoModel.objects.get(user=cur)  # Getting the user from userinfomodel
    temp_favourites = FavouriteAdsModel.objects.filter(user=cur_user)
    favourites = []
    for favourite in temp_favourites:
        favourites.append(favourite.ad.pk)
    return render(request, "myapp/costumesads.html", context={"costumes": costumes, "favourites": favourites})


@login_required
def ViewOtherAds(request, username):
    others = AdsInfoModel.objects.filter(category="other")
    cur = User.objects.get(username=username)   # Getting the user from user model
    cur_user = UserInfoModel.objects.get(user=cur)  # Getting the user from userinfomodel
    temp_favourites = FavouriteAdsModel.objects.filter(user=cur_user)
    favourites = []
    for favourite in temp_favourites:
        favourites.append(favourite.ad.pk)
    return render(request, "myapp/otherads.html", context={"others": others, "favourites": favourites})


@login_required
def ViewFavouriteAds(request, username, pk=None, purpose=None):
    cur = User.objects.get(username=username)   # Getting the user from user model
    cur_user = UserInfoModel.objects.get(user=cur)  # Getting the user from userinfomodel
    if (pk != None and purpose == "deletead"):
        ad = FavouriteAdsModel.objects.get(pk=pk)
        ad.delete()
    elif (pk != None and purpose == "seelater"):
        cur_ad = AdsInfoModel.objects.get(pk=pk)
        FavouriteAdsModel.objects.create(user=cur_user, ad=cur_ad)
    elif (pk != None and purpose == "deleteadnew"):
        ads = FavouriteAdsModel.objects.all()
        for ad in ads:
            if ad.ad.pk == pk:
                ad.delete()
                break
    favourites = FavouriteAdsModel.objects.filter(user=cur_user)
    return render(request, "myapp/favouriteads.html", context={"favourites": favourites})


@login_required
def ViewPostedAds(request, username, pk=None):
    cur = User.objects.get(username=username)   # Getting the user from user model
    cur_user = UserInfoModel.objects.get(user=cur)  # Getting the user from userinfomodel
    if (pk != None):
        ad = AdsInfoModel.objects.get(pk=pk)
        ad.delete()
    posted = AdsInfoModel.objects.filter(user=cur_user)
    return render(request, "myapp/postedads.html", context={"posted": posted})



