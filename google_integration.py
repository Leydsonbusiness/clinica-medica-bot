#Integração com google agenda(marcar consultas)  

# =============== MARCAR CONSULTAS =================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, time
from pathlib import Path
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build

# =============== CONFIG =================

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "service_account.json"
TZ = ZoneInfo("America/Fortaleza")
CALENDAR_ID = "leydsonestudos@gmail.com"

CONSULTA_MIN = 50
INTERVALO_MIN = 20
SLOT_MIN = CONSULTA_MIN + INTERVALO_MIN  #70min consulta total

WORK_WINDOWS = [
    (time(8, 0), time(12, 0)),
    (time(14, 0), time(18, 0)),
]

def get_calendar_service():
    """Cria o client do Google Calendar usando service_account.json"""
    base_dir = Path(__file__).resolve().parent
    json_path = base_dir / SERVICE_ACCOUNT_FILE

    creds = service_account.Credentials.from_service_account_file(
        str(json_path),
        scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)


def list_events_in_range(service, start_dt: datetime, end_dt: datetime) -> list:
    """Lista eventos no intervalo."""
    res = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_dt.isoformat(),
        timeMax=end_dt.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    return res.get("items", [])


def get_busy_intervals_for_day(service, day: datetime):
    """Retorna lista de (inicio, fim) ocupados no dia."""
    start_day = day.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=TZ)
    end_day = start_day + timedelta(days=1)

    events = list_events_in_range(service, start_day, end_day)

    busy = []
    for ev in events:
        # ignora eventos de dia inteiro
        if "dateTime" not in ev.get("start", {}) or "dateTime" not in ev.get("end", {}):
            continue

        s = datetime.fromisoformat(ev["start"]["dateTime"])
        e = datetime.fromisoformat(ev["end"]["dateTime"])

        # garante tz
        if s.tzinfo is None:
            s = s.replace(tzinfo=TZ)
        if e.tzinfo is None:
            e = e.replace(tzinfo=TZ)

        busy.append((s, e))
    return busy


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """Colisão entre intervalos [a_start,a_end) e [b_start,b_end)."""
    return a_start < b_end and b_start < a_end


def generate_slots_for_day(day: datetime):
    """Gera slots fixos do dia com tamanho de 70min (50+20)."""
    slots = []
    for w_start, w_end in WORK_WINDOWS:
        cur = datetime.combine(day.date(), w_start, tzinfo=TZ)
        end_window = datetime.combine(day.date(), w_end, tzinfo=TZ)

        while cur + timedelta(minutes=SLOT_MIN) <= end_window:
            slots.append(cur)  # só o start do slot
            cur += timedelta(minutes=SLOT_MIN)

    return slots


def get_free_slots_for_date(date_yyyy_mm_dd: str):
    """
    Retorna uma lista de horários livres (start datetime) para a data informada.
    Ex: "2026-01-25"
    """
    service = get_calendar_service()
    day = datetime.fromisoformat(date_yyyy_mm_dd).replace(tzinfo=TZ)

    busy = get_busy_intervals_for_day(service, day)
    slots = generate_slots_for_day(day)

    free = []
    for start in slots:
        end = start + timedelta(minutes=SLOT_MIN)  # checa o slot completo (70)
        conflict = any(overlaps(start, end, b_start, b_end) for (b_start, b_end) in busy)
        if not conflict:
            free.append(start)

    return free


def create_appointment(date_yyyy_mm_dd: str, hh_mm: str, patient_name: str, patient_telefone: str | None = None):
    """
    Cria evento de consulta (50min) no Calendar.
    """
    service = get_calendar_service()

    start_dt = datetime.fromisoformat(f"{date_yyyy_mm_dd}T{hh_mm}:00").replace(tzinfo=TZ)
    end_dt = start_dt + timedelta(minutes=CONSULTA_MIN)

    desc = []
    if patient_telefone:
        desc.append(f"TELEFONE: {patient_telefone}")
    desc_text = "\n".join(desc) if desc else "Agendado via bot"

    event = {
        "summary": f"Consulta - {patient_name}",
        "description": desc_text,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/Fortaleza"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "America/Fortaleza"},
    }

    created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created  # retorna dict do evento (tem id, htmlLink etc.)

def get_events_for_day(day: datetime) -> list[dict]:
    service = get_calendar_service()

    if day.tzinfo is None:
        day = day.replace(tzinfo=TZ)
    else:
        day = day.astimezone(TZ)

    start_day = day.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=TZ)
    end_day = start_day + timedelta(days=1)

    return list_events_in_range(service, start_day, end_day)