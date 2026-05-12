import logging
from typing import Annotated
from urllib.parse import parse_qs

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from twilio.base.exceptions import TwilioRestException
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.rest import Client
from twilio.twiml.voice_response import Dial, VoiceResponse

from app.config import settings
from app.database import get_db
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
    return call


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

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(call, field_name, value)

    db.commit()
    db.refresh(call)
    return call


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
