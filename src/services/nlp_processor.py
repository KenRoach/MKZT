from typing import Dict, List, Tuple
import spacy
from textblob import TextBlob
from fuzzywuzzy import fuzz
from src.utils.logger import logger

class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("es_core_news_md")
        self.intent_patterns = {
            "order": ["quiero", "pedir", "ordenar", "llevar", "comprar"],
            "menu": ["menú", "carta", "opciones", "platos", "postres"],
            "payment": ["pagar", "yappy", "tarjeta", "efectivo"],
            "location": ["dirección", "ubicación", "donde", "lugar"],
            "status": ["estado", "tiempo", "cuánto falta", "dónde está"],
            "complaint": ["problema", "mal", "error", "queja", "frío", "caliente"],
            "gratitude": ["gracias", "excelente", "bueno", "genial"]
        }

    async def analyze_message(self, message: str) -> Dict:
        """Analyze message for intent, sentiment, and entities"""
        doc = self.nlp(message.lower())
        blob = TextBlob(message)
        
        return {
            "intent": await self._detect_intent(doc),
            "sentiment": blob.sentiment.polarity,
            "entities": await self._extract_entities(doc),
            "urgency": await self._detect_urgency(doc),
            "formality": await self._analyze_formality(doc)
        }

    async def _detect_intent(self, doc) -> Dict[str, float]:
        """Detect multiple possible intents with confidence scores"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            max_score = max(fuzz.partial_ratio(doc.text, pattern) for pattern in patterns)
            if max_score > 60:  # Threshold for intent detection
                intent_scores[intent] = max_score / 100
                
        return intent_scores

    async def _extract_entities(self, doc) -> List[Dict]:
        """Extract named entities and quantities"""
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
            
        # Extract quantities and products
        quantities = []
        products = []
        
        for token in doc:
            if token.like_num:
                quantities.append({
                    "number": token.text,
                    "next_word": token.nbor().text if token.i + 1 < len(doc) else None
                })
            elif token.pos_ == "NOUN":
                products.append(token.text)
                
        return {
            "named_entities": entities,
            "quantities": quantities,
            "products": products
        }

    async def _detect_urgency(self, doc) -> float:
        """Detect message urgency level"""
        urgency_words = {
            "urgente": 1.0,
            "rápido": 0.8,
            "pronto": 0.6,
            "ahora": 0.7,
            "inmediato": 0.9
        }
        
        max_urgency = 0.0
        for token in doc:
            if token.text.lower() in urgency_words:
                max_urgency = max(max_urgency, urgency_words[token.text.lower()])
                
        return max_urgency

    async def _analyze_formality(self, doc) -> float:
        """Analyze message formality level"""
        formal_indicators = ["por favor", "gracias", "cordialmente", "usted"]
        informal_indicators = ["oye", "hey", "dale", "ok"]
        
        formal_count = sum(1 for phrase in formal_indicators if phrase in doc.text.lower())
        informal_count = sum(1 for phrase in informal_indicators if phrase in doc.text.lower())
        
        total = formal_count + informal_count
        if total == 0:
            return 0.5  # Neutral formality
            
        return formal_count / total

nlp_processor = NLPProcessor() 