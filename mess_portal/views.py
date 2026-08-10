from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
import pandas as pd
import urllib.request
import time
from  django.core.cache import cache
import os

GOOGLE_SHEET_URL = ('https://docs.google.com/spreadsheets/d/'
                    '19orUPC3WDjW31AUQeZbcB6n-6g8f02HtL7MhMF0Qpq8/export?format=xlsx')

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
SECTIONS = ['BREAKFAST', 'LUNCH', 'Tea Time', 'DINNER']

LEADERSHIP = [
    {
        'name': 'Director, IIT Bhilai',
        'role': 'Official Message',
        'quote': '',
        'photo': 'images/director.jpg',
    },

    {
        'name': 'Dean of Student Affairs,IIT Bhilai',
        'role': 'Dean of Student Affairs',
        'quote': '',
        'photo': 'images/Dosa.jpg',
    },
    {
            'name': 'Faculty In-Charge (FIC), Mess',
            'role': 'Faculty In-Charge',
            'quote': "",
            'photo': 'images/fic.jpg',
    },
    {
        'name': 'Mess Coordinator,IIT Bhilai',
        'role': 'Manish Kumar Yadav ',
        'quote': '',
        'photo': 'images/Coordinator.jpg',
    },
]

COMMITTEE = [
    {'name': 'Student Representative', 'role': 'Mess Coordinator', 'email': 'messcoordinator@iitbhilai.ac.in', 'photo': 'images/member1.jpg'},
    {'name': 'Menu Coordinator', 'role': 'Weekly Menu & Planning', 'email': 'messcoordinator@iitbhilai.ac.in', 'photo': 'images/member2.jpg'},
    {'name': 'Feedback In-Charge', 'role': 'Complaints & Suggestions', 'email': 'ficmess@iitbhilai.ac.in', 'photo': 'images/member3.jpg'},
]

NOTICES = [
    {
        'title': 'Mess Card is Mandatory at Every Meal',
        'date': 'Important',
        'category': 'Rules',
        'text': 'All students must carry their mess card while entering the dining hall. Entry without a mess card will be denied.',
        'color': '#d4183d',
    },
    {
        'title': 'Meal Timings — Strictly Enforced',
        'date': 'Important',
        'category': 'Timings',
        'text': 'Breakfast 8:00–10:00 AM • Lunch 12:00–2:00 PM • Snacks 5:00–6:00 PM • Dinner 7:00–9:00 PM. No service outside these hours.',
        'color': '#2541b2',
    },
    {
        'title': 'Hygiene Rules — Wash Hands Before Serving',
        'date': 'Reminder',
        'category': 'Hygiene',
        'text': 'Hand sanitizer and wash basins are available at both entrances. Do not touch food directly while serving yourself.',
        'color': '#10b981',
    },
    {
        'title': 'No Food or Utensils to Be Taken Out',
        'date': 'Reminder',
        'category': 'Rules',
        'text': 'Food, plates and cutlery must not be removed from the mess hall. Violators will be reported to the mess committee.',
        'color': '#45347d',
    },
    {
        'title': 'Guests Allowed Only on Weekends',
        'date': 'Notice',
        'category': 'Guests',
        'text': 'Students may bring a maximum of one guest on Saturday or Sunday lunch. Guest coupons must be purchased at the mess office in advance.',
        'color': '#d97706',
    },
    {
        'title': 'Feedback & Complaints — Weekly Review',
        'date': 'Notice',
        'category': 'Feedback',
        'text': 'Submit complaints through the committee members or the feedback box near the exit. Every complaint is reviewed every Friday.',
        'color': '#8e7db4',
    },
]


MENU_CACHE_KEY = 'mess_menu_weeks'
MENU_HASH_KEY = 'mess_menu_hash'
MENU_CHECK_KEY = 'mess_menu_last_check'
MENU_CHECK_INTERVAL = 1200 # 20 min  between Google Sheet examination
MENU_CACHE_TTL = 86400  # 24h 

def _file_hash(excel_path):
    """SHA-256 of the downloaded sheet, used to detect real content changes."""
    import hashlib
    try:
        with open(excel_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def _get_cached_menu():
    """Serve the menu from Redis unless the Google Sheet actually changed.

    Strategy:
    - between probes (30s) -> render straight from Redis, no download at all
    - at each probe -> download the sheet, hash it, and compare with the hash
      of the last parsed file; only if it differs do we re-parse and refresh
      the cache. Sheet edits therefore appear within ~30 seconds."""
    weeks = cache.get(MENU_CACHE_KEY)
    last_check = cache.get(MENU_CHECK_KEY)
    now = time.time()
    if weeks is not None and last_check is not None and now - last_check < MENU_CHECK_INTERVAL:
        return weeks, None
    excel_path = os.path.join(settings.BASE_DIR, 'mess_menu.xlsx')
    _refresh_file()  # refreshes the local copy; silently fails offline
    file_hash = _file_hash(excel_path)
    if weeks is not None and file_hash == cache.get(MENU_HASH_KEY):
        cache.set(MENU_CHECK_KEY, now, MENU_CACHE_TTL)
        return weeks, None
    weeks, error = _parse_menu()
    if weeks and file_hash:
        cache.set(MENU_CACHE_KEY, weeks, MENU_CACHE_TTL)
        cache.set(MENU_HASH_KEY, file_hash, MENU_CACHE_TTL)
    cache.set(MENU_CHECK_KEY, now, MENU_CACHE_TTL)
    return weeks, error


def _refresh_file():
    excel_path = os.path.join(settings.BASE_DIR, 'mess_menu.xlsx')
    try:
        urllib.request.urlretrieve(GOOGLE_SHEET_URL, excel_path)
    except Exception:
        pass
    return os.path.exists(excel_path)


def _parse_menu():
    """Always read the menu live from the Google Sheet.
    Falls back to the last cached xlsx if the download fails."""
    if _refresh_file():
        return _parse_menu_xlsx()
    excel_path = os.path.join(settings.BASE_DIR, 'mess_menu.xlsx')
    if os.path.exists(excel_path):
        return _parse_menu_xlsx()
    return None, 'Could not download the menu. Check your internet connection and that the Google Sheet link is public.'


def _parse_menu_xlsx():
    excel_path = os.path.join(settings.BASE_DIR, 'mess_menu.xlsx')
    if not os.path.exists(excel_path):
        return None, 'Could not download the menu. Check your internet connection and that the Google Sheet link is public.'

    try:
        weeks = []
        for sheet in ['1&3 Week', '2&4']:
            df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
            sections = []
            current = None
            for _, row in df.iterrows():
                label = row[0]
                if pd.isna(label):
                    continue
                label = str(label).strip()
                if label in SECTIONS:
                    current = {'name': label, 'rows': []}
                    sections.append(current)
                    continue
                if label == 'Meal / Category' or current is None:
                    continue
                items = []
                for day in range(1, 8):
                    val = row[day]
                    if pd.notna(val):
                        items.append(str(val).replace('\n', ' ').replace('"', '').strip())
                    else:
                        items.append('')
                current['rows'].append({'category': label, 'items': items})
            weeks.append({
                'label': 'Week 1 & 3' if sheet == '1&3 Week' else 'Week 2 & 4',
                'sections': sections,
            })
        return weeks, None
    except Exception as exc:
        return None, 'Could not read mess_menu.xlsx: {}'.format(exc)


def _day_view(week, day_index):
    return [{
        'name': section['name'],
        'rows': [{'category': r['category'], 'item': r['items'][day_index]} for r in section['rows']],
    } for section in week['sections']]


def _today_day():
    return timezone.now().strftime('%A')


def _announcements():
    from .models import Announcement
    return list(Announcement.objects.filter(active=True))


def _notices():
    from .models import Notice
    qs = Notice.objects.filter(active=True)
    if qs.exists():
        return list(qs)
    return NOTICES


def home(request):
    weeks, error = _get_cached_menu()
    today = _today_day()
    day_index = DAYS.index(today) if today in DAYS else 0
    today_sections = _day_view(weeks[0], day_index) if weeks else []
    return render(request, 'home.html', {
        'leadership': LEADERSHIP,
        'notices': _notices(),
        'announcements': _announcements(),
        'weeks': weeks,
        'menu_error': error,
        'today': today,
        'today_sections': today_sections,
    })


def menu(request):
    weeks, error = _get_cached_menu()
    days_data = None
    if weeks:
        days_data = [
            {'day': day, 'sections': _day_view(weeks[0], i)}
            for i, day in enumerate(DAYS)
        ]
    return render(request, 'menu.html', {
        'days_data': days_data,
        'menu_error': error,
        'today': _today_day(),
    })


def menu_sheet(request):
    weeks, error = _get_cached_menu()
    return render(request, 'menu_sheet.html', {
        'weeks': weeks,
        'menu_error': error,
        'days': DAYS,
    })


def committee(request):
    return render(request, 'committee.html', {'committee': COMMITTEE})


def contact(request):
    return render(request, 'contact.html')

def complaints(request):
    return render(request, 'complaints.html')