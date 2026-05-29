import resend

from src.common.config import config


async def send_booking_confirmation(
    to_email: str,
    user_name: str,
    movie_title: str,
    start_time: str,
    hall_name: str,
    seats: str,
    ticket_code: str,
    qr_base64: str,
) -> None:
    resend.api_key = config.resend_api_key

    html = f"""
    <h2>Ваш билет в кино</h2>
    <p>Здравствуйте, {user_name}!</p>
    <p><strong>Фильм:</strong> {movie_title}</p>
    <p><strong>Дата и время:</strong> {start_time}</p>
    <p><strong>Зал:</strong> {hall_name}</p>
    <p><strong>Места:</strong> {seats}</p>
    <p><strong>Код билета:</strong> {ticket_code}</p>
    <img src="data:image/png;base64,{qr_base64}" alt="QR-код билета" width="200" />
    <p>Покажите QR-код на входе в зал.</p>
    """

    resend.Emails.send({
        "from": config.email_from,
        "to": to_email,
        "subject": f"Билет на «{movie_title}»",
        "html": html,
    })
