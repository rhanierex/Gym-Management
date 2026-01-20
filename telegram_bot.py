# -*- coding: utf-8 -*-
import os
import requests
from datetime import datetime, timedelta
from models import Member, db
import threading
import time

class TelegramBot:
    def __init__(self, token, chat_id=None):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.last_update_id = 0
        self.flask_app = None
    
    def send_message(self, message, chat_id=None, parse_mode="HTML"):
        """Send message to Telegram"""
        try:
            target_chat_id = chat_id or self.chat_id
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": target_chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def get_updates(self, offset=None):
        """Get updates from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"timeout": 30, "offset": offset}
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                return response.json().get('result', [])
            return []
        except Exception as e:
            print(f"❌ Get updates error: {e}")
            return []
    
    def handle_command(self, message):
        """Handle incoming command"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            
            if not text:
                return
            
            # Extract command and args
            parts = text.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            print(f"📨 Received: {text} from {chat_id}")
            
            # Handle commands
            if command == '/start' or command == '/help':
                self.cmd_start(chat_id)
            elif command == '/cek':
                self.cmd_cek(chat_id, args)
            elif command == '/cari':
                self.cmd_cari(chat_id, args)
            elif command == '/expired':
                self.cmd_expired(chat_id)
            elif command == '/aktif':
                self.cmd_aktif(chat_id)
            elif command == '/stats':
                self.cmd_stats(chat_id)
            elif command == '/alert':
                self.cmd_alert(chat_id)
            elif text.startswith('MG'):
                # Quick check by ID
                self.cmd_cek(chat_id, [text])
            else:
                self.send_message(
                    "❓ Perintah tidak dikenali.\n\n"
                    "Ketik /help untuk melihat daftar perintah.",
                    chat_id
                )
                
        except Exception as e:
            print(f"❌ Handle command error: {e}")
    
    def cmd_start(self, chat_id):
        """Command /start"""
        message = """
🏋️ <b>Selamat Datang di Gym Management Bot!</b>

Gunakan command berikut:

📋 <b>INFORMASI MEMBER:</b>
/cek <code>ID_MEMBER</code> - Cek info member
/cari <code>NAMA</code> - Cari member
/expired - Member akan expired (3 hari)
/aktif - Semua member aktif

📊 <b>STATISTIK:</b>
/stats - Statistik gym
/alert - Trigger alert expired

❓ <b>BANTUAN:</b>
/help - Menu bantuan

━━━━━━━━━━━━━━━━━━━━━━
💡 <i>Kirim ID member langsung untuk cek cepat!</i>
Contoh: <code>MG698144</code>
"""
        self.send_message(message, chat_id)
    
    def cmd_cek(self, chat_id, args):
        """Command /cek [ID]"""
        if not args:
            self.send_message(
                "❌ Format salah!\n\n"
                "Gunakan: /cek <code>MG123456</code>",
                chat_id
            )
            return
        
        with self.flask_app.app_context():
            try:
                member_id = args[0].strip().upper()
                member = Member.query.filter_by(member_id=member_id).first()
                
                if not member:
                    self.send_message(
                        f"❌ Member <code>{member_id}</code> tidak ditemukan!",
                        chat_id
                    )
                    return
                
                today = datetime.now().date()
                days_left = (member.tanggal_expire.date() - today).days
                
                if days_left < 0:
                    status = f"❌ <b>EXPIRED ({abs(days_left)} hari lalu)</b>"
                    status_emoji = "🔴"
                elif days_left == 0:
                    status = "⚠️ <b>EXPIRED HARI INI</b>"
                    status_emoji = "🟠"
                elif days_left <= 3:
                    status = f"⚠️ <b>Akan expired {days_left} hari lagi</b>"
                    status_emoji = "🟡"
                else:
                    status = f"✅ <b>Aktif ({days_left} hari lagi)</b>"
                    status_emoji = "🟢"
                
                msg = f"{status_emoji} <b>INFO MEMBER</b>\n"
                msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                msg += f"🆔 ID: <code>{member.member_id}</code>\n"
                msg += f"👤 Nama: <b>{member.nama}</b>\n"
                msg += f"📱 HP: {member.no_handphone}\n"
                msg += f"🏠 Alamat: {member.alamat}\n"
                msg += f"👔 Pekerjaan: {member.pekerjaan}\n"
                msg += f"⚧ Gender: {member.jenis_kelamin}\n\n"
                msg += f"💳 Type: <b>{member.type_member.replace('_', ' ').title()}</b>\n"
                msg += f"💰 Biaya: Rp {member.biaya_bulanan:,.0f}/bulan\n"
                msg += f"📆 Terdaftar: {member.tanggal_daftar.strftime('%d-%m-%Y')}\n"
                msg += f"📅 Expired: {member.tanggal_expire.strftime('%d-%m-%Y')}\n\n"
                msg += f"⏰ Status: {status}\n\n"
                msg += f"🕒 {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
                
                self.send_message(msg, chat_id)
                
            except Exception as e:
                self.send_message(f"❌ Error: {str(e)}", chat_id)
    
    def cmd_cari(self, chat_id, args):
        """Command /cari [NAMA]"""
        if not args:
            self.send_message(
                "❌ Format salah!\n\n"
                "Gunakan: /cari <code>nama member</code>",
                chat_id
            )
            return
        
        with self.flask_app.app_context():
            try:
                search_name = ' '.join(args).strip()
                members = Member.query.filter(
                    Member.nama.ilike(f'%{search_name}%')
                ).all()
                
                if not members:
                    self.send_message(
                        f"❌ Tidak ada member dengan nama '<b>{search_name}</b>'",
                        chat_id
                    )
                    return
                
                msg = f"🔍 <b>HASIL PENCARIAN: {search_name}</b>\n"
                msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                today = datetime.now().date()
                
                for idx, member in enumerate(members[:10], 1):
                    days_left = (member.tanggal_expire.date() - today).days
                    
                    if days_left < 0:
                        emoji = "🔴"
                    elif days_left <= 3:
                        emoji = "🟡"
                    else:
                        emoji = "🟢"
                    
                    msg += f"{idx}. {emoji} <b>{member.nama}</b>\n"
                    msg += f"   🆔 <code>{member.member_id}</code>\n"
                    msg += f"   📅 {member.tanggal_expire.strftime('%d-%m-%Y')}\n"
                    msg += f"   ⏰ {days_left} hari lagi\n\n"
                
                if len(members) > 10:
                    msg += f"<i>...dan {len(members) - 10} member lainnya</i>\n\n"
                
                msg += f"📊 Total: <b>{len(members)}</b> ditemukan"
                
                self.send_message(msg, chat_id)
                
            except Exception as e:
                self.send_message(f"❌ Error: {str(e)}", chat_id)
    
    def cmd_expired(self, chat_id):
        """Command /expired"""
        with self.flask_app.app_context():
            try:
                today = datetime.now()
                three_days = today + timedelta(days=3)
                
                members = Member.query.filter(
                    Member.tanggal_expire >= today,
                    Member.tanggal_expire <= three_days
                ).order_by(Member.tanggal_expire.asc()).all()
                
                if not members:
                    self.send_message(
                        "✅ Tidak ada member yang akan expired dalam 3 hari!",
                        chat_id
                    )
                    return
                
                msg = "⚠️ <b>MEMBER AKAN EXPIRED (3 HARI)</b>\n"
                msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for idx, m in enumerate(members, 1):
                    days = (m.tanggal_expire.date() - today.date()).days
                    
                    if days == 0:
                        st = "⚠️ <b>HARI INI</b>"
                    elif days == 1:
                        st = "⚠️ <b>BESOK</b>"
                    else:
                        st = f"📅 <b>{days} hari lagi</b>"
                    
                    msg += f"{idx}. 👤 <b>{m.nama}</b>\n"
                    msg += f"   🆔 <code>{m.member_id}</code>\n"
                    msg += f"   📱 {m.no_handphone}\n"
                    msg += f"   📅 {m.tanggal_expire.strftime('%d-%m-%Y')}\n"
                    msg += f"   ⏰ {st}\n\n"
                
                msg += f"📊 Total: <b>{len(members)}</b> member"
                
                self.send_message(msg, chat_id)
                
            except Exception as e:
                self.send_message(f"❌ Error: {str(e)}", chat_id)
    
    def cmd_aktif(self, chat_id):
        """Command /aktif"""
        with self.flask_app.app_context():
            try:
                today = datetime.now()
                
                members = Member.query.filter(
                    Member.tanggal_expire >= today
                ).order_by(Member.tanggal_expire.asc()).all()
                
                if not members:
                    self.send_message("❌ Tidak ada member aktif", chat_id)
                    return
                
                msg = "✅ <b>MEMBER AKTIF</b>\n"
                msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for idx, m in enumerate(members[:15], 1):
                    days = (m.tanggal_expire.date() - today.date()).days
                    
                    if days <= 3:
                        emoji = "🟡"
                    else:
                        emoji = "🟢"
                    
                    msg += f"{idx}. {emoji} <b>{m.nama}</b>\n"
                    msg += f"   🆔 <code>{m.member_id}</code>\n"
                    msg += f"   📅 {m.tanggal_expire.strftime('%d-%m-%Y')} ({days}h)\n\n"
                
                if len(members) > 15:
                    msg += f"<i>...dan {len(members) - 15} member lainnya</i>\n\n"
                
                msg += f"📊 Total: <b>{len(members)}</b> member aktif"
                
                self.send_message(msg, chat_id)
                
            except Exception as e:
                self.send_message(f"❌ Error: {str(e)}", chat_id)
    
    def cmd_stats(self, chat_id):
        """Command /stats"""
        with self.flask_app.app_context():
            try:
                today = datetime.now()
                
                aktif = Member.query.filter(Member.tanggal_expire >= today).count()
                expired = Member.query.filter(Member.tanggal_expire < today).count()
                total = db.session.query(db.func.sum(Member.total)).scalar() or 0
                
                three_days = today + timedelta(days=3)
                akan_exp = Member.query.filter(
                    Member.tanggal_expire >= today,
                    Member.tanggal_expire <= three_days
                ).count()
                
                msg = "📊 <b>STATISTIK GYM</b>\n"
                msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                msg += "📈 <b>MEMBER:</b>\n"
                msg += f"✅ Aktif: <b>{aktif}</b>\n"
                msg += f"❌ Expired: <b>{expired}</b>\n"
                msg += f"⚠️ Akan Expired (3hr): <b>{akan_exp}</b>\n\n"
                msg += "💰 <b>PENDAPATAN:</b>\n"
                msg += f"💵 Total: <b>Rp {total:,.0f}</b>\n\n"
                msg += f"🕒 {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
                
                self.send_message(msg, chat_id)
                
            except Exception as e:
                self.send_message(f"❌ Error: {str(e)}", chat_id)
    
    def cmd_alert(self, chat_id):
        """Command /alert"""
        self.send_message("🔄 Checking member yang akan expired...", chat_id)
        
        with self.flask_app.app_context():
            try:
                today = datetime.now()
                three_days = today + timedelta(days=3)
                
                members = Member.query.filter(
                    Member.tanggal_expire >= today,
                    Member.tanggal_expire <= three_days
                ).order_by(Member.tanggal_expire.asc()).all()
                
                if members:
                    self.send_expiry_alert(members, chat_id)
                    self.send_message(
                        f"✅ Alert dikirim untuk <b>{len(members)}</b> member!",
                        chat_id
                    )
                else:
                    self.send_message(
                        "✅ Tidak ada member yang akan expired dalam 3 hari!",
                        chat_id
                    )
                    
            except Exception as e:
                self.send_message(f"❌ Error: {str(e)}", chat_id)
    
    def send_expiry_alert(self, members, chat_id=None):
        """Send expiry alert"""
        if not members:
            return
        
        msg = "🚨 <b>ALERT: Member Akan Expired</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        today = datetime.now().date()
        
        for m in members:
            days = (m.tanggal_expire.date() - today).days
            
            if days == 0:
                st = "⚠️ <b>HARI INI</b>"
            elif days == 1:
                st = "⚠️ <b>BESOK</b>"
            else:
                st = f"📅 <b>{days} hari lagi</b>"
            
            msg += f"👤 <b>{m.nama}</b>\n"
            msg += f"🆔 <code>{m.member_id}</code>\n"
            msg += f"📱 {m.no_handphone}\n"
            msg += f"💳 {m.type_member.replace('_', ' ').title()}\n"
            msg += f"📅 {m.tanggal_expire.strftime('%d-%m-%Y')}\n"
            msg += f"⏰ {st}\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        msg += f"📊 Total: <b>{len(members)}</b> member"
        
        self.send_message(msg, chat_id)
    
    def start_polling(self, flask_app):
        """Start polling for updates"""
        self.flask_app = flask_app
        print("🤖 Telegram Bot polling started!")
        print("📋 Commands: /start, /help, /cek, /cari, /expired, /aktif, /stats, /alert")
        
        while True:
            try:
                updates = self.get_updates(self.last_update_id + 1)
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    
                    if 'message' in update:
                        self.handle_command(update['message'])
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Polling error: {e}")
                time.sleep(5)


def get_telegram_bot():
    """Get Telegram Bot instance"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if token:
        return TelegramBot(token, chat_id)
    else:
        print("⚠️ TELEGRAM_BOT_TOKEN not set")
        return None


def check_expiring_members(app):
    """Check expiring members and send alert"""
    with app.app_context():
        try:
            bot = get_telegram_bot()
            if not bot:
                return
            
            bot.flask_app = app
            
            today = datetime.now()
            three_days = today + timedelta(days=3)
            
            members = Member.query.filter(
                Member.tanggal_expire >= today,
                Member.tanggal_expire <= three_days
            ).order_by(Member.tanggal_expire.asc()).all()
            
            if members and bot.chat_id:
                bot.send_expiry_alert(members, bot.chat_id)
                print(f"✅ Alert sent for {len(members)} members")
            else:
                print("ℹ️ No members expiring")
                
        except Exception as e:
            print(f"❌ Check expiring error: {e}")


def run_telegram_bot(app):
    """Run bot in polling mode"""
    bot = get_telegram_bot()
    if bot:
        bot.start_polling(app)
