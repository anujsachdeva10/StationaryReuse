"""StationaryReuse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from myapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', views.UserRegistrationView, name="user_registration"),
    path('login/', views.UserLoginView, name="user_login"),
    path('logout/', views.UserLogoutView, name="user_logout"),
    path('profile/', include('myapp.urls')),
    path('', views.HomePageView, name="home"),  # for the unsigned user.
    path('user/<str:username>/', views.HomePageView, name="loginhome"),  # for the signed in user.
    path('<str:username>/postad/', views.PostAdView, name="postad"),
    path('ad-description/<int:pk>/', views.AdDescriptionView, name="ad_description"),
    path('user/<str:username>/booksads/', views.ViewBookAds, name="booksads"),
    path('user/<str:username>/stationaryads/', views.ViewStationaryAds, name="stationaryads"),
    path('user/<str:username>/uniformads/', views.ViewUniformAds, name="uniformads"),
    path('user/<str:username>/otherads/', views.ViewOtherAds, name="otherads"),
    path('favourites/<str:username>/', views.ViewFavouriteAds, name="favourites"),
    path('favourites/<str:username>/<int:pk>/<str:purpose>/', views.ViewFavouriteAds, name="favourites"), # URL to remove an add from the favourite ad option.
    path('postedads/<str:username>/', views.ViewPostedAds, name="postedads"),
    path('postedads/<str:username>/<int:pk>/', views.ViewPostedAds, name="postedads"),  # URL for deleting a posted ad.
    path('chat/', include('chat.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
