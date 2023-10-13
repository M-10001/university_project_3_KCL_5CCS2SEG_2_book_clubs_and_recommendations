from django.shortcuts import redirect, render
from django.contrib import messages as msgs
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from .forms import LogInForm, ClubCreationForm, SignUpForm, ConfirmationForm, SearchBooksForm, MeetingCreationForm
from django.contrib.auth.decorators import login_required
from .models import User, Club, Membership, Application, Book, Meeting, MeetingRecommendation, Message
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views.generic.list import ListView
from book_clubs import helpers
from django.utils import timezone

@helpers.login_prohibited
def home(request):
    return render(request, 'home.html')

@helpers.login_prohibited
def sign_up(request):
    if request.method == 'POST':
        sign_up_form = SignUpForm(request.POST)
        if sign_up_form.is_valid():
            user = sign_up_form.save()
            login(request, user)
            return redirect('user_page')
    else:
        sign_up_form = SignUpForm()
    return render(request, 'sign_up.html', {'sign_up_form' : sign_up_form})

@helpers.login_prohibited
def log_in(request):
    next_url = ''

    if request.method == 'POST':
        next_url = request.POST.get('next') or 'user_page'
        log_in_form = LogInForm(request.POST)

        if log_in_form.is_valid():
            username = log_in_form.cleaned_data.get('username')
            password = log_in_form.cleaned_data.get('password')
            user = authenticate(username = username, password = password)

            if user is not None:
                login(request, user)
                return redirect(next_url)

        msgs.add_message(request, msgs.ERROR, "The credentials provided were invalid!")
    else:
        next_url = request.GET.get('next') or ''

    log_in_form = LogInForm()
    return render(request, 'log_in.html', {'log_in_form' : log_in_form, 'next' : next_url})

@login_required
def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def user_page(request):
    return render(request, 'user_page.html')

@login_required
def create_club(request):
    if request.method == 'POST':
        club_form = ClubCreationForm(data = request.POST)

        if club_form.is_valid():
            club = club_form.save()
            Membership.objects.create(club = club, member = request.user, member_type = Membership.MemberTypes.OWNER)
            msgs.add_message(request, msgs.SUCCESS, "Created club!")
            return redirect(reverse('club_page', kwargs = {'club_id' : club.id}))
    else:
        club_form = ClubCreationForm()

    return render(request, 'create_club.html', {'club_form' : club_form})

@login_required
def user_club_list(request):
    clubs = request.user.memberships.all()
    return render(request, 'user_club_list.html', {'clubs' : clubs})

@login_required
def applicable_clubs(request):
    clubs = Club.objects.exclude(members = request.user)
    clubs = clubs.exclude(applicants = request.user)
    return render(request, 'applicable_clubs.html', {'clubs' : clubs})

@login_required
def apply_to_club(request, club_id):
    try:
        club = Club.objects.get(id = club_id)
    except Club.DoesNotExist:
        return redirect('applicable_clubs')

    try:
        Membership.objects.get(club = club, member = request.user)
        return redirect('applicable_clubs')
    except Membership.DoesNotExist:
            try:
                Application.objects.get(club = club, applicant = request.user)
                return redirect('applicable_clubs')
            except Application.DoesNotExist:
                Application.objects.create(
                    club = club,
                    applicant = request.user
                )
                msgs.add_message(request, msgs.SUCCESS, "Applied to club!")
                return redirect('applicable_clubs')

@login_required
def user_application_list(request):
    applications = Application.objects.filter(applicant = request.user)
    return render(request, 'user_application_list.html', {'applications' : applications})

@login_required
@helpers.club_requirements
def club_page(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    owner_memberships = Membership.objects.filter(club = club, member_type = Membership.MemberTypes.OWNER)
    meetings_to_choose_books_for = Meeting.objects.filter(club = club, book_chooser = request.user, chosen_book = None, active = True)
    return render(
        request,
        'club_page.html',
        {
            'membership' : membership,
            'club' : club,
            'owner_memberships' : owner_memberships,
            'meetings_to_choose_books_for' : meetings_to_choose_books_for
        }
    )

@login_required
@helpers.club_requirements
def club_edit(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)

    if (membership.is_owner()):
        if request.method == 'POST':
            club_form = ClubCreationForm(instance = club, data = request.POST)
            if club_form.is_valid():
                club = club_form.save()
                msgs.add_message(request, msgs.SUCCESS, "Edited club!")
                return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))
        else:
            club_form = ClubCreationForm(instance = club)
        return render(request, 'club_edit.html', {'membership' : membership, 'club_form' : club_form, 'club' : club})
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.club_requirements
def disband_club(request, club_id):
    def to_bool(str):
        return True if str == 'True' else False

    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)

    if not membership.is_owner():
        return redirect(reverse('club_page', kwargs = {'club_id': club_id}))

    if (request.method == 'POST'):
        confirmation_form = ConfirmationForm(request.POST)

        if confirmation_form.is_valid():
            disband = to_bool(confirmation_form.cleaned_data.get('confirmation'))

            if disband:
                club.delete()
                msgs.add_message(request, msgs.SUCCESS, "Club disbanded.")
                return redirect(reverse('user_club_list'))
            else:
                return redirect(reverse('club_page', kwargs = {'club_id': club_id}))
    else:
        confirmation_form = ConfirmationForm()

    return render(request, 'disband_club.html', {'membership': membership, 'confirmation_form': confirmation_form})

@login_required
@helpers.club_requirements
def club_application_list(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)

    if not membership.is_owner():
        return redirect (reverse('club_page', kwargs = {'club_id' : club_id}))

    applications = Application.objects.filter(club = club)
    return render(request, 'club_application_list.html', {'membership' : membership, 'applications' : applications})

@login_required
@helpers.applicant_and_club_requirements
def accept_application(request, user_id, club_id):
    club = Club.objects.get(id = club_id)
    if Membership.objects.get(club = club, member = request.user).member_type == Membership.MemberTypes.OWNER:
        applicant_to_accept = User.objects.get(id = user_id)
        Application.objects.get(club = club, applicant = applicant_to_accept).delete()
        Membership.objects.create(club = club, member = applicant_to_accept, member_type = Membership.MemberTypes.MEMBER)
        msgs.add_message(request, msgs.SUCCESS, "Accepted new member!")
        return redirect(reverse('club_application_list', kwargs = {'club_id' : club_id}))
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.applicant_and_club_requirements
def reject_application(request, user_id, club_id):
    club = Club.objects.get(id = club_id)
    if Membership.objects.get(club = club, member = request.user).member_type == Membership.MemberTypes.OWNER:
        applicant_to_reject = User.objects.get(id = user_id)
        Application.objects.get(club = club, applicant = applicant_to_reject).delete()
        msgs.add_message(request, msgs.SUCCESS, "Rejected applicant!")
        return redirect(reverse('club_application_list', kwargs = {'club_id' : club_id}))
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.club_requirements
def member_list(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    membership_list = Membership.objects.filter(club = club)
    return render(request, 'member_list.html', {'membership' : membership, 'membership_list' : membership_list})

@login_required
@helpers.member_and_club_requirements
def kick_member(request, user_id, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    member = User.objects.get(id = user_id)
    member_membership = Membership.objects.get(club = club, member = member)

    if ((not membership.is_owner()) or member_membership.is_owner()):
        return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))

    if request.method == 'POST':
        kick_member_form = ConfirmationForm(request.POST)

        if kick_member_form.is_valid():
            confirmation = kick_member_form.cleaned_data.get('confirmation')

            if (confirmation == 'True'):
                member_membership.delete()

                if (club.meeting_cycle_limit_passed()):
                    club.meeting_cycle = CLUB.MEETING_CYCLE_DEFAULT
                    club.save()

                msgs.add_message(request, msgs.SUCCESS, "Kicked member!")

            return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))
    else:
        kick_member_form = ConfirmationForm()

    return render(request, 'kick_member.html', {'membership' : membership, 'member_membership' : member_membership, 'kick_member_form' : kick_member_form})

@login_required
@helpers.club_requirements
def shedule_meeting(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)

    if not membership.is_owner():
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

    if (request.method == 'POST'):
        meeting_creation_form = MeetingCreationForm(request.POST)

        if meeting_creation_form.is_valid():
            deadline = meeting_creation_form.cleaned_data.get('deadline')
            members = club.members.all()
            chooser = members[club.meeting_cycle]
            club.meeting_cycle = club.meeting_cycle + 1

            if club.meeting_cycle_limit_passed():
                club.meeting_cycle = Club.MEETING_CYCLE_DEFAULT

            club.save()
            meeting = Meeting.objects.create(club = club, book_chooser = chooser, active = True, deadline = deadline)
            recommendations = helpers.get_recommendations_for_club(club_id, 8)

            for recommendation in recommendations:
                MeetingRecommendation.objects.create(meeting = meeting, book = Book.objects.get(isbn = recommendation))

            msgs.add_message(request, msgs.SUCCESS, "Created meeting!")
            return redirect(reverse('meeting_list', kwargs = {'club_id' : club_id}))
    else:
        meeting_creation_form = MeetingCreationForm()

    return render(request, 'shedule_meeting.html', {'membership' : membership, 'meeting_creation_form' : meeting_creation_form})

@login_required
@helpers.club_and_meeting_requirements_for_book_chooser
def meeting_book_selection(request, club_id, meeting_id, page):
    current_user = request.user
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = current_user)
    meeting = Meeting.objects.get(id = meeting_id)
    recommended_books = meeting.recommendations.all()
    all_books_info = []

    if (request.method == 'POST'):
        search_books_form = SearchBooksForm(request.POST)

        if search_books_form.is_valid():
            isbn = search_books_form.cleaned_data.get('isbn')
            name = search_books_form.cleaned_data.get('name')
            author = search_books_form.cleaned_data.get('author')
            year_of_publication = search_books_form.cleaned_data.get('year_of_publication')
            publisher = search_books_form.cleaned_data.get('publisher')

            if (isbn or name or (year_of_publication != None) or publisher):
                search_books = Book.objects.all()

                if isbn:
                    search_books.filter(isbn__icontains = isbn)
                if name:
                    search_books = search_books.filter(name__icontains = name)
                if author:
                    search_books = search_books.filter(author__icontains = author)
                if (year_of_publication != None):
                    search_books = search_books.filter(year_of_publication = year_of_publication)
                if publisher:
                    search_books = search_books.filter(publisher__icontains = publisher)

                page = 0
                all_books_info = list(search_books.values_list('isbn', 'name'))
                search_books = None

    last_page = 0
    next_page = 0
    previous_page = 0
    books_info = []

    if not all_books_info:
        all_books_info = list(Book.objects.all().values_list('isbn', 'name'))
        last_page = int(len(all_books_info) / 50)

        if ((page > last_page) or (page < 0)):
            page = 0

        books_info = all_books_info[50 * page : (50 * (page + 1))]
        next_page = page + 1

        if (next_page > last_page):
            next_page = 0

        previous_page = page - 1

        if (previous_page < 0):
            previous_page = 0
    else:
        books_info = all_books_info

    search_books_form = SearchBooksForm()

    return render(
        request,
        'meeting_book_selection.html',
        {
            'membership' : membership,
            'meeting' : meeting,
            'books_info' : books_info,
            'recommended_books' : recommended_books,
            'page' : page,
            'next_page' : next_page,
            'previous_page' : previous_page,
            'last_page' : last_page,
            'search_books_form' : search_books_form
        }
    )

@login_required
def select_meeting_book(request, club_id, meeting_id, book_isbn):
    club = Club.objects.filter(id = club_id).first()
    membership = Membership.objects.filter(club = club, member = request.user).first()
    meeting = Meeting.objects.filter(id = meeting_id).first()
    book = Book.objects.filter(isbn = book_isbn).first()

    if ((not club) or (not membership)):
        return redirect(reverse('user_club_list'))
    if ((not meeting) or (meeting.club != club) or (meeting.book_chooser != request.user) or (not meeting.active) or meeting.chosen_book):
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))
    if not book:
        return redirect(reverse('meeting_book_selection', kwargs = {'club_id' : club_id, 'meeting_id' : meeting_id, 'page' : 0}))

    meeting.chosen_book = book
    meeting.save()
    msgs.add_message(request, msgs.SUCCESS, "Book has been selected!")
    return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.club_requirements
def meeting_list(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    meetings = Meeting.objects.filter(club = club, active = True)
    return render(request, 'meeting_list.html', {'membership' : membership, 'meetings' : meetings})

@login_required
@helpers.club_and_join_meeting_requirements
def meeting(request, club_id, meeting_id):
    current_user = request.user
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = current_user)
    meeting = Meeting.objects.get(id = meeting_id)
    return render(request, 'meeting.html', {'membership' : membership, 'meeting' : meeting, 'club_id' : club_id, 'meeting_id' : meeting_id})

@login_required
@helpers.club_and_join_meeting_requirements
def send(request, club_id, meeting_id):
    username = request.POST['username']
    message = request.POST['message']
    if message:
        new_message = Message.objects.create(
            value = message,
            name_of_user = username,
            meeting = Meeting.objects.get(id = meeting_id)
        )

@login_required
@helpers.club_and_join_meeting_requirements
def get_messages(request, club_id, meeting_id):
    club = Club.objects.get(id = club_id)
    meeting = Meeting.objects.get(id = meeting_id, club = club)
    messages = Message.objects.filter(meeting = meeting)
    messages_values = list(messages.values())

    for i in range(len(messages_values)):
        messages_values[i]['post_time'] = messages[i].post_time_visual_output()

    return JsonResponse({'messages' : messages_values})

@login_required
def end_meeting(request, club_id, meeting_id):
    club = Club.objects.filter(id = club_id).first()
    membership = Membership.objects.filter(club = club, member = request.user).first()
    meeting = Meeting.objects.filter(id = meeting_id, active = True).first()

    if ((not club) or (not membership)):
        return redirect(reverse('user_club_list'))

    if ((not membership.is_owner()) or (not meeting) or (meeting.club != club)):
        return redirect(reverse('meeting_list', kwargs = {'club_id' : club_id}))

    meeting.active = False
    meeting.save()
    msgs.add_message(request, msgs.SUCCESS, 'Ended meeting!')
    return redirect(reverse('meeting_list', kwargs = {'club_id' : club_id}))
