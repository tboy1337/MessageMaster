# MessageMaster

A cross-platform Python application with Tkinter GUI that allows sending free SMS messages to mobile phones worldwide.

## Features

- Clean, modern UI with recipient input, message composition, country selection
- Multiple SMS gateway API integrations (Twilio, TextBelt, etc.)
- Message scheduling and automation
- Contact management with CSV import/export
- Message templates system
- Message history tracking
- Secure API key storage
- System tray integration
- Desktop notifications
- Cross-platform compatibility (Windows/Mac/Linux)
- Command Line Interface for automation and scripting

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Register for API keys:
   - [Twilio](https://www.twilio.com/try-twilio) - Create a free account
   - [TextBelt](https://textbelt.com/) - Get a free API key

4. Configure the application:
   - You can add your API keys through the Settings tab in the application
   - Alternatively, create a `.env` file in the project root:
     ```
     TWILIO_ACCOUNT_SID=your_account_sid
     TWILIO_AUTH_TOKEN=your_auth_token
     TWILIO_PHONE_NUMBER=your_twilio_phone_number
     TEXTBELT_API_KEY=your_textbelt_api_key
     ```

5. Run the application:
   ```
   python run.py
   ```

## Command Line Interface

The application provides a full-featured Command Line Interface (CLI) for automation and scripting:

```
python run.py cli --help
```

Or for more direct access:

```
python run.py cli send "+1234567890" "Hello from MessageMaster"
```

### CLI Commands

- `send` - Send an SMS message
  ```
  python run.py cli send RECIPIENT MESSAGE [--service SERVICE]
  ```

- `contacts` - Manage contacts
  ```
  python run.py cli contacts list
  python run.py cli contacts add NAME PHONE [--country COUNTRY] [--notes NOTES]
  python run.py cli contacts delete ID
  ```

- `history` - View message history
  ```
  python run.py cli history [--limit LIMIT]
  ```

- `schedule` - Manage scheduled messages
  ```
  python run.py cli schedule list [--all]
  python run.py cli schedule add RECIPIENT MESSAGE TIME [--service SERVICE] [--recurring {daily,weekly,monthly}] [--interval INTERVAL]
  python run.py cli schedule cancel ID
  ```

- `templates` - Manage message templates
  ```
  python run.py cli templates list
  python run.py cli templates add NAME CONTENT
  python run.py cli templates delete ID
  ```

- `services` - Manage SMS services
  ```
  python run.py cli services list
  python run.py cli services configure NAME CREDENTIALS
  python run.py cli services activate NAME
  ```

## Command Line Options

The application supports the following command line options:

```
python run.py --help
usage: main.py [-h] [--minimized] [--debug] [--config CONFIG] [--cli]

MessageMaster

optional arguments:
  -h, --help       show this help message and exit
  --minimized      Start application minimized
  --debug          Enable debug logging
  --config CONFIG  Path to custom config file
  --cli            Run in command line mode
```

## System Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python)
- For system tray functionality:
  - Windows: No additional requirements
  - macOS: `rumps` package (optional)
  - Linux: `PyGObject` and `AppIndicator3` (optional)

## Usage Limitations

- Twilio Free Trial: Limited credits for testing, recipient numbers must be verified
- TextBelt: 1 free SMS per day with free API key
- Rate limiting is implemented to comply with free tier restrictions

## Project Structure

- `src/api`: SMS service interfaces and implementations
- `src/automation`: Message scheduling and automation
- `src/cli`: Command line interface
- `src/gui`: User interface components
- `src/models`: Data models and database interaction
- `src/security`: Security and credentials management
- `src/services`: Application services (notifications, config)
- `src/utils`: Utility functions and helpers
- `tests`: Unit and integration tests

## Testing

Run the test suite:
```
python -m unittest discover tests
```

## Customization

- Application settings are stored in `~/.message_master/config.json`
- Logs are stored in `~/.message_master/logs/`
- Database is stored in `~/.message_master/message_master.db`

## Acknowledgements

- [Twilio](https://www.twilio.com/) - SMS API provider
- [TextBelt](https://textbelt.com/) - SMS API provider
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI toolkit