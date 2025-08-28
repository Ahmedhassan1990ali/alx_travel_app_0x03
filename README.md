# ALX Travel App with Celery Background Tasks

This project implements background task processing using Celery with RabbitMQ for handling email notifications in the ALX Travel App.

## Features

- Background email notifications for booking confirmations
- Celery task queue with RabbitMQ message broker
- Asynchronous task processing
- Email templates with HTML formatting

## Setup Instructions

### Prerequisites

- Python 3.8+
- RabbitMQ server
- SMTP email service (Gmail, SendGrid, etc.)

### Installation

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd alx_travel_app_0x03
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install RabbitMQ:**
   - Ubuntu: `sudo apt-get install rabbitmq-server`
   - Mac: `brew install rabbitmq`
   - Windows: Download from [rabbitmq.com](https://www.rabbitmq.com/)

3. **Start RabbitMQ:**
   ```bash
   sudo systemctl start rabbitmq-server  # Linux
   # or
   rabbitmq-server  # Mac/Windows
   ```

4. **Environment Variables:**
   Create a `.env` file:
   ```bash
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com
   CELERY_BROKER_URL=amqp://localhost:5672//
   CELERY_RESULT_BACKEND=rpc://
   ```

### Running the Application

1. **Start Django development server:**
   ```bash
   python manage.py runserver
   ```

2. **Start Celery worker:**
   ```bash
   celery -A alx_travel_app worker --loglevel=info
   ```

3. **Start Celery beat (if using periodic tasks):**
   ```bash
   celery -A alx_travel_app beat --loglevel=info
   ```

### Testing

1. **Create a booking through the API**
2. **Check Celery worker logs for task execution**
3. **Verify email delivery**

## File Structure

```
alx_travel_app_0x03/
├── alx_travel_app/
│   ├── __init__.py
│   ├── celery.py          # Celery configuration
│   ├── settings.py        # Updated with Celery and email config
│   └── ...
├── listings/
│   ├── tasks.py           # Celery tasks
│   ├── views.py           # Updated BookingViewSet
│   ├── templates/
│   │   └── listings/
│   │       └── email/
│   │           └── booking_confirmation.html
│   └── ...
└── README.md
```

## Troubleshooting

1. **RabbitMQ connection issues:**
   - Ensure RabbitMQ is running: `sudo systemctl status rabbitmq-server`
   - Check connection: `rabbitmqctl status`

2. **Email sending issues:**
   - Verify SMTP credentials
   - Check email provider's app password requirements

3. **Celery worker issues:**
   - Check broker URL format
   - Verify task imports with `celery -A alx_travel_app inspect registered`


