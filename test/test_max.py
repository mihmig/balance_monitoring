import os

from plugins.max_sender import MaxSender

max_sender = MaxSender(os.environ['MAX_BOT_TOKEN'])
max_sender.send_message(os.environ['MAX_CHAT_ID'],
                        "Номер +7 <b>964-296-7425</b>:\n"
                        "Осталось 🟢 <b>250</b> мин.\n"
                        "Осталось 🟢 <b>158</b> SMS\n\n"
                        "Номер +7 <b>963-200-4377</b>:\n"
                        "Осталось 🔴 <b>0</b> мин.\n"
                        "Осталось 🔴 <b>0</b> SMS")