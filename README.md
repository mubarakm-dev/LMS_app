# SQI LMS

A terminal-based learning management system built with Python and MySQL, using an N-tier architecture. Students, instructors and admins each get their own menu. Quizzes can be translated into other languages and read aloud, and many menu actions can be triggered by voice.

## Features

| Role | What they can do |
|---|---|
| Everyone | Register with email OTP verification, log in, view and update their profile, change password |
| Student | Browse and enroll in courses, read lessons, view and submit assignments, see marks, take timed quizzes (in a translated language, with read-aloud), speak commands |
| Instructor | Create, update and delete courses, view enrolled students, manage lessons, assignments and quizzes, grade submissions, release results, translate quizzes, reports and CSV exports, speak commands, voice translator |
| Admin | View, search and filter users, change roles, disable and reactivate accounts, platform statistics, CSV summary report |

Permissions are enforced in the services layer, not just hidden in the menus. Every protected call also re-checks the database, so a disabled account or a changed role takes effect on the next action.

## Architecture

```
main.py                  wires everything together (the only place that does)
src/
  presentation/          terminal menus only (input and print)
    student/  teacher/
  services/              business rules and permissions (@require_role)
  data/
    connection.py
    repositories/        all SQL, one repository per table
  integration/           email, translator, text-to-speech, speech-to-text, CSV
  domain/                models, enums, errors
  config.py              reads .env
sql/                     schema.sql, seed.sql
output/                  generated CSV files (not committed)
```

A menu calls a service, a service calls repositories and integrations. Nothing calls upwards, and SQL appears only in `data/repositories/`.

## Requirements

- Python 3 (developed and tested on Python 3.14, Windows 11)
- XAMPP (or any MySQL / MariaDB server)
- A microphone and speakers for the voice features
- Internet for: sending verification emails, read-aloud (Edge TTS), and the first-time model downloads
- ffmpeg on your PATH (Whisper needs it)

## Installation

1. **Create and activate a virtual environment**

   ```
   python -m venv lms_env
   lms_env\Scripts\activate          # macOS/Linux: source lms_env/bin/activate
   ```

2. **Install the packages**

   ```
   pip install -r requirements.txt
   ```

   This project uses `pygame-ce`, not `pygame`, because the regular package does not build on Python 3.14.

3. **Create the database**

   Start MySQL in XAMPP, then run both files from the `sql` folder, in this order:

   ```
   mysql -u root < sql/schema.sql
   mysql -u root < sql/seed.sql
   ```

   Or open phpMyAdmin, choose Import, and import `schema.sql` and then `seed.sql`.

   Warning: `schema.sql` starts with `DROP DATABASE IF EXISTS lms_db`, so running it again wipes all data.

4. **Configure the environment**

   Copy `.env.example` to `.env` and fill it in. Never commit `.env`.

   | Variable | Meaning | Default |
   |---|---|---|
   | DB_HOST, DB_PORT | MySQL server | localhost, 3306 |
   | DB_USER, DB_PASSWORD | MySQL login | root, empty (XAMPP) |
   | DB_NAME | database name | lms_db |
   | SMTP_HOST, SMTP_PORT | mail server | smtp.gmail.com, 465 |
   | SMTP_USER, SMTP_PASSWORD | sender account (for Gmail use an App Password) | none |
   | OUTPUT_DIR | where CSV files are saved | output |

5. **Install the translation models (once, needs internet)**

   Translation runs offline with Argos Translate, but each language pair must be downloaded first:

   ```python
   import argostranslate.package as package

   package.update_package_index()
   wanted = {("en", "fr"), ("fr", "en"), ("en", "es"), ("en", "ar"), ("ar", "en")}
   for p in package.get_available_packages():
       if (p.from_code, p.to_code) in wanted:
           package.install_from_path(p.download())
   ```

   Save it as a file and run it with the virtual environment active.

6. **Whisper model.** The first voice command downloads the `base` model (about 140 MB) automatically.

## Running

```
python main.py
```

The seeded admin account is:

| Email | Password |
|---|---|
| admin@sqi.testing | Admin@1234 |

Change this password from the profile menu before using the system for real. Register students and instructors through the app, verify them with the emailed code, and promote an instructor from the admin menu.

## Voice features

- **Read aloud:** during a quiz type `R` to hear the current question and its options. Instructors can listen while reviewing a translation. The answer key is never read.
- **Speak a command:** student menu 9, instructor menu 10. Record for 5 seconds and say a command ("my courses", "reports") or an option number ("option 5"). Sensitive actions such as enrolling, submitting, deleting and logging out ask you to confirm first.
- **Voice translator (instructors):** instructor menu 11. Choose the language you speak and the language to translate into, speak for 8 seconds, and the translation is shown and spoken back.

Speech is generated by Edge TTS (online) and recognised by Whisper (offline).

## Languages

| | English | French | Spanish | Arabic |
|---|---|---|---|---|
| Translate from English | source | yes | yes | yes |
| Translate to English | n/a | yes | no | yes |
| Spoken voice | yes | yes | yes | yes |
| Voice translator input | yes | yes | no | yes |

Only language pairs that were tested are offered. Voice commands are English only.

## Known limitations

- Spanish to English translation produced unusable output, so it is disabled.
- Yoruba and Hausa are not supported: there is no offline translation model and no text-to-speech voice for them.
- Arabic text may look reversed in a terminal that does not support right-to-left text. The audio is unaffected.
- Machine translations should be reviewed by the instructor before a quiz is given. Students only see a language when every question in the quiz has an up-to-date translation.
- Voice recognition accuracy depends on the microphone and accent. The first voice command is slow while Whisper loads. Typing the menu number always works.
- Read-aloud needs internet access.
- Quiz timers are kept in memory, so restarting the app during a quiz loses the timer.
- Logins are not rate limited and there is no password-reset flow.

## Security notes

- Passwords are hashed with bcrypt and must contain 8 or more characters with upper case, lower case, a digit and a special character.
- Email verification uses a 6-digit code that expires after 10 minutes and allows 5 attempts.
- All SQL uses parameterized queries.
- CSV exports guard against spreadsheet formula injection.
- Students never receive the correct answers while a quiz is open.
