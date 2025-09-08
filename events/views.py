from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event
from .forms import EventForm
from datetime import date, timedelta, datetime
from calendar import monthrange
import calendar
from django.utils.http import urlencode
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@login_required
def calendar_view(request):
    # Pobierz miesiąc i rok z query params lub domyślnie bieżący
    try:
        month = int(request.GET.get('month', None))
        year = int(request.GET.get('year', None))
    except (TypeError, ValueError):
        month = None
        year = None
    today = date.today()
    if not month or not year:
        month = today.month
        year = today.year
    first_day = date(year, month, 1)
    # Oblicz ostatni dzień miesiąca
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    days = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
    # Pobierz wydarzenia z bazy
    events = Event.objects.filter(user=request.user).all()
    events_by_day = {d: [] for d in days}
    for event in events:
        # Wydarzenia niecykliczne
        if not event.is_recurring or event.recurrence_type == 'none' or not event.recurrence_type:
            if event.date in events_by_day:
                events_by_day[event.date].append(event)
        else:
            # Wydarzenia cykliczne roczne lub domyślne
            if event.recurrence_type == 'yearly' or not event.recurrence_type or event.recurrence_type == 'none':
                for d in days:
                    if d.day == event.date.day and d.month == event.date.month:
                        events_by_day[d].append(event)
            else:
                current = event.date
                end = event.recurrence_end or last_day
                while current <= end and current <= last_day:
                    if current >= first_day and current in events_by_day:
                        events_by_day[current].append(event)
                    if event.recurrence_type == 'daily':
                        current += timedelta(days=1)
                    elif event.recurrence_type == 'weekly':
                        current += timedelta(weeks=1)
                    elif event.recurrence_type == 'monthly':
                        year_, month_ = current.year, current.month + 1
                        if month_ > 12:
                            year_ += 1
                            month_ = 1
                        try:
                            current = current.replace(year=year_, month=month_)
                        except ValueError:
                            last_day_of_month = monthrange(year_, month_)[1]
                            current = current.replace(year=year_, month=month_, day=last_day_of_month)
                    else:
                        break
    # Tworzenie tygodni (poniedziałek-niedziela)
    weeks = []
    week = []
    first_weekday = first_day.weekday() # 0=poniedziałek
    for _ in range(first_weekday):
        week.append(None)
    for d in days:
        week.append(d)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)
    # Polskie nazwy miesięcy
    miesiace_pol = [
        '', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
        'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'
    ]
    month_name = miesiace_pol[month]
    # Wylicz poprzedni i następny miesiąc/rok
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    return render(request, 'events/calendar.html', {
        'weeks': weeks,
        'events_by_day': events_by_day,
        'month_name': month_name,
        'month': month,
        'year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': date.today(),
    })

@login_required
def add_event(request, event_date=None):
    is_ajax = request.GET.get('ajax') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            if is_ajax:
                return JsonResponse({'success': True})
            return redirect('calendar')
        else:
            if is_ajax:
                html = render_to_string('events/event_form.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'form_html': html})
    else:
        initial = {'date': event_date} if event_date else {}
        form = EventForm(initial=initial)
        if is_ajax:
            html = render_to_string('events/event_form.html', {'form': form}, request=request)
            return HttpResponse(html)
    # Jeśli nie AJAX, przekieruj do kalendarza
    return redirect('calendar')

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)
    is_ajax = request.GET.get('ajax') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            if is_ajax:
                return JsonResponse({'success': True})
            return redirect('calendar')
        else:
            if is_ajax:
                html = render_to_string('events/event_form.html', {'form': form, 'edit': True}, request=request)
                return JsonResponse({'success': False, 'form_html': html})
    else:
        form = EventForm(instance=event)
        if is_ajax:
            html = render_to_string('events/event_form.html', {'form': form, 'edit': True}, request=request)
            return HttpResponse(html)
    
    # Jeśli nie AJAX, przekieruj do kalendarza
    return redirect('calendar')

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Wydarzenie zostało usunięte.')
        # Obsługa żądania AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
            return JsonResponse({'success': True})
        return redirect('calendar')
    return render(request, 'events/confirm_delete.html', {'event': event})

@login_required
def clear_calendar(request):
    if request.method == 'POST':
        scope = request.POST.get('scope')
        year = int(request.POST.get('year', date.today().year))
        month = int(request.POST.get('month', date.today().month))
        qs = Event.objects.filter(user=request.user)
        if scope == 'month':
            qs = qs.filter(date__year=year, date__month=month)
            msg = f'Wyczyszczono wydarzenia z miesiąca: {month:02d}.{year}'
        elif scope == 'year':
            qs = qs.filter(date__year=year)
            msg = f'Wyczyszczono wydarzenia z roku: {year}'
        else:
            msg = 'Wyczyszczono cały kalendarz!'
        count = qs.count()
        qs.delete()
        messages.success(request, f'{msg} (usunięto {count} wydarzeń)')
    return redirect(reverse('calendar') + f'?month={month}&year={year}')

@login_required
@require_http_methods(["POST"])
def move_event_date(request, event_id):
    """Przenieś wydarzenie na inny dzień (drag & drop). Oczekuje POST new_date=YYYY-MM-DD"""
    event = get_object_or_404(Event, id=event_id, user=request.user)
    new_date_str = request.POST.get('new_date')
    try:
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    except Exception:
        return JsonResponse({'success': False, 'error': 'Nieprawidłowa data'}, status=400)
    event.date = new_date
    event.save(update_fields=['date'])
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["GET"])
def api_events_by_date(request, event_date):
    """API endpoint do pobierania wydarzeń dla konkretnego dnia"""
    try:
        # Konwertuj string daty na obiekt date
        date_obj = datetime.strptime(event_date, '%Y-%m-%d').date()
        
        # Pobierz wszystkie wydarzenia użytkownika
        all_events = Event.objects.filter(user=request.user)
        
        # Filtruj wydarzenia dla konkretnego dnia (włączając cykliczne)
        events_for_day = []
        
        for event in all_events:
            # Wydarzenia niecykliczne
            if not event.is_recurring or event.recurrence_type == 'none' or not event.recurrence_type:
                if event.date == date_obj:
                    events_for_day.append(event)
            else:
                # Wydarzenia cykliczne roczne
                if event.recurrence_type == 'yearly':
                    if date_obj.day == event.date.day and date_obj.month == event.date.month:
                        events_for_day.append(event)
                # Wydarzenia cykliczne dzienne, tygodniowe, miesięczne
                elif event.recurrence_type in ['daily', 'weekly', 'monthly']:
                    current = event.date
                    end = event.recurrence_end or date_obj + timedelta(days=365)  # domyślnie rok do przodu
                    
                    while current <= end:
                        if current == date_obj:
                            events_for_day.append(event)
                            break
                        
                        if event.recurrence_type == 'daily':
                            current += timedelta(days=1)
                        elif event.recurrence_type == 'weekly':
                            current += timedelta(weeks=1)
                        elif event.recurrence_type == 'monthly':
                            year_, month_ = current.year, current.month + 1
                            if month_ > 12:
                                year_ += 1
                                month_ = 1
                            try:
                                current = current.replace(year=year_, month=month_)
                            except ValueError:
                                last_day_of_month = monthrange(year_, month_)[1]
                                current = current.replace(year=year_, month=month_, day=last_day_of_month)
                        else:
                            break
        
        # Przygotuj dane do zwrócenia
        events_data = []
        for event in events_for_day:
            events_data.append({
                'id': event.id,
                'category': event.category,
                'category_display': event.get_category_display(),
                'custom_category': event.custom_category,
                'description': event.description,
                'date': date_obj.strftime('%d.%m.%Y'),
                'icon': event.icon or 'fa-calendar-check',
                'is_recurring': event.is_recurring,
                'recurrence_type': event.recurrence_type,
            })
        
        return JsonResponse({
            'success': True,
            'date': date_obj.strftime('%d.%m.%Y'),
            'events': events_data
        })
        
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Nieprawidłowy format daty'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def api_upcoming(request):
    """Zwraca listę nadchodzących wydarzeń w horyzoncie days (domyślnie 14)."""
    try:
        days_ahead = int(request.GET.get('days', '14'))
        today_ = date.today()
        end_ = today_ + timedelta(days=days_ahead)
        all_events = Event.objects.filter(user=request.user)
        upcoming = []
        for ev in all_events:
            if not ev.is_recurring or ev.recurrence_type in (None, '', 'none'):
                if today_ <= ev.date <= end_:
                    upcoming.append((ev.date, ev))
            else:
                # obsługa recurring: yearly, daily, weekly, monthly w ograniczonym horyzoncie
                current = ev.date
                limit = end_
                # dla yearly – generuj tylko jeśli w horyzoncie > roku? tu: tylko jeśli ten rok w zakresie
                if ev.recurrence_type == 'yearly':
                    for d in (today_ + timedelta(days=i) for i in range((end_ - today_).days + 1)):
                        if d.day == ev.date.day and d.month == ev.date.month:
                            upcoming.append((d, ev))
                    continue
                # dla daily/weekly/monthly – iteruj od startu aż do końca
                end_rec = ev.recurrence_end or limit
                cur = max(current, today_)
                # wyrównaj cur do najbliższego wystąpienia >= today_
                if ev.recurrence_type == 'weekly':
                    delta_days = (cur - ev.date).days
                    if delta_days % 7 != 0:
                        cur = cur + timedelta(days=(7 - (delta_days % 7)))
                while cur <= end_rec and cur <= end_:
                    if cur >= today_:
                        upcoming.append((cur, ev))
                    if ev.recurrence_type == 'daily':
                        cur += timedelta(days=1)
                    elif ev.recurrence_type == 'weekly':
                        cur += timedelta(weeks=1)
                    elif ev.recurrence_type == 'monthly':
                        y, m = cur.year, cur.month + 1
                        if m > 12:
                            y += 1
                            m = 1
                        try:
                            cur = cur.replace(year=y, month=m)
                        except ValueError:
                            last_day_of_month = monthrange(y, m)[1]
                            cur = cur.replace(year=y, month=m, day=last_day_of_month)
                    else:
                        break
        # sortuj i ogranicz do max 50 pozycji
        upcoming.sort(key=lambda x: (x[0], x[1].id))
        result = []
        for d, ev in upcoming[:50]:
            result.append({
                'id': ev.id,
                'date_iso': d.strftime('%Y-%m-%d'),
                'date': d.strftime('%d.%m.%Y'),
                'category': ev.category,
                'category_display': ev.get_category_display(),
                'custom_category': ev.custom_category,
                'description': ev.description,
                'icon': ev.icon or 'fa-calendar-check',
                'is_recurring': ev.is_recurring,
                'recurrence_type': ev.recurrence_type,
            })
        return JsonResponse({'success': True, 'events': result})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
