from datetime import datetime
from django.utils import timezone
from .models import OpeningHour


def is_open_now(vendor):
    """
    Returns True if the vendor is currently open.
    Day: Monday=1 ... Sunday=7 (matches DAYS choices in models.py)
    Times stored as "09:00 AM" / "10:00 PM" format.
    """
    # ✅ FIXED: use timezone.localtime() instead of datetime.now()
    # so it respects IST instead of UTC (fixes Render server timezone issue)
    now = timezone.localtime(timezone.now())
    today = now.weekday() + 1  # Python Mon=0 → your Mon=1

    hours_today = OpeningHour.objects.filter(vendor=vendor, day=today)

    if not hours_today.exists():
        return False

    for slot in hours_today:
        if slot.is_closed:
            return False
        try:
            open_dt  = datetime.strptime(slot.from_hour.strip(), '%I:%M %p')
            close_dt = datetime.strptime(slot.to_hour.strip(),   '%I:%M %p')
            # ✅ FIXED: compare using hour+minute only, not current_time_str
            # This avoids exact minute mismatch (e.g. 09:23 AM not in choices)
            now_dt   = datetime.strptime(now.strftime('%I:%M %p'), '%I:%M %p')
            if open_dt <= now_dt <= close_dt:
                return True
        except ValueError:
            continue

    return False


def get_vendor_hours_context(vendor):
    now = timezone.localtime(timezone.now())
    today = now.weekday() + 1

    DAY_NAMES = {
        1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday',
        5: 'Friday',  6: 'Saturday', 7: 'Sunday',
    }

    all_slots = OpeningHour.objects.filter(vendor=vendor).order_by('day', 'from_hour')

    today_slot = None
    for slot in all_slots:
        if slot.day == today and not slot.is_closed:
            today_slot = slot
            break

    all_hours = []
    seen_days = set()
    for slot in all_slots:
        day_name = DAY_NAMES.get(slot.day, '')
        if slot.day not in seen_days:
            seen_days.add(slot.day)
            all_hours.append({
                'day_name' : day_name,
                'from_hour': slot.from_hour,
                'to_hour'  : slot.to_hour,
                'is_closed': slot.is_closed,
            })

    return {
        'today_slot': today_slot,
        'all_hours' : all_hours,
        'is_open'   : is_open_now(vendor),
    }