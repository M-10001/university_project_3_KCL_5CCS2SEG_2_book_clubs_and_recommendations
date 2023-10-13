import random
from surprise import dump
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages as msgs
from .models import User, Club, Membership, Application, Book, Meeting

def _membership_check(request, club_id):
    """Checks if current user is part of club with id being club_id."""
    try:
        club = Club.objects.get(id = club_id)
        membership = Membership.objects.get(club = club, member = request.user)
    except ObjectDoesNotExist:
        return False
    else:
        return True

def _meeting_check(club, meeting_id):
    """Checks if meeting of meeting_id is part of club."""
    try:
        Meeting.objects.get(id = meeting_id, club = club)
    except ObjectDoesNotExist:
        return False
    else:
        return True

def _get_anti_test_set_for_user(train_set, test_subject):
    """Gets anti test set of ratings for user."""
    fill = train_set.global_mean
    anti_testset = []
    u = train_set.to_inner_uid(test_subject)
    user_items = set([j for (j, _) in train_set.ur[u]])
    anti_testset += [(train_set.to_raw_uid(u), train_set.to_raw_iid(i), fill) for
                             i in train_set.all_items() if
                             i not in user_items]

    return anti_testset

def login_prohibited(function):
    """Redirects to user_page view if current user is logged in."""
    def wrapper(request):
        if request.user.is_authenticated:
            return redirect('user_page')
        else:
            return function(request)

    return wrapper

def club_requirements(function):
    """
        Used to check if current user accessing club
        information with club_id is a member of that club.
        Redirects to appropriate views depending on the checks.
    """
    def wrapper(request, club_id):
        if _membership_check(request, club_id):
            return function(request, club_id)
        else:
            return redirect('user_club_list')

    return wrapper

def member_and_club_requirements(function):
    """
        Used to check if current user accessing club
        information with club_id is a member of that club, and
        the user with user_id is a member of that club as well.
        Redirects to appropriate views depending on the checks.
    """
    def wrapper(request, user_id, club_id):
        if _membership_check(request, club_id):
            try:
                club = Club.objects.get(id = club_id)
                member = User.objects.get(id = user_id)
                member_membership = Membership.objects.get(club = club, member = member)
            except ObjectDoesNotExist:
                return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))
            else:
                return function(request, user_id, club_id)
        else:
            return redirect('user_club_list')

    return wrapper

def applicant_and_club_requirements(function):
    """
        Used to check if current user accessing club
        information with club_id is an applicant of that club, and
        the user with user_id is an applicant of that club as well.
        Redirects to appropriate views depending on the checks.
    """
    def wrapper(request, user_id, club_id):
        if _membership_check(request, club_id):
            try:
                club = Club.objects.get(id = club_id)
                applicant = User.objects.get(id = user_id)
                applicant_application = Application.objects.get(club = club, applicant = applicant)
            except ObjectDoesNotExist:
                return redirect(reverse('club_application_list', kwargs = {'club_id' : club_id}))
            else:
                return function(request, user_id, club_id)
        else:
            return redirect('user_club_list')

    return wrapper

def club_and_meeting_requirements_for_book_chooser(function):
    """
        Used to check if current user accessing club
        information with club_id is a member of that club, and
        also whether the meeting with meeting_id
        is part of that club, and current user is a book_chooser of that meeting.
        Also checks if that meeting is active, and no book is chosen for it.
        Redirects to appropriate views depending on the checks.
    """
    def wrapper(request, club_id, meeting_id, page):
        if _membership_check(request, club_id):
            club = Club.objects.get(id = club_id)

            if _meeting_check(club, meeting_id):
                try:
                    meeting = Meeting.objects.get(id = meeting_id, book_chooser = request.user, chosen_book = None, active = True)
                except ObjectDoesNotExist:
                    pass
                else:
                    return function(request, club_id, meeting_id, page)

            return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))
        else:
            return redirect(reverse('user_club_list'))

    return wrapper

def club_and_join_meeting_requirements(function):
    """
        Used to check if current user accessing club
        information with club_id is a member of that club, and
        also whether the meeting with meeting_id is part of that club.
        Also checks if that meeting is active,
        has passed deadline, and has a chosen_book.
        Redirects to appropriate views depending on the checks.
    """
    def wrapper(request, club_id, meeting_id):
        if _membership_check(request, club_id):
            club = Club.objects.get(id = club_id)

            if _meeting_check(club, meeting_id):
                meeting = Meeting.objects.get(id = meeting_id)

                if (meeting.passed_deadline() and (meeting.chosen_book != None)):
                    if meeting.active:
                        return function(request, club_id, meeting_id)
                    else:
                        msgs.add_message(request, msgs.INFO, "The meeting has ended.")

            return redirect(reverse('meeting_list', kwargs = {'club_id' : club_id}))
        else:
            return redirect(reverse('user_club_list'))

    return wrapper

def get_recommendations_for_club(club_id, recommendations_limit):
    """
        Used to retrieve recommendations for a club for book selection.
        It outputs a list of book_isbns.
        Each book is based on a single member's prefernce, so each member's
        top predictions are used instead of the average of each book.
        Books that are already used in a meeting are not recommended again.
        Returns None if total members in a club are zero or below.
    """
    try:
        (predictions, algo) = dump.load('book_clubs/recommender_algorithm')
    except:
        return None

    recommendations = []
    club = Club.objects.get(id = club_id)
    all_member_ids = list(club.members.all().values_list('id', flat = True))
    total_members = len(all_member_ids)
    randomizer = 0

    if (total_members > recommendations_limit):
        randomizer = random.randint(0, total_members - 1)
        i = randomizer
    elif(total_members > 0):
        members = total_members
    else:
        return None

    all_recommendations = []

    for member_id in all_member_ids:
        user_recommendations = []

        try:
            test_set = _get_anti_test_set_for_user(algo.trainset, member_id)
            predictions = algo.test(test_set)

            for user_id, book_isbn, actual_rating, estimated_rating, _ in predictions:
                user_recommendations.append((book_isbn, estimated_rating))

            user_recommendations.sort(key=lambda x: x[1], reverse=True)
        except ValueError:
            pass

        all_recommendations.append(user_recommendations)

    all_book_isbns = list(Book.objects.all().values_list('isbn', flat = True))
    used_book_isbns = list(Book.objects.filter(meeting__club = club).values_list('isbn', flat = True))
    i = randomizer
    j = [0] * total_members

    while (len(recommendations) < recommendations_limit):
        checks_passed = False

        while (not checks_passed):
            while (len(all_recommendations[i]) <= j[i]):
                all_recommendations.remove(all_recommendations[i])
                j.pop(i)

                if (len(all_recommendations) <= 0):
                    return recommendations

                if (i >= len(all_recommendations)):
                    i = 0

            checks_passed = True
            book_isbn = all_recommendations[i][j[i]][0]

            if ((book_isbn in used_book_isbns) or (book_isbn in recommendations) or (not (book_isbn in all_book_isbns))):
                j[i] = j[i] + 1
                checks_passed = False

        recommendations.append(all_recommendations[i][j[i]][0])
        i = i + 1

        if (i >= len(all_recommendations)):
            i = 0
            j = [x+1 for x in j]

    return recommendations
