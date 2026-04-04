from telethon import TelegramClient, events
import asyncio
import re

API_ID    = 31648224
API_HASH  = "ca99d29645b47c34ab39da6a68d1534d"
SESSION   = "redpacket_session"

SOURCE_CHANNELS = [
    "FreeCryptoBoxes2",
    "allbinancebox",
    "red_packetz",
]

TARGET_CHANNEL = "redpocketbinancexyz"

WELCOME_MSG = """🎁 Welcome! Thanks for joining this group where you can find Binance gift boxes.

To claim these codes you need to go on:
📱 Binance mobile app > Fundings > Pay > Crypto Box > Receive

Don't forget to react with 👍 or 👎 if the code is working or not to help others!"""

client = TelegramClient(SESSION, API_ID, API_HASH)
code_counter = 0
sent_codes = set()

def extract_code(text):
    if not text:
        return None
    clean = re.sub(r'[`\s]', '', text)
    if re.match(r'^[A-Z0-9]{6,10}$', clean):
        return clean
    return None

async def main():
    global code_counter
    await client.start()
    me = await client.get_me()
    print(f"تم الدخول: {me.first_name}")

    sources = []
    for ch in SOURCE_CHANNELS:
        try:
            entity = await client.get_entity(ch)
            sources.append(entity)
            print(f"✅ متصل بـ: {entity.title}")
        except Exception as e:
            print(f"❌ خطأ: {ch} - {e}")

    target = await client.get_entity(TARGET_CHANNEL)
    print(f"✅ الهدف: {target.title}")

    await client.send_message(target, WELCOME_MSG)
    print("✅ تم إرسال رسالة الترحيب الأولى")

    @client.on(events.NewMessage(chats=sources))
    async def handler(event):
        global code_counter
        msg = event.message
        code = extract_code(msg.text)
        if not code:
            print(f"⏭️ تخطي: {repr(msg.text)}")
            return
        if code in sent_codes:
            print(f"🔁 مكرر: {code}")
            return
        try:
            await client.send_message(target, code)
            sent_codes.add(code)
            code_counter += 1
            print(f"✅ كود [{code_counter}]: {code}")
            if code_counter % 10 == 0:
                await client.send_message(target, WELCOME_MSG)
                print(f"✅ رسالة الترحيب بعد {code_counter} كود")
        except Exception as e:
            print(f"❌ خطأ: {e}")

    print("البوت يعمل...")
    await client.run_until_disconnected()

asyncio.run(main())
