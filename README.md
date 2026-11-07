🤖 Vindora Assistant

Your Smart Support Assistant for Vindora

Vindora Assistant هو بوت دعم فني على Telegram، مصمم لمساعدة مستخدمي منصة Vindora من خلال نظام أسئلة وأجوبة محلي، يساعد العملاء والمسوقين والموردين في الوصول إلى المعلومات بسهولة وسرعة.

---

✨ Features

- Multi-Audience Support: دعم ثلاثة أقسام رئيسية:
  - 🛍 Customers — العملاء.
  - 📦 Suppliers — الموردون.
  - 📢 Marketers — المسوقون.
- Smart FAQ Matching: مطابقة الأسئلة حتى مع اختلاف طريقة صياغتها.
- Arabic Text Normalization: معالجة اختلافات كتابة الحروف العربية.
- Keyword Matching: استخدام الكلمات المفتاحية للوصول إلى الإجابات المناسبة.
- Unanswered Questions: تسجيل الأسئلة التي لا يمتلك البوت إجابة مؤكدة عنها لمراجعتها.
- Admin Dashboard: لوحة إدارة خاصة بالمشرفين.
- FAQ Management: إضافة الأسئلة والإجابات وإدارة تفعيلها وتعطيلها.
- Statistics: متابعة إحصائيات المستخدمين والأسئلة.

🛠 Tech Stack

Technology| Usage
Python| Main programming language
pyTelegramBotAPI| Telegram Bot API
SQLite| Local database
RapidFuzz| Fuzzy text matching

📁 Project Structure

VindoraBot/
│
├── bot.py              # Main bot application
├── config.py           # Bot configuration
├── database.py         # Database operations
├── answer_engine.py    # FAQ matching engine
├── admin.py            # Admin dashboard
├── requirements.txt    # Dependencies
│
└── vindora.db          # SQLite database (created at runtime)

⚙️ Installation

1. Clone the Repository

git clone https://github.com/USERNAME/VindoraBot.git

cd VindoraBot

2. Install Dependencies

pip install -r requirements.txt

3. Configure the Bot

Open "config.py" and add your Telegram Bot Token and Admin ID.

BOT_TOKEN = "YOUR_BOT_TOKEN"

ADMIN_IDS = {
    123456789
}

DATABASE_NAME = "vindora.db"

ANSWER_THRESHOLD = 62

«Security: Never publish your real Bot Token or private credentials in a public repository.»

4. Run the Bot

python bot.py

---

🎛 Admin Dashboard

The bot includes a private administration panel accessible through:

/admin

Available management options:

- ➕ Add new FAQ.
- 📥 Review unanswered questions.
- 📚 Manage existing FAQs.
- 🔄 Activate or deactivate questions.
- 📊 View bot statistics.

Only Telegram IDs configured in "ADMIN_IDS" can access the administration panel.

💬 How It Works

1. The user starts the bot using "/start".
2. The user selects their category: Customer, Supplier, or Marketer.
3. The user sends a question.
4. The answer engine searches the relevant FAQ database.
5. If a suitable answer is found, the bot sends it.
6. If no suitable answer is found, the question is saved for administrator review.

📦 Requirements

pyTelegramBotAPI
rapidfuzz

Python 3.9+ is recommended.

🔐 Privacy & Security

- Administrator access is restricted by Telegram user ID.
- The database is stored locally using SQLite.
- Bot credentials should be kept private.
- Avoid sharing sensitive customer or financial information through public channels.

🚀 Project Vision

The goal of Vindora Assistant is to build a reliable support experience for the Vindora ecosystem, reduce repetitive support inquiries, and make platform information more accessible to customers, suppliers, and marketers.

Future improvements may include:

- Expanded FAQ knowledge base.
- Improved Arabic language understanding.
- Advanced question analytics.
- More administrator tools.
- Integration with additional Vindora services.

📄 License

Choose and add an appropriate open-source license before publishing this repository.

---

<p align="center">
  <strong>Vindora Assistant</strong><br>
  Smart Support. Better Experience.
</p><p align="center">
  Built for the Vindora Ecosystem.
</p>
