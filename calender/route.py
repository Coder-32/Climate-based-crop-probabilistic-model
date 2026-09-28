from flask import Blueprint, request, jsonify, redirect, url_for, session, send_file

try:
    from flask_dance.contrib.google import google
except Exception:
    google = None

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import os
import io
import pandas as pd
import google.genai as genai

from createpdf import CREATEPDF
from services.createevents import generate_crop_schedule, schedule_to_google_events

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
if GEMINI_API_KEY and GEMINI_API_KEY != 'your-api-key-here':
    try:
        genai_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        genai_client = None
else:
    genai_client = None

calendar_bp = Blueprint('calendar', __name__)

def get_calendar_service():
    try:
        if not google or not getattr(google, 'authorized', False):
            return None

        token = getattr(google, 'token', None)
        if not token or not token.get('access_token'):
            return None
        
        creds = Credentials(
            token=token.get('access_token'),
            refresh_token=token.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
        )
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"Calendar service notice: {e}")
        return None

@calendar_bp.route('/create_events')
def create_events():
    crop = request.args.get('crop', 'rice')
    location = request.args.get('location') or session.get('user', {}).get('location', 'Kolkata')
    try:
        schedule = generate_crop_schedule(crop, location)
    except Exception as e:
        print(f"Error generating schedule: {e}")
        return f"<h3>Error generating schedule: {e}</h3>", 500
    if schedule.empty:
        return "<h3>No schedule could be generated for the requested crop and location.</h3>", 400

    service = get_calendar_service()
    event_bodies = schedule_to_google_events(schedule, crop, location)
    created_count = 0
    failed = []

    if service is not None:
        for event in event_bodies:
            try:
                service.events().insert(calendarId='primary', body=event).execute()
                created_count += 1
            except Exception as e:
                failed.append(str(e))
    else:
        # Self-contained local schedule generation without requiring Google OAuth
        created_count = len(event_bodies)

    if failed:
        return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Calendar Sync - Partial Success</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 40px;
                max-width: 500px;
                text-align: center;
            }}
            h3 {{ color: #333; margin-bottom: 20px; font-size: 24px; }}
            .success-count {{
                font-size: 32px;
                font-weight: bold;
                color: #4caf50;
                margin: 20px 0;
            }}
            .error-count {{
                font-size: 18px;
                color: #f44336;
                margin: 10px 0;
            }}
            ul {{
                text-align: left;
                margin: 20px 0;
                padding-left: 20px;
            }}
            li {{
                color: #666;
                margin: 8px 0;
                font-size: 14px;
            }}
            a {{
                display: inline-block;
                margin-top: 30px;
                background: #667eea;
                color: white;
                padding: 12px 30px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                transition: background 0.3s ease;
            }}
            a:hover {{
                background: #764ba2;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h3>📅 Partial Calendar Sync Completed</h3>
            <div class="success-count">{created_count} Events Created</div>
            <div class="error-count">⚠️ {len(failed)} Errors</div>
            <div>
                <h4 style="color: #333; margin-top: 20px;">Error Details:</h4>
                <ul>{"".join(f"<li>❌ {error}</li>" for error in failed)}</ul>
            </div>
            <a href='https://calendar.google.com/calendar/u/0/r' target='_blank'>📖 View Your Google Calendar</a>
        </div>
    </body>
    </html>
        """

    sync_subtitle = "Your crop schedule has been successfully synced to Google Calendar" if service is not None else "Your 2026 crop production schedule is ready!"
    google_btn_html = "<a href='https://calendar.google.com/calendar/u/0/r' target='_blank' class='btn-primary'>📖 View in Google Calendar</a>" if service is not None else "<a href='/dashboard' class='btn-primary'>🌱 View Dashboard</a>"

    # On success, return styled HTML with link to Google Calendar or Dashboard
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Production Schedule Ready</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 50px;
                max-width: 600px;
                text-align: center;
            }}
            .success-icon {{
                font-size: 60px;
                margin-bottom: 20px;
            }}
            h2 {{
                color: #2d3748;
                font-size: 28px;
                margin-bottom: 12px;
            }}
            .info {{
                background: #f0f4ff;
                border-left: 4px solid #667eea;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: left;
            }}
            .info-item {{
                font-size: 16px;
                color: #4a5568;
                margin: 10px 0;
            }}
            .info-item strong {{
                color: #2d3748;
            }}
            .cta-buttons {{
                display: flex;
                gap: 12px;
                justify-content: center;
                margin-top: 30px;
                flex-wrap: wrap;
            }}
            a {{
                padding: 12px 28px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                display: inline-block;
            }}
            .btn-primary {{
                background: #667eea;
                color: white;
            }}
            .btn-primary:hover {{
                background: #764ba2;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            }}
            .btn-secondary {{
                background: #e2e8f0;
                color: #2d3748;
                border: 1px solid #cbd5e0;
            }}
            .btn-secondary:hover {{
                background: #cbd5e0;
            }}
            .chat-widget {{
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                margin-top: 24px;
                text-align: left;
            }}
            .chat-widget h3 {{
                margin-bottom: 14px;
                color: #2d3748;
            }}
            .chat-log {{
                min-height: 180px;
                max-height: 280px;
                overflow-y: auto;
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 14px;
                margin-bottom: 14px;
                color: #2d3748;
            }}
            .chat-item {{
                margin-bottom: 12px;
                line-height: 1.5;
            }}
            .chat-item.user {{
                color: #2b6cb0;
            }}
            .chat-item.bot {{
                color: #4a5568;
            }}
            .chat-actions {{
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 10px;
            }}
            .chat-actions input {{
                width: 100%;
                padding: 12px 14px;
                border-radius: 10px;
                border: 1px solid #cbd5e0;
                font-size: 15px;
            }}
            .chat-actions button {{
                background: #667eea;
                border: none;
                color: white;
                padding: 12px 18px;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s ease;
            }}
            .chat-actions button:hover {{
                transform: translateY(-1px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">✅</div>
            <h2>Schedule Generated!</h2>
            <p style="color: #718096; margin-bottom: 20px;">{sync_subtitle}</p>
            
            <div class="info">
                <div class="info-item">📅 <strong>Milestones & Tasks:</strong> {created_count} events planned</div>
                <div class="info-item">🌾 <strong>Crop:</strong> {crop.title()}</div>
                <div class="info-item">📍 <strong>Location:</strong> {location}</div>
            </div>

            <div class="chat-widget">
                <h3>Ask the AgriLab Assistant</h3>
                <div id="chatLog" class="chat-log"></div>
                <div class="chat-actions">
                    <input id="chatQuestion" placeholder="Ask about this calendar, crop schedule, or app feature..." />
                    <button id="chatSend">Send</button>
                </div>
            </div>
            
            <div class="cta-buttons">
                {google_btn_html}
                <a href="/calendar/download_pdf?crop={crop}&location={location}" class="btn-primary">📄 Download calendar.pdf</a>
                <a href="/" class="btn-secondary">← Back to Home</a>
            </div>
        </div>
    <script>
        async function postChat(question) {{
            const response = await fetch('/calendar/chat', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ question }})
            }});
            return response.json();
        }}

        document.getElementById('chatSend').addEventListener('click', async () => {{
            const questionInput = document.getElementById('chatQuestion');
            const question = questionInput.value.trim();
            if (!question) return;
            const chatLog = document.getElementById('chatLog');
            chatLog.innerHTML += `<div class="chat-item user"><strong>You:</strong> ${{question}}</div>`;
            questionInput.value = '';
            chatLog.innerHTML += `<div class="chat-item bot"><em>Thinking...</em></div>`;
            chatLog.scrollTop = chatLog.scrollHeight;

            const result = await postChat(question);
            const lastItem = chatLog.querySelector('.chat-item.bot:last-child');
            if (result && result.answer) {{
                lastItem.innerHTML = `<strong>AgriLab:</strong> ${{result.answer}}`;
            }} else {{
                lastItem.innerHTML = `<strong>AgriLab:</strong> Recommended: Follow the irrigation and nitrogen schedule in calendar.pdf for maximum yield.`;
            }}
            chatLog.scrollTop = chatLog.scrollHeight;
        }});
    </script>
    </body>
    </html>
    """


@calendar_bp.route('/download_pdf')
def download_calendar_pdf():
    crop = request.args.get('crop', 'rice')
    location = request.args.get('location') or session.get('user', {}).get('location', 'Kolkata')
    try:
        schedule = generate_crop_schedule(crop, location)
    except Exception as e:
        print(f"Error generating schedule: {e}")
        return f"<h3>Error generating PDF schedule: {e}</h3>", 500

    if schedule.empty:
        return "<h3>No schedule could be generated for the requested crop and location.</h3>", 400

    pdf_builder = CREATEPDF()
    schedule = schedule.copy()
    schedule['Month'] = pd.to_datetime(schedule['Date']).dt.month_name()

    all_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    for month in all_months:
        month_events = schedule[schedule['Month'] == month]
        if month_events.empty:
            pdf_builder.add_event(month, '', 'No scheduled events for this month.', '')
            continue

        event_text = ''
        for _, row in month_events.iterrows():
            event_text += f"Date: {row['Date']}\n"
            event_text += f"Activity: {row['Activity']}\n"
            if row.get('Requirements'):
                event_text += f"Requirements: {row['Requirements']}\n"
            event_text += '\n'

        pdf_builder.add_event(month, month_events.iloc[0]['Date'], f'{crop.title()} Schedule for {month}', event_text)

    pdf_path = pdf_builder.save()
    return send_file(pdf_path, mimetype='application/pdf', as_attachment=True, download_name='calender.pdf')


@calendar_bp.route('/chat', methods=['POST'])
def calendar_chat():
    data = request.get_json(force=True, silent=True) or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    active_client = genai_client
    if not active_client:
        key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if key and key != 'your-api-key-here':
            try:
                active_client = genai.Client(api_key=key)
            except Exception:
                active_client = None

    if active_client:
        try:
            prompt = f"You are the AgriLab calendar assistant. Answer user questions about the calendar, events, and app workflow in a helpful and concise way. Question: {question}"
            response = active_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            answer = response.text.strip()
            return jsonify({'answer': answer})
        except Exception as e:
            print(f"Gemini chat notice: {e}")

    return jsonify({
        'answer': f"AgriLab Assistant: Regarding '{question}', adhere to the watering and nutrient top-up intervals generated in your calendar.pdf schedule for best results. (Tip: set GEMINI_API_KEY in .env for custom live answers)."
    })


@calendar_bp.route('/add_harvest', methods=['GET', 'POST'])
def add_harvest():
    service = get_calendar_service()
    if not service:
        return "<h3>Success!</h3><p>Harvest recommendation simulated: Golden Wheat on 2026-05-15.</p><p><a href='/dashboard'>Return to Dashboard</a></p>"

    crop_name = "Golden Wheat - Plot A"
    harvest_date = "2026-05-15"

    event = {
        'summary': f'🌾 Harvest Recommendation: {crop_name}',
        'description': 'Automated recommendation based on MarEye surveillance and GDD data.',
        'start': {
            'date': harvest_date, 
            'timeZone': 'Asia/Kolkata'
        },
        'end': {
            'date': harvest_date, 
            'timeZone': 'Asia/Kolkata'
        },
        'colorId': '5',
        'reminders': {
            'useDefault': True
        }
    }

    try:
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        return f"<h3>Success!</h3><p>Event created: <a href='{event_result.get('htmlLink')}'>View on Google Calendar</a></p>"
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return f"<h3>Error</h3><p>{str(e)}</p>"