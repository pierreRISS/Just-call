# Mobile

Expo + React Native + TypeScript mobile app connected to the FastAPI todo API.

## Setup

```bash
npm install
cp .env.example .env
npm run start:lan
```

## API URL

The mobile app reads `EXPO_PUBLIC_API_URL`.

Defaults:

- Android emulator: `http://10.0.2.2:8000`
- iOS simulator and web: `http://localhost:8000`

For a real phone on the same Wi-Fi, use your computer LAN IP:

```text
EXPO_PUBLIC_API_URL=http://192.168.x.x:8000
```

Start the backend with a network host so the phone can reach it:

```bash
cd ../backend
uv run uvicorn app.main:app --host 0.0.0.0 --reload
```

Then start Expo in LAN mode:

```bash
cd ../mobile
npm run start:lan
```
