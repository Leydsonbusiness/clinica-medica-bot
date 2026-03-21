#arquivo para lembrete diário de agendamento

from datetime import datetime
from zoneinfo import ZoneInfo
from telegram.ext import ContextTypes

from bot.core.google_integration import get_events_for_day # importa função do arquivo do agendamento

TZ = ZoneInfo("America/Fortaleza")

async def agenda_daily(context: ContextTypes.DEFAULT_TYPE):
    chat_id_medico = context.bot_data["CHAT_ID_MEDICO"]

    events = get_events_for_day(datetime.now(TZ))

    if not events:
        msg = ("Bom dia, Dr. Heitor! Espero que tenha tido uma boa noite de sono para encarar mais um dia 😉. \n\n"

        "📭 *Agenda de hoje:* sem agendamentos.")

    else:
        lines = ["Bom dia, Dr. Heitor! Espero que tenha tido uma boa noite de sono para encarar mais um dia 😉. \n\n"
                 "📭 *Agenda de hoje:*"]
        for ev in events:
            if "dateTime" not in ev.get("start", {}) or "dateTime" not in ev.get("end", {}):
                continue

            s = datetime.fromisoformat(ev["start"]["dateTime"]).astimezone(TZ)
            e = datetime.fromisoformat(ev["end"]["dateTime"]).astimezone(TZ)

            title = ev.get("summary", "Sem título")
            lines.append(f"• {s.strftime('%H:%M')}–{e.strftime('%H:%M')} — {title}")
        
        msg = "\n".join(lines) if len(lines) > 1 else "📭 *Agenda de hoje:* sem agendamentos."
    
    await context.bot.send_message(chat_id = chat_id_medico, text=msg, parse_mode="Markdown")