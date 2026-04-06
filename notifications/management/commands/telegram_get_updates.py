from django.core.management.base import BaseCommand

from notifications.services import get_telegram_updates


class Command(BaseCommand):
    help = "Fetch Telegram bot updates to help detect chat_id."

    def handle(self, *args, **options):
        updates = get_telegram_updates()
        if not updates:
            self.stdout.write("No updates found.")
            return

        for update in updates:
            message = update.get("message") or update.get("channel_post") or {}
            chat = message.get("chat", {})
            self.stdout.write(
                f"update_id={update.get('update_id')} chat_id={chat.get('id')} chat_type={chat.get('type')}"
            )
