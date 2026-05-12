import logging
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated
from urllib.parse import parse_qs

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from twilio.base.exceptions import TwilioRestException
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.rest import Client
from twilio.twiml.voice_response import Dial, VoiceResponse

from app.ai_coach import (
    generate_replay_reply,
    generate_review,
    normalize_transcript,
    structure_transcript_text,
    transcribe_audio_file,
)
from app.config import settings
from app.database import SessionLocal, get_db
from app.models import AIReview, Prospect, ReplaySession, SalesCall, User, UserSettings
from app.schemas import (
    AIReviewCreate,
    AIReviewRead,
    AIReviewUpdate,
    AuthSessionRead,
    CallCreate,
    CallRead,
    CallUpdate,
    LoginRequest,
    OutboundCallCreate,
    OutboundCallRead,
    ProspectCreate,
    ProspectRead,
    ProspectUpdate,
    ReplaySessionCreate,
    ReplaySessionRead,
    ReplaySessionUpdate,
    ReplayMessageCreate,
    UserRead,
    UserSettingsRead,
    UserSettingsUpdate,
    VoiceConfigRead,
    VoiceTokenRead,
)
from app.security import create_session_token, hash_password, verify_password
from app.seed import seed_database

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
def seed_default_workspace() -> None:
    if settings.seed_on_startup:
        seed_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def get_default_user(db: Session) -> User:
    user = db.scalar(select(User).order_by(User.id.asc()))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is empty. Run migrations and seed the database.",
        )
    return user


def get_auth_user(request: Request, db: Session) -> User:
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in.")

    user = db.scalar(select(User).where(User.session_token == token))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Please sign in again.")
    return user


def current_user_dependency(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    return get_auth_user(request, db)


CurrentUser = Annotated[User, Depends(current_user_dependency)]


def maybe_generate_call_review(call: SalesCall, db: Session) -> AIReview | None:
    if call.status != "completed":
        return None

    try:
        review_payload = generate_review(call.transcript_data, call.transcript)
    except Exception:
        logger.exception("AI review generation failed for call %s", call.id)
        return None

    if review_payload is None:
        return None

    review = db.scalar(select(AIReview).where(AIReview.call_id == call.id))
    if review is None:
        review = AIReview(user_id=call.user_id, call_id=call.id, **review_payload)
        db.add(review)
    else:
        for field_name, value in review_payload.items():
            setattr(review, field_name, value)

    call.global_score = review_payload["global_score"]
    call.ai_summary = review_payload["summary"]
    db.commit()
    db.refresh(review)
    db.refresh(call)
    return review


def download_twilio_recording(recording_url: str) -> bytes:
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        raise ValueError("Twilio is not configured.")

    media_url = recording_url if recording_url.endswith((".mp3", ".wav")) else f"{recording_url}.mp3"
    with httpx.Client(timeout=60) as client:
        response = client.get(
            media_url,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
        )
        response.raise_for_status()
        return response.content


def process_call_recording(call_id: int, recording_url: str) -> None:
    db = SessionLocal()
    temp_path = None
    try:
        call = db.get(SalesCall, call_id)
        if call is None:
            logger.warning("Recording callback references missing call %s", call_id)
            return

        audio_bytes = download_twilio_recording(recording_url)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_file:
            audio_file.write(audio_bytes)
            temp_path = audio_file.name

        transcript = transcribe_audio_file(Path(temp_path))
        transcript_data = structure_transcript_text(transcript)
        call.recording_url = recording_url
        call.transcript = transcript
        call.transcript_data = transcript_data
        call.status = "completed"
        db.commit()
        db.refresh(call)
        maybe_generate_call_review(call, db)
    except Exception:
        logger.exception("Recording processing failed for call %s", call_id)
    finally:
        if temp_path is not None:
            Path(temp_path).unlink(missing_ok=True)
        db.close()


@app.post("/auth/login", response_model=AuthSessionRead)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> AuthSessionRead:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if user.password_hash is None:
        user.password_hash = hash_password("justcall")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    user.session_token = create_session_token()
    db.commit()
    db.refresh(user)
    return AuthSessionRead(token=user.session_token, user=user)


@app.get("/auth/session", response_model=UserRead)
def get_auth_session(user: CurrentUser) -> User:
    return user


@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    user.session_token = None
    db.commit()


@app.get("/me", response_model=UserRead)
def get_current_user(user: CurrentUser) -> User:
    return user


@app.get("/prospects", response_model=list[ProspectRead])
def list_prospects(user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> list[Prospect]:
    statement = (
        select(Prospect)
        .where(Prospect.user_id == user.id)
        .order_by(Prospect.created_at.desc(), Prospect.id.desc())
    )
    return list(db.scalars(statement))


@app.post("/prospects", response_model=ProspectRead, status_code=status.HTTP_201_CREATED)
def create_prospect(payload: ProspectCreate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> Prospect:
    existing = db.scalar(
        select(Prospect).where(
            Prospect.user_id == user.id,
            Prospect.phone_number == payload.phone_number,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This phone number is already in the prospect list.",
        )

    prospect = Prospect(user_id=user.id, **payload.model_dump())
    db.add(prospect)
    db.commit()
    db.refresh(prospect)
    return prospect


@app.get("/prospects/{prospect_id}", response_model=ProspectRead)
def get_prospect(prospect_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> Prospect:
    prospect = db.get(Prospect, prospect_id)
    if prospect is None or prospect.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect not found.")
    return prospect


@app.patch("/prospects/{prospect_id}", response_model=ProspectRead)
def update_prospect(
    prospect_id: int,
    payload: ProspectUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Prospect:
    prospect = db.get(Prospect, prospect_id)
    if prospect is None or prospect.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect not found.")

    updates = payload.model_dump(exclude_unset=True)
    if "phone_number" in updates and updates["phone_number"] != prospect.phone_number:
        existing = db.scalar(
            select(Prospect).where(
                Prospect.user_id == user.id,
                Prospect.phone_number == updates["phone_number"],
            )
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This phone number is already in the prospect list.",
            )

    for field_name, value in updates.items():
        setattr(prospect, field_name, value)

    db.commit()
    db.refresh(prospect)
    return prospect


@app.delete("/prospects/{prospect_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prospect(prospect_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    prospect = db.get(Prospect, prospect_id)
    if prospect is None or prospect.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect not found.")

    db.delete(prospect)
    db.commit()


@app.get("/calls", response_model=list[CallRead])
def list_calls(user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> list[SalesCall]:
    statement = (
        select(SalesCall)
        .options(selectinload(SalesCall.ai_review))
        .where(SalesCall.user_id == user.id)
        .order_by(SalesCall.created_at.desc(), SalesCall.id.desc())
    )
    return list(db.scalars(statement))


@app.post("/calls", response_model=CallRead, status_code=status.HTTP_201_CREATED)
def create_call(payload: CallCreate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> SalesCall:
    prospect = None
    if payload.prospect_id is not None:
        prospect = db.get(Prospect, payload.prospect_id)
        if prospect is None or prospect.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect not found.")

    data = payload.model_dump()
    if prospect is not None:
        data["prospect_name"] = data["prospect_name"] or prospect.name
        data["company"] = data["company"] or prospect.company
        data["phone_number"] = data["phone_number"] or prospect.phone_number
    data["transcript_data"] = normalize_transcript(data.get("transcript_data"), data.get("transcript"))
    if not data.get("prospect_name") or not data.get("phone_number"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A call needs either a prospect_id or prospect_name and phone_number.",
        )

    call = SalesCall(user_id=user.id, **data)
    if prospect is not None:
        prospect.last_called_at = data.get("ended_at") or data.get("started_at")
        prospect.last_call = "Today"
    db.add(call)
    db.commit()
    db.refresh(call)
    maybe_generate_call_review(call, db)
    return db.scalar(
        select(SalesCall).options(selectinload(SalesCall.ai_review)).where(SalesCall.id == call.id)
    ) or call


@app.get("/calls/{call_id}", response_model=CallRead)
def get_call(call_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> SalesCall:
    call = db.scalar(
        select(SalesCall).options(selectinload(SalesCall.ai_review)).where(SalesCall.id == call_id)
    )
    if call is None or call.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found.")
    return call


@app.patch("/calls/{call_id}", response_model=CallRead)
def update_call(
    call_id: int,
    payload: CallUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> SalesCall:
    call = db.get(SalesCall, call_id)
    if call is None or call.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found.")

    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(call, field_name, value)
    if "transcript" in updates or "transcript_data" in updates:
        call.transcript_data = normalize_transcript(call.transcript_data, call.transcript)

    db.commit()
    db.refresh(call)
    if call.status == "completed" and (
        "status" in updates
        or "transcript" in updates
        or "transcript_data" in updates
        or call.ai_review is None
    ):
        maybe_generate_call_review(call, db)
    return db.scalar(
        select(SalesCall).options(selectinload(SalesCall.ai_review)).where(SalesCall.id == call.id)
    ) or call


@app.delete("/calls/{call_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_call(call_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    call = db.get(SalesCall, call_id)
    if call is None or call.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found.")

    db.delete(call)
    db.commit()


@app.post("/ai-reviews", response_model=AIReviewRead, status_code=status.HTTP_201_CREATED)
def upsert_ai_review(payload: AIReviewCreate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> AIReview:
    call = db.get(SalesCall, payload.call_id)
    if call is None or call.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found.")

    review = db.scalar(select(AIReview).where(AIReview.call_id == payload.call_id))
    data = payload.model_dump(exclude={"call_id"})
    if review is None:
        review = AIReview(user_id=user.id, call_id=payload.call_id, **data)
        db.add(review)
    else:
        for field_name, value in data.items():
            setattr(review, field_name, value)

    call.global_score = payload.global_score
    call.ai_summary = payload.summary
    db.commit()
    db.refresh(review)
    return review


@app.patch("/ai-reviews/{review_id}", response_model=AIReviewRead)
def update_ai_review(
    review_id: int,
    payload: AIReviewUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> AIReview:
    review = db.get(AIReview, review_id)
    if review is None or review.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI review not found.")

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, field_name, value)
    if payload.global_score is not None:
        review.call.global_score = payload.global_score
    if payload.summary is not None:
        review.call.ai_summary = payload.summary

    db.commit()
    db.refresh(review)
    return review


@app.get("/replay-sessions", response_model=list[ReplaySessionRead])
def list_replay_sessions(user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> list[ReplaySession]:
    statement = (
        select(ReplaySession)
        .where(ReplaySession.user_id == user.id)
        .order_by(ReplaySession.created_at.desc(), ReplaySession.id.desc())
    )
    return list(db.scalars(statement))


@app.post("/replay-sessions", response_model=ReplaySessionRead, status_code=status.HTTP_201_CREATED)
def create_replay_session(
    payload: ReplaySessionCreate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ReplaySession:
    if payload.call_id is not None:
        call = db.get(SalesCall, payload.call_id)
        if call is None or call.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found.")
    if payload.prospect_id is not None:
        prospect = db.get(Prospect, payload.prospect_id)
        if prospect is None or prospect.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect not found.")

    replay_session = ReplaySession(
        user_id=user.id,
        **payload.model_dump(mode="json"),
    )
    db.add(replay_session)
    db.commit()
    db.refresh(replay_session)
    return replay_session


@app.patch("/replay-sessions/{replay_session_id}", response_model=ReplaySessionRead)
def update_replay_session(
    replay_session_id: int,
    payload: ReplaySessionUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ReplaySession:
    replay_session = db.get(ReplaySession, replay_session_id)
    if replay_session is None or replay_session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Replay session not found.")

    for field_name, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(replay_session, field_name, value)

    db.commit()
    db.refresh(replay_session)
    return replay_session


@app.post("/replay-sessions/{replay_session_id}/messages", response_model=ReplaySessionRead)
def send_replay_message(
    replay_session_id: int,
    payload: ReplayMessageCreate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ReplaySession:
    replay_session = db.get(ReplaySession, replay_session_id)
    if replay_session is None or replay_session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Replay session not found.")

    source_call = db.get(SalesCall, replay_session.call_id) if replay_session.call_id is not None else None
    if source_call is not None and source_call.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found.")

    current_messages = list(replay_session.messages or [])
    seller_message = {"speaker": "seller", "text": payload.text}
    messages_for_ai = [*current_messages, seller_message]

    try:
        ai_text = generate_replay_reply(
            source_transcript_data=source_call.transcript_data if source_call else None,
            source_transcript_text=source_call.transcript if source_call else None,
            messages=messages_for_ai,
            seller_message=payload.text,
            difficulty=replay_session.difficulty,
            prospect_behavior=replay_session.prospect_behavior,
            objection_type=replay_session.objection_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Replay generation failed for session %s", replay_session.id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI replay could not generate a client response.",
        ) from exc

    replay_session.messages = [
        *messages_for_ai,
        {"speaker": "ai", "text": ai_text or "Je vois. Et concretement, pourquoi je devrais changer maintenant ?"},
    ]
    replay_session.status = "active"
    db.commit()
    db.refresh(replay_session)
    return replay_session


@app.get("/settings", response_model=UserSettingsRead)
def get_settings(user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> UserSettings:
    settings_row = db.scalar(select(UserSettings).where(UserSettings.user_id == user.id))
    if settings_row is None:
        settings_row = UserSettings(user_id=user.id)
        db.add(settings_row)
        db.commit()
        db.refresh(settings_row)
    return settings_row


@app.patch("/settings", response_model=UserSettingsRead)
def update_settings(
    payload: UserSettingsUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> UserSettings:
    settings_row = get_settings(user, db)
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings_row, field_name, value)

    db.commit()
    db.refresh(settings_row)
    return settings_row


@app.post("/twilio/outbound-calls", response_model=OutboundCallRead, status_code=status.HTTP_201_CREATED)
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
        call_id = (request.query_params.get("CallId") or "").strip()
        record_consent = (request.query_params.get("RecordConsent") or "").strip()
    else:
        raw_body = (await request.body()).decode("utf-8")
        form_payload = parse_qs(raw_body)
        to_number = (form_payload.get("To") or [""])[0].strip()
        call_id = (form_payload.get("CallId") or [""])[0].strip()
        record_consent = (form_payload.get("RecordConsent") or [""])[0].strip()
        twilio_sid = (form_payload.get("CallSid") or [""])[0].strip()
        if call_id and twilio_sid:
            with SessionLocal() as db:
                call = db.get(SalesCall, int(call_id)) if call_id.isdigit() else None
                if call is not None:
                    call.twilio_sid = twilio_sid
                    db.commit()

    logger.info("Twilio Voice webhook received: method=%s to=%s", request.method, to_number or "<missing>")

    response = VoiceResponse()
    if not to_number:
        response.say("Missing destination number.")
        logger.warning("Twilio Voice webhook missing To parameter.")
        return Response(content=str(response), media_type="application/xml")

    dial_action_url = str(request.url_for("voice_dial_status")).replace("http://", "https://")
    recording_callback_url = str(request.url_for("voice_recording_status")).replace("http://", "https://")
    if call_id:
        dial_action_url = f"{dial_action_url}?call_id={call_id}"
        recording_callback_url = f"{recording_callback_url}?call_id={call_id}"

    dial_kwargs = {
        "caller_id": settings.twilio_phone_number,
        "action": dial_action_url,
        "method": "POST",
    }
    if record_consent == "true":
        dial_kwargs.update(
            {
                "record": "record-from-answer-dual",
                "recording_status_callback": recording_callback_url,
                "recording_status_callback_method": "POST",
                "recording_status_callback_event": "completed",
            }
        )

    dial = Dial(**dial_kwargs)
    dial.number(to_number)
    response.append(dial)

    return Response(content=str(response), media_type="application/xml")


@app.post("/voice/dial-status")
async def voice_dial_status(request: Request) -> Response:
    raw_body = (await request.body()).decode("utf-8")
    form_payload = parse_qs(raw_body)
    call_id = (request.query_params.get("call_id") or "").strip()
    dial_status = (form_payload.get("DialCallStatus") or [""])[0].strip()
    duration = (form_payload.get("DialCallDuration") or ["0"])[0].strip()
    parent_sid = (form_payload.get("CallSid") or [""])[0].strip()

    if call_id.isdigit():
        with SessionLocal() as db:
            call = db.get(SalesCall, int(call_id))
            if call is not None:
                call.status = "completed" if dial_status == "completed" else "failed"
                call.duration_seconds = int(duration) if duration.isdigit() else call.duration_seconds
                call.twilio_sid = call.twilio_sid or parent_sid or None
                call.ended_at = datetime.now(UTC)
                db.commit()

    response = VoiceResponse()
    response.hangup()
    return Response(content=str(response), media_type="application/xml")


@app.post("/voice/recording-status")
async def voice_recording_status(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    raw_body = (await request.body()).decode("utf-8")
    form_payload = parse_qs(raw_body)
    call_id = (request.query_params.get("call_id") or "").strip()
    recording_url = (form_payload.get("RecordingUrl") or [""])[0].strip()
    recording_status = (form_payload.get("RecordingStatus") or [""])[0].strip()

    if call_id.isdigit() and recording_url and recording_status in {"completed", "absent"}:
        with SessionLocal() as db:
            call = db.get(SalesCall, int(call_id))
            if call is not None:
                call.recording_url = recording_url
                db.commit()
        if recording_status == "completed":
            background_tasks.add_task(process_call_recording, int(call_id), recording_url)

    return {"status": "ok"}


@app.get("/voice/twiml")
async def create_voice_twiml_get(request: Request) -> Response:
    return await voice_twiml_response(request)


@app.post("/voice/twiml")
async def create_voice_twiml_post(request: Request) -> Response:
    return await voice_twiml_response(request)
