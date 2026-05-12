from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.database import SessionLocal
from app.models import AIReview, Prospect, ReplaySession, SalesCall, User, UserSettings
from app.security import hash_password


def seed_database() -> None:
    with SessionLocal() as db:
        existing_user = db.scalar(select(User).where(User.email == "pierre@just-call.local"))
        if existing_user is not None:
            return

        user = User(
            email="pierre@just-call.local",
            display_name="Pierre Caller",
            role="Senior account executive",
            password_hash=hash_password("justcall"),
        )
        db.add(user)
        db.flush()

        prospects = [
            Prospect(
                user_id=user.id,
                name="Camille Laurent",
                company="Nestra",
                role="VP Revenue",
                phone_number="+33 6 42 19 80 14",
                email="camille@nestra.co",
                status="Advancing",
                priority="High",
                temperature="Warm",
                context=(
                    "Nestra is hiring 18 account executives this quarter. Camille cares about "
                    "ramp speed, clean process, and coaching without adding manager overhead."
                ),
                previous_notes=(
                    "Camille reacted well to manager leverage. She asked for proof that reps "
                    "would not need extra admin."
                ),
                call_objective="Confirm pilot criteria and secure a workflow review with her sales managers.",
                possible_objections=["Adoption risk", "Manager time", "Existing call recording tools"],
                priority_signals=["Hiring sales team", "Recent Series A", "Outbound motion"],
                last_touch="LinkedIn reply, 2 days ago",
                last_call="Today",
                last_called_at=datetime.now(UTC) - timedelta(hours=2),
            ),
            Prospect(
                user_id=user.id,
                name="Arthur Besson",
                company="AltoPay",
                role="Head of Sales",
                phone_number="+33 7 61 45 12 70",
                email="arthur@altopay.io",
                status="Engaged",
                priority="Medium",
                temperature="Neutral",
                context=(
                    "AltoPay sells into mid-market finance teams. Arthur mentioned inconsistent "
                    "discovery quality across new reps."
                ),
                previous_notes=(
                    "Arthur wants less variability between reps. He is comparing enablement tools this month."
                ),
                call_objective="Understand current coaching cadence and identify one measurable pilot outcome.",
                possible_objections=["Budget timing", "Tool overlap", "Data privacy"],
                priority_signals=["Discovery gaps", "Mid-market", "Training budget"],
                last_touch="Email opened today",
                last_call="Yesterday",
                last_called_at=datetime.now(UTC) - timedelta(days=1),
            ),
            Prospect(
                user_id=user.id,
                name="Maya Chen",
                company="HelioWorks",
                role="Founder",
                phone_number="+33 6 88 02 33 91",
                email="maya@helioworks.com",
                status="New",
                priority="Low",
                temperature="Cold",
                context=(
                    "Small founder-led sales team. Likely sensitive to tools that feel heavy. "
                    "Lead with clarity and low setup."
                ),
                previous_notes="Maya is skeptical of operational drag. Keep the story concrete and lightweight.",
                call_objective="Earn permission for a short second conversation around founder-led sales habits.",
                possible_objections=["Too many tools", "Small team", "No time to implement"],
                priority_signals=["Founder-led sales", "Lean team", "No CRM admin"],
                last_touch="No previous contact",
                last_call="No call yet",
            ),
        ]
        db.add_all(prospects)
        db.flush()

        calls = [
            SalesCall(
                user_id=user.id,
                prospect_id=prospects[0].id,
                prospect_name=prospects[0].name,
                company=prospects[0].company,
                phone_number=prospects[0].phone_number,
                status="completed",
                quick_action="Meeting booked",
                duration_seconds=768,
                notes="Strong discovery. Camille wants concrete pilot success criteria.",
                transcript=(
                    "Camille pushed on adoption risk. You slowed down, clarified the team workflow, "
                    "and moved the conversation toward pilot success criteria."
                ),
                ai_summary=(
                    "Strong discovery. The clearest moment came when you tied ramp speed to lower "
                    "manager review time."
                ),
                global_score=88,
                tags=["Discovery", "Pilot interest", "Hiring signal"],
                started_at=datetime.now(UTC) - timedelta(hours=2, minutes=20),
                ended_at=datetime.now(UTC) - timedelta(hours=2, minutes=7),
            ),
            SalesCall(
                user_id=user.id,
                prospect_id=prospects[1].id,
                prospect_name=prospects[1].name,
                company=prospects[1].company,
                phone_number=prospects[1].phone_number,
                status="completed",
                quick_action="Follow-up",
                duration_seconds=499,
                notes="Good pace. Next step should be framed earlier.",
                transcript=(
                    "Arthur described uneven discovery calls. You mirrored the issue well, then waited "
                    "too long before proposing a concrete next step."
                ),
                ai_summary="Good pace, but the next step could have been framed earlier and with more confidence.",
                global_score=76,
                tags=["Objection", "Next step"],
                started_at=datetime.now(UTC) - timedelta(days=1, hours=1),
                ended_at=datetime.now(UTC) - timedelta(days=1, minutes=52),
            ),
        ]
        db.add_all(calls)
        db.flush()

        review = AIReview(
            user_id=user.id,
            call_id=calls[0].id,
            global_score=88,
            summary=(
                "You handled the adoption objection calmly and kept the conversation grounded in "
                "Camille's reality."
            ),
            strengths=[
                "You slowed down before answering the strongest objection.",
                "Your next step sounded practical, not pushy.",
                "You used her hiring context naturally.",
            ],
            improvement_focus=(
                "Pause a little longer after budget concerns. Let the prospect finish the emotional "
                "part before you move into proof."
            ),
        )
        replay = ReplaySession(
            user_id=user.id,
            call_id=calls[0].id,
            prospect_id=prospects[0].id,
            difficulty="Balanced",
            objection_type="Tool fatigue",
            prospect_behavior="Skeptical but fair",
            simulation_mode="Objection practice",
            messages=[
                {
                    "speaker": "ai",
                    "text": "I understand the promise, but my team already has too many tools.",
                },
                {
                    "speaker": "seller",
                    "text": "That is fair. The reason teams keep it is that it does not ask reps to change their workflow first.",
                },
            ],
        )
        settings = UserSettings(
            user_id=user.id,
            audio_input="Studio microphone",
            noise_cleanup="Soft",
            microphone_permission="granted",
            notifications={
                "post_call_review": True,
                "follow_up_reminders": True,
                "quiet_mode": True,
            },
            ai_preferences={
                "feedback_tone": "Encouraging",
                "replay_difficulty": "Balanced",
                "coaching_style": "Concise",
            },
            integrations={
                "crm": "prepared",
                "calendar": "connected",
                "email": "ready",
            },
            status_options=["New", "Contacted", "Engaged", "Advancing", "Scheduled", "Converted", "Archived"],
        )
        db.add_all([review, replay, settings])
        db.commit()
