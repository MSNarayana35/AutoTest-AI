"""
Timezone utilities for Indian Standard Time (IST)
"""
from datetime import datetime
import pytz

# Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now() -> datetime:
    """Get current time in IST"""
    return datetime.now(IST)

def utc_to_ist(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to IST"""
    if utc_dt.tzinfo is None:
        # Assume UTC if no timezone
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(IST)

def format_ist_datetime(dt: datetime) -> str:
    """Format datetime in IST with Indian format (DD/MM/YYYY HH:MM:SS)"""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    ist_dt = dt.astimezone(IST)
    return ist_dt.strftime('%d/%m/%Y %I:%M:%S %p IST')

def format_ist_date(dt: datetime) -> str:
    """Format date in IST with Indian format (DD/MM/YYYY)"""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    ist_dt = dt.astimezone(IST)
    return ist_dt.strftime('%d/%m/%Y')

def format_ist_time(dt: datetime) -> str:
    """Format time in IST (HH:MM:SS AM/PM)"""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    ist_dt = dt.astimezone(IST)
    return ist_dt.strftime('%I:%M:%S %p')
