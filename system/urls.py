"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from book_clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('user_page/', views.user_page, name = 'user_page'),
    path('create_club/', views.create_club, name = 'create_club'),
    path('user_club_list/', views.user_club_list, name = 'user_club_list'),
    path('applicable_clubs/', views.applicable_clubs, name = 'applicable_clubs'),
    path('apply_to_club/<int:club_id>/', views.apply_to_club, name = 'apply_to_club'),
    path('user_application_list/', views.user_application_list, name = 'user_application_list'),
    path('club_page/<int:club_id>/', views.club_page, name = 'club_page'),
    path('club_edit/<int:club_id>/', views.club_edit, name = 'club_edit'),
    path('disband_club/<int:club_id>/', views.disband_club, name = 'disband_club'),
    path('club_application_list/<int:club_id>/', views.club_application_list, name = 'club_application_list'),
    path('accept_application/<int:user_id>/<int:club_id>/', views.accept_application, name = 'accept_application'),
    path('reject_application/<int:user_id>/<int:club_id>/', views.reject_application, name = 'reject_application'),
    path('member_list/<int:club_id>/', views.member_list, name = 'member_list'),
    path('kick_member/<int:user_id>/<int:club_id>/', views.kick_member, name = 'kick_member'),
    path('shedule_meeting/<int:club_id>/', views.shedule_meeting, name = 'shedule_meeting'),
    path('meeting_book_selection/<int:club_id>/<int:meeting_id>/<int:page>/', views.meeting_book_selection, name = 'meeting_book_selection'),
    path('select_meeting_book/<int:club_id>/<int:meeting_id>/<str:book_isbn>/', views.select_meeting_book, name = 'select_meeting_book'),
    path('meeting_list/<int:club_id>/', views.meeting_list, name = 'meeting_list'),
    path('meeting/<int:club_id>/<int:meeting_id>/', views.meeting, name = 'meeting'),
    path('send/<int:club_id>/<int:meeting_id>/', views.send, name = 'send'),
    path('get_messages/<int:club_id>/<int:meeting_id>/', views.get_messages, name = 'get_messages'),
    path('end_meeting/<int:club_id>/<int:meeting_id>/', views.end_meeting, name = 'end_meeting')
]
