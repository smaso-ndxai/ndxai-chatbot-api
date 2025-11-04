# 🤖 NdxAI ChatBot API

Backend API per al ChatBot de NdxAI utilitzant OpenAI GPT-4o-mini i FastAPI.

## 🚀 Deploy a Railway

### Configuració ràpida

1. **Connecta el repositori a Railway**
   - Ves a https://railway.app
   - Login amb GitHub
   - New Project → Deploy from GitHub repo
   - Selecciona aquest repo

2. **Afegeix variables d'entorn**
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
   ```

3. **Deploy automàtic**
   - Railway detecta automàticament Python i FastAPI
   - El deploy es fa automàticament

### URL del Backend

Després del deploy, Railway et donarà una URL:
```
https://xxx.up.railway.app
```

## 🧪 Testing local

```bash
# Instal·lar dependències
pip install -r requirements.txt

# Crear .env
echo "OPENAI_API_KEY=sk-proj-xxxxx" > .env

# Executar
uvicorn main:app --reload --port 3001
```

Prova: http://localhost:3001/api/health

## 📡 Endpoints

- `GET /` - Info de l'API
- `GET /api/health` - Health check
- `POST /api/chat` - Endpoint del chatbot

## 🔒 Seguretat

- ✅ CORS configurat per www.ndxai.eu
- ✅ Rate limiting (15 peticions/minut)
- ✅ Validació de peticions
- ✅ Gestió d'errors

## 💰 Costos

**GPT-4o-mini** és molt econòmic:
- ~$0.0003 per conversa
- 1000 converses ≈ $0.30

## 📚 Documentació

OpenAI API: https://platform.openai.com/docs
