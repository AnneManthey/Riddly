from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import CalendarSettings, Door, UserDoorProgress
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .middleware import REMEMBER_ME_SESSION_AGE, REMEMBER_ME_SESSION_KEY


def login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            if request.POST.get("remember_me"):
                request.session[REMEMBER_ME_SESSION_KEY] = True
                request.session.set_expiry(REMEMBER_ME_SESSION_AGE)
            else:
                # Without opt-in, discard the session cookie when the browser closes.
                request.session.set_expiry(0)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    remember_me_checked = (
        request.method != "POST" or "remember_me" in request.POST
    )
    return render(
        request,
        'login.html',
        {"form": form, "remember_me_checked": remember_me_checked},
    )


def _get_user_door_progress(user):
    door_ids = set(Door.objects.values_list('id', flat=True))
    existing_door_ids = set(
        UserDoorProgress.objects.filter(user=user).values_list('door_id', flat=True)
    )
    # Ignore conflicts so parallel requests can safely initialize the same progress rows.
    UserDoorProgress.objects.bulk_create(
        [
            UserDoorProgress(user=user, door_id=door_id)
            for door_id in door_ids - existing_door_ids
        ],
        ignore_conflicts=True,
    )
    return UserDoorProgress.objects.filter(user=user).select_related('door')


def _door_is_accessible(door, progress, date_restrictions_enabled, today=None):
    # Solved doors stay accessible even when date restrictions are enabled.
    if progress.solved or not date_restrictions_enabled:
        return True

    today = today or timezone.localdate()
    return today.year >= 2026 and today.month == 12 and today.day >= door.number


@login_required(login_url="login")
def dashboard(request):
    calendar_settings, _ = CalendarSettings.objects.get_or_create(pk=1)
    progress_records = _get_user_door_progress(request.user)
    doors = [
        {
            'door': progress.door,
            'progress': progress,
            'is_accessible': _door_is_accessible(
                progress.door,
                progress,
                calendar_settings.date_restrictions_enabled,
            ),
        }
        for progress in progress_records
    ]
    return render(request, 'dashboard.html', {'doors': doors})

@login_required(login_url="login")
def riddle(request, slug):
    door = get_object_or_404(Door, slug=slug)
    progress, _ = UserDoorProgress.objects.get_or_create(
        user=request.user,
        door=door,
    )
    calendar_settings, _ = CalendarSettings.objects.get_or_create(pk=1)
    if not _door_is_accessible(
        door,
        progress,
        calendar_settings.date_restrictions_enabled,
    ):
        messages.info(request, "Diese Tür ist noch gesperrt.")
        return redirect("dashboard")

    if request.method == "POST" and not progress.solved:
        answer = request.POST.get("answer", "").strip().lower()
        progress.attempts += 1
        # Accept the solution phrase anywhere in the normalized response.
        if answer and door.solution.strip().lower() in answer:
            progress.solved = True
            progress.solved_at = timezone.now()
            progress.save()
            messages.success(request, "Yay!.")
            return redirect("riddle", slug=slug)
        progress.save()
        messages.error(request, "Nicht ganz. Nächster Versuch!")
        return redirect("riddle", slug=slug)
    return render(request, 'riddle.html', {'door': door, 'progress': progress})


def logout(request):
    if request.method == "POST":
        auth_logout(request)
    return redirect("login")

def imprint(request):
    return render(request, 'impressum.html')