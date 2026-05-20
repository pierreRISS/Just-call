import json
import random
import re
from pathlib import Path
from typing import Any

from groq import Groq

from app.config import settings

METRIC_DEFINITIONS: list[dict[str, str]] = [
    {
        "id": "control",
        "label": "Lead control",
        "focus": "cadre l'echange, garde l'initiative, reformule et avance sans forcer",
    },
    {
        "id": "listening",
        "label": "Listening quality",
        "focus": "ecoute, rebondit sur les reponses, creuse contexte, douleurs, impact et timing",
    },
    {
        "id": "confidence",
        "label": "Confidence",
        "focus": "intro claire, ton assure, phrases courtes, preuve ou exemple credible",
    },
    {
        "id": "objections",
        "label": "Objection handling",
        "focus": "accueille les objections, les traite concretement et reprend le fil",
    },
    {
        "id": "closing",
        "label": "Closing clarity",
        "focus": "pitch utile, prochaine etape claire, demande simple et assumee",
    },
]

FALLBACK_STRENGTHS = [
    "Tu as garde une structure claire malgre un appel incomplet.",
    "Le contexte prospect est assez propre pour alimenter le reste du coaching.",
    "La prochaine etape reste lisible pour continuer le suivi commercial.",
    "Les notes donnent une base exploitable pour rejouer l'appel avec l'IA.",
]

FALLBACK_FOCUS = [
    "Clarifie la prochaine etape en une phrase simple, puis confirme un horaire precis.",
    "Pose une question de douleur avant de presenter la solution.",
    "Reformule l'objection principale avant de revenir a la valeur metier.",
    "Garde une intro plus courte et bascule plus vite vers le contexte du prospect.",
]


def normalize_transcript(
    transcript_data: list[dict[str, Any]] | None,
    transcript_text: str | None,
) -> list[dict[str, str]]:
    if transcript_data:
        normalized: list[dict[str, str]] = []
        for turn in transcript_data:
            speaker = normalize_speaker(str(turn.get("speaker", "")))
            text = str(turn.get("text", "")).strip()
            if speaker and text:
                normalized.append({"speaker": speaker, "text": text})
        if normalized:
            return normalized

    text = (transcript_text or "").strip()
    if not text:
        return []

    turns: list[dict[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^(caller|seller|commercial|client|prospect|ai)\s*:\s*(.+)$", line, re.I)
        if match:
            speaker = normalize_speaker(match.group(1))
            content = match.group(2).strip()
        else:
            speaker = "caller"
            content = line
        if speaker and content:
            turns.append({"speaker": speaker, "text": content})
    return turns


def normalize_speaker(value: str) -> str | None:
    speaker = value.strip().casefold()
    if speaker in {"caller", "seller", "commercial", "rep"}:
        return "caller"
    if speaker in {"client", "prospect", "ai", "customer"}:
        return "client"
    return None


def transcript_to_text(turns: list[dict[str, str]]) -> str:
    return "\n".join(f"{turn['speaker']}: {turn['text']}" for turn in turns)


def generate_review(
    transcript_data: list[dict[str, Any]] | None,
    transcript_text: str | None,
) -> dict[str, Any] | None:
    if not settings.groq_api_key:
        return None

    turns = normalize_transcript(transcript_data, transcript_text)
    if not turns:
        return None

    client = Groq(api_key=settings.groq_api_key)
    metric_contract = "\n".join(
        f"- {metric['id']} ({metric['label']}): {metric['focus']}"
        for metric in METRIC_DEFINITIONS
    )
    prompt = (
        "Tu es un coach de cold call B2B. Analyse l'appel avec des conseils courts, "
        "directs et impactants. Note sur 100, pas sur 10.\n\n"
        "Criteres obligatoires:\n"
        f"{metric_contract}\n\n"
        "Reponds uniquement en JSON valide avec ce format exact:\n"
        '{"global_score": 72, "summary": "2 phrases maximum.", '
        '"strengths": ["phrase courte", "phrase courte"], '
        '"improvement_focus": "1 conseil prioritaire, concret, moins de 180 caracteres.", '
        '"metrics": [{"id": "control", "label": "Lead control", "score": 70, '
        '"delta": "+0%", "comment": "1 phrase courte"}]}\n\n'
        "Contraintes:\n"
        "- exactement 5 metrics, dans l'ordre des criteres\n"
        "- chaque score entre 0 et 100\n"
        "- summary: maximum 2 phrases\n"
        "- strengths: 2 items maximum\n"
        "- improvement_focus: pas de pave, une action claire\n\n"
        "Transcript structure:\n"
        f"{json.dumps(turns, ensure_ascii=False)}"
    )

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": "Tu reponds en francais, en JSON valide, sans markdown.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1200,
    )
    raw_content = str(response.choices[0].message.content or "").strip()
    parsed = parse_json_object(raw_content)
    return normalize_review_payload(parsed)


def generate_fallback_review(
    transcript_data: list[dict[str, Any]] | None,
    transcript_text: str | None,
) -> dict[str, Any]:
    turns = normalize_transcript(transcript_data, transcript_text)
    seed_text = transcript_to_text(turns) or (transcript_text or "")
    rng = random.SystemRandom()
    metrics: list[dict[str, Any]] = []

    for definition in METRIC_DEFINITIONS:
        score = rng.randint(1, 100)
        metrics.append(
            {
                "id": definition["id"],
                "label": definition["label"],
                "score": score,
                "delta": f"+{rng.randint(0, 12)}%",
                "comment": "Score de secours genere automatiquement pour garder le workflow testable.",
            }
        )

    global_score = round(sum(metric["score"] for metric in metrics) / len(metrics))
    context_note = (
        "Transcription partielle exploitee."
        if seed_text.strip()
        else "Twilio n'a pas fourni de transcription exploitable."
    )

    return {
        "global_score": global_score,
        "summary": (
            f"{context_note} Une review de secours a ete creee pour que l'historique, "
            "les scores et le replay restent fonctionnels."
        ),
        "strengths": rng.sample(FALLBACK_STRENGTHS, k=2),
        "improvement_focus": rng.choice(FALLBACK_FOCUS),
        "metrics": metrics,
    }


def generate_replay_reply(
    *,
    source_transcript_data: list[dict[str, Any]] | None,
    source_transcript_text: str | None,
    messages: list[dict[str, str]],
    seller_message: str,
    difficulty: str,
    prospect_behavior: str,
    objection_type: str,
) -> str:
    if not settings.groq_api_key:
        raise ValueError("Groq is not configured.")

    source_turns = normalize_transcript(source_transcript_data, source_transcript_text)
    client = Groq(api_key=settings.groq_api_key)
    prompt = (
        "Tu joues le client dans un replay de cold call. Reponds comme une vraie personne: "
        "court, oral, coherent, jamais professoral.\n\n"
        f"Difficulte: {difficulty}\n"
        f"Comportement client: {prospect_behavior}\n"
        f"Objection a travailler: {objection_type}\n\n"
        "Appel original:\n"
        f"{transcript_to_text(source_turns) or '[indisponible]'}\n\n"
        "Historique du replay:\n"
        f"{json.dumps(messages, ensure_ascii=False)}\n\n"
        "Dernier message du seller:\n"
        f"{seller_message}\n\n"
        "Ecris uniquement la prochaine reponse du client. Maximum 2 phrases."
    )
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": "Tu es le prospect/client. Tu ne donnes pas de coaching.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.55,
        max_tokens=180,
    )
    return str(response.choices[0].message.content or "").strip()


def transcribe_audio_file(audio_path: Path) -> str:
    if not settings.groq_api_key:
        raise ValueError("Groq is not configured.")

    client = Groq(api_key=settings.groq_api_key)
    with audio_path.open("rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(audio_path.name, audio_file.read()),
            model=settings.groq_transcription_model,
            response_format="text",
            language="fr",
        )
    return str(transcription or "").strip()


def structure_transcript_text(transcript_text: str) -> list[dict[str, str]]:
    text = transcript_text.strip()
    if not text or not settings.groq_api_key:
        return normalize_transcript(None, text)

    client = Groq(api_key=settings.groq_api_key)
    prompt = (
        "Transforme cette transcription brute d'appel commercial en tours de parole. "
        "Utilise uniquement les speakers caller et client. Si tu n'es pas certain, "
        "fais au mieux avec le contexte. Ne change pas le fond.\n\n"
        "Reponds uniquement en JSON valide:\n"
        '{"conversation": [{"speaker": "caller", "text": "..."}, {"speaker": "client", "text": "..."}]}\n\n'
        f"Transcription brute:\n{text}"
    )
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": "Tu structures des transcripts d'appels. JSON uniquement."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_tokens=1800,
    )
    raw_content = str(response.choices[0].message.content or "").strip()
    parsed = parse_json_object(raw_content)
    conversation = parsed.get("conversation", [])
    return normalize_transcript(conversation if isinstance(conversation, list) else None, text)


def parse_json_object(raw_content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_content, re.S)
        if not match:
            raise
        parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("AI response must be a JSON object.")
    return parsed


def normalize_review_payload(payload: dict[str, Any]) -> dict[str, Any]:
    metrics_by_id = {
        str(metric.get("id", "")): metric
        for metric in payload.get("metrics", [])
        if isinstance(metric, dict)
    }
    metrics: list[dict[str, Any]] = []
    for definition in METRIC_DEFINITIONS:
        raw_metric = metrics_by_id.get(definition["id"], {})
        score = clamp_score(raw_metric.get("score", 0))
        metrics.append(
            {
                "id": definition["id"],
                "label": definition["label"],
                "score": score,
                "delta": str(raw_metric.get("delta") or "+0%"),
                "comment": str(raw_metric.get("comment") or "").strip(),
            }
        )

    average_score = round(sum(metric["score"] for metric in metrics) / len(metrics))
    global_score = clamp_score(payload.get("global_score", average_score))
    strengths = payload.get("strengths", [])
    if not isinstance(strengths, list):
        strengths = []

    return {
        "global_score": global_score,
        "summary": str(payload.get("summary") or "Analyse terminee.").strip(),
        "strengths": [str(item).strip() for item in strengths if str(item).strip()][:2],
        "improvement_focus": str(payload.get("improvement_focus") or "").strip(),
        "metrics": metrics,
    }


def clamp_score(value: Any) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, score))
