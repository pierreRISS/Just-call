import logging
from typing import Annotated
from urllib.parse import parse_qs

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session
from twilio.base.exceptions import TwilioRestException
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.rest import Client
from twilio.twiml.voice_response import Dial, VoiceResponse

from app.config import settings
from app.database import Base, engine, get_db
from app.models import CallLog, Contact, Meeting
from app.schemas import (
    CallLogCreate,
    CallLogRead,
    ContactCreate,
    ContactRead,
    ContactUpdate,
    MeetingCreate,
    MeetingRead,
    OutboundCallCreate,
    OutboundCallRead,
    VoiceConfigRead,
    VoiceTokenRead,
)

app = FastAPI(title="Just Call API")
logger = logging.getLogger("just-call.voice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=(
        r"http://("
        r"localhost|127\.0\.0\.1|0\.0\.0\.0|"
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        r"172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|"
        r"192\.168\.\d{1,3}\.\d{1,3}"
        r"):(5173|5174|5175|5176|5177|5178|5179)"
    ),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/contacts", response_model=list[ContactRead])
def list_contacts(db: Annotated[Session, Depends(get_db)]) -> list[Contact]:
    statement = select(Contact).order_by(Contact.created_at.asc(), Contact.id.asc())
    return list(db.scalars(statement))


@app.post("/contacts", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: Annotated[Session, Depends(get_db)]) -> Contact:
    existing_contact = db.scalar(
        select(Contact).where(Contact.phone_number == payload.phone_number)
    )
    if existing_contact is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This phone number is already in the call list.",
        )

    contact = Contact(
        name=payload.name,
        phone_number=payload.phone_number,
        notes=payload.notes,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@app.patch("/contacts/{contact_id}", response_model=ContactRead)
def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Contact:
    contact = db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )

    updates = payload.model_dump(exclude_unset=True)
    if "phone_number" in updates and updates["phone_number"] != contact.phone_number:
        existing_contact = db.scalar(
            select(Contact).where(Contact.phone_number == updates["phone_number"])
        )
        if existing_contact is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This phone number is already in the call list.",
            )

    for field_name, value in updates.items():
        setattr(contact, field_name, value)

    db.commit()
    db.refresh(contact)
    return contact


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    contact = db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )

    db.delete(contact)
    db.commit()


@app.get("/call-logs", response_model=list[CallLogRead])
def list_call_logs(db: Annotated[Session, Depends(get_db)]) -> list[CallLog]:
    statement = select(CallLog).order_by(CallLog.created_at.desc(), CallLog.id.desc())
    return list(db.scalars(statement))


@app.delete("/call-logs", status_code=status.HTTP_204_NO_CONTENT)
def delete_call_logs(db: Annotated[Session, Depends(get_db)]) -> None:
    db.execute(update(Meeting).where(Meeting.call_log_id.is_not(None)).values(call_log_id=None))
    db.execute(delete(CallLog))
    db.commit()


@app.post("/call-logs", response_model=CallLogRead, status_code=status.HTTP_201_CREATED)
def create_call_log(payload: CallLogCreate, db: Annotated[Session, Depends(get_db)]) -> CallLog:
    contact = db.get(Contact, payload.contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )

    call_log = CallLog(
        contact=contact,
        contact_name=contact.name,
        phone_number=contact.phone_number,
        outcome=payload.outcome,
        duration_seconds=payload.duration_seconds,
        notes=payload.notes,
    )
    contact.last_called_at = func.now()
    db.add(call_log)
    db.commit()
    db.refresh(call_log)
    return call_log


@app.post("/calls", response_model=OutboundCallRead, status_code=status.HTTP_201_CREATED)
def create_outbound_call(payload: OutboundCallCreate) -> OutboundCallRead:
    if (
        not settings.twilio_account_sid
        or not settings.twilio_auth_token
        or not settings.twilio_phone_number
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Twilio is not configured on the server.",
        )

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    try:
        call = client.calls.create(
            url=settings.twilio_voice_url,
            to=payload.to,
            from_=settings.twilio_phone_number,
        )
    except TwilioRestException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.msg or "Twilio could not create the call.",
        ) from exc

    return OutboundCallRead(
        sid=call.sid,
        status=call.status,
        to=payload.to,
        from_number=settings.twilio_phone_number,
    )


def missing_voice_config() -> list[str]:
    required_values = {
        "TWILIO_ACCOUNT_SID": settings.twilio_account_sid,
        "TWILIO_PHONE_NUMBER": settings.twilio_phone_number,
        "TWILIO_API_KEY_SID": settings.twilio_api_key_sid,
        "TWILIO_API_KEY_SECRET": settings.twilio_api_key_secret,
        "TWILIO_TWIML_APP_SID": settings.twilio_twiml_app_sid,
    }
    return [name for name, value in required_values.items() if not value]


@app.get("/voice/config", response_model=VoiceConfigRead)
def get_voice_config() -> VoiceConfigRead:
    missing = missing_voice_config()
    return VoiceConfigRead(
        is_ready=not missing,
        missing=missing,
        phone_number=settings.twilio_phone_number,
    )


@app.get("/voice/token", response_model=VoiceTokenRead)
def create_voice_token() -> VoiceTokenRead:
    missing = missing_voice_config()
    if missing:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Twilio Voice is missing: {', '.join(missing)}.",
        )

    identity = "just-call-browser"
    token = AccessToken(
        settings.twilio_account_sid,
        settings.twilio_api_key_sid,
        settings.twilio_api_key_secret,
        identity=identity,
    )
    token.add_grant(
        VoiceGrant(
            outgoing_application_sid=settings.twilio_twiml_app_sid,
            incoming_allow=False,
        )
    )

    return VoiceTokenRead(token=token.to_jwt(), identity=identity)


async def voice_twiml_response(request: Request) -> Response:
    if not settings.twilio_phone_number:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Twilio phone number is not configured on the server.",
        )

    if request.method == "GET":
        to_number = (request.query_params.get("To") or "").strip()
    else:
        raw_body = (await request.body()).decode("utf-8")
        form_payload = parse_qs(raw_body)
        to_number = (form_payload.get("To") or [""])[0].strip()

    logger.info("Twilio Voice webhook received: method=%s to=%s", request.method, to_number or "<missing>")

    response = VoiceResponse()
    if not to_number:
        response.say("Missing destination number.")
        logger.warning("Twilio Voice webhook missing To parameter.")
        return Response(content=str(response), media_type="application/xml")

    dial = Dial(caller_id=settings.twilio_phone_number)
    dial.number(to_number)
    response.append(dial)

    return Response(content=str(response), media_type="application/xml")


@app.get("/voice/twiml")
async def create_voice_twiml_get(request: Request) -> Response:
    return await voice_twiml_response(request)


@app.post("/voice/twiml")
async def create_voice_twiml_post(request: Request) -> Response:
    return await voice_twiml_response(request)


@app.get("/meetings", response_model=list[MeetingRead])
def list_meetings(db: Annotated[Session, Depends(get_db)]) -> list[Meeting]:
    statement = select(Meeting).order_by(Meeting.scheduled_at.asc(), Meeting.id.asc())
    return list(db.scalars(statement))


@app.post("/meetings", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
def create_meeting(payload: MeetingCreate, db: Annotated[Session, Depends(get_db)]) -> Meeting:
    contact = db.get(Contact, payload.contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )

    call_log = None
    if payload.call_log_id is not None:
        call_log = db.get(CallLog, payload.call_log_id)
        if call_log is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call log not found.",
            )

    meeting = Meeting(
        contact=contact,
        call_log=call_log,
        contact_name=contact.name,
        phone_number=contact.phone_number,
        scheduled_at=payload.scheduled_at,
        notes=payload.notes,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting
