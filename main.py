from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

# CORS - Canvia els origins pel teu domini de GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.ndxai.eu",     # Domini principal
        "https://ndxai.eu",         # Domini sense www
        "http://localhost:5173",    # Desenvolupament local
        "http://localhost:4173",    # Preview local
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Inicialitzar client d'OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Rate limiting simple
rate_limit_data = defaultdict(list)
RATE_LIMIT = 15  # màxim 15 peticions
RATE_WINDOW = timedelta(minutes=1)  # per minut


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    language: str = "es"


def check_rate_limit(ip: str) -> bool:
    """Comprova si l'IP ha superat el rate limit"""
    now = datetime.now()
    
    # Filtrar peticions dins la finestra de temps
    rate_limit_data[ip] = [
        timestamp for timestamp in rate_limit_data[ip]
        if now - timestamp < RATE_WINDOW
    ]
    
    if len(rate_limit_data[ip]) >= RATE_LIMIT:
        return False
    
    rate_limit_data[ip].append(now)
    return True


def get_system_prompt(language: str) -> str:
    """Genera el system prompt segons l'idioma"""
    lang = {
        'ca': 'català',
        'es': 'español',
        'en': 'English'
    }.get(language, 'español')
    
    return f"""Ets un assistent d'IA útil per a Neural Dynamics AI (NdxAI), una empresa especialitzada en solucions d'Intel·ligència Artificial per a la indústria.

IMPORTANT: Has de respondre NOMÉS en {lang}, independentment de l'idioma en què l'usuari escrigui.

Sobre NdxAI:
- Som experts en Intel·ligència Artificial per a la indústria
- Ubicació: Vic, Barcelona
- Contacte: info@ndxai.eu, +34696978421
- LinkedIn: @neural-dynamics-ai

Els nostres serveis:

1. **Manteniment Predictiu**: Utilitzem dades històriques i models d'IA per predir fallades abans que passin, reduint costos de manteniment i evitant interrupcions inesperades a la producció.

2. **Visió Artificial**: Models d'IA que inspeccionen productes amb precisió superior a la humana, detectant defectes microscòpics en línies de producció, assegurant estàndards de qualitat consistents.

3. **Bessó Digital**: Rèpliques virtuals de les operacions físiques que permeten simular canvis, provar millores i predir resultats sense aturar la producció.

4. **Bots i Assistents d'IA**: Assistents virtuals intel·ligents per a webs, apps, consultes d'informació interna i suport a clients, automatitzant tasques repetitives.

5. **Analítica Avançada**: Convertim les dades de l'empresa en avantatge competitiu mitjançant IA i Machine Learning - previsió de vendes, optimització d'inventaris, segmentació de clients, preus dinàmics.

6. **Automatització Intel·ligent**: Sistemes d'IA que automatitzen processos repetitius i administratius, reduint errors i alliberant temps valuós per a tasques estratègiques.

El nostre equip inclou experts en:
- Sergi Masó (Analista de Dades)
- Iker Reina (Arquitecte de Ciberseguretat i Infraestructura Cloud)
- Gil Prat (Enginyer Full Stack)
- Mariona Forcada (Enginyera de Dades)
- Carlo Manzo (Científic de Dades)

El teu rol:
- Respondre preguntes sobre els serveis de NdxAI
- Explicar com la IA pot ajudar les empreses segons les seves necessitats específiques
- Proporcionar informació sobre l'empresa
- Ser útil, professional i concís
- Si et pregunten sobre coses fora de l'àmbit de NdxAI, redirigeix educadament cap als serveis de l'empresa
- Respón SEMPRE en {lang}

Mantingues les respostes breus (2-3 paràgrafs màxim) i amb recomanacions accionables."""


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "model": "gpt-4o-mini"
    }


@app.post("/api/chat")
async def chat(request: Request, chat_request: ChatRequest):
    """Endpoint principal del chatbot"""
    
    # Obtenir IP del client
    client_ip = request.client.host
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again in a minute."
        )
    
    try:
        # Validació
        if not chat_request.messages:
            raise HTTPException(
                status_code=400,
                detail="Messages array cannot be empty"
            )
        
        # Limitar l'històric per evitar costos excessius (últims 8 missatges)
        limited_messages = chat_request.messages[-8:]
        
        # Convertir a format d'OpenAI
        api_messages = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in limited_messages
        ]
        
        # Afegir el system prompt
        messages_with_system = [
            {
                "role": "system",
                "content": get_system_prompt(chat_request.language)
            }
        ] + api_messages
        
        # Crida a l'API d'OpenAI amb GPT-4o-mini
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_with_system,
            max_tokens=500,
            temperature=0.7,
        )
        
        return {
            "content": response.choices[0].message.content
        }
        
    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        
        # Errors específics d'OpenAI
        if "authentication" in error_message.lower() or "api_key" in error_message.lower():
            raise HTTPException(
                status_code=500,
                detail="Configuration error. Please contact support."
            )
        elif "rate_limit" in error_message.lower():
            raise HTTPException(
                status_code=429,
                detail="Service temporarily busy. Please try again shortly."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="An error occurred processing your request. Please try again."
            )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NdxAI ChatBot API",
        "version": "1.0.0",
        "model": "gpt-4o-mini",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat"
        }
    }


# Per executar localment: uvicorn main:app --reload --port 3001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
