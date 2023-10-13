from django.contrib import admin
from book_clubs.models import User, Club, Membership, Application, Book, Rating, Meeting, MeetingRecommendation, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'username', 'email', 'first_name', 'last_name', 'location', 'age', 'is_active'
    ]

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'meeting_cycle'
    ]

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'club', 'member', 'member_type'
    ]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'club', 'applicant'
    ]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'isbn', 'name', 'author', 'year_of_publication', 'publisher'
    ]

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'book', 'rating'
    ]

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'club', 'book_chooser', 'active', 'deadline'
    ]

@admin.register(MeetingRecommendation)
class MeetingRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'meeting', 'book'
    ]

@admin.register(Message)
class Message(admin.ModelAdmin):
    list_display = [
        'id', 'meeting', 'name_of_user', 'value', 'post_time'
    ]
