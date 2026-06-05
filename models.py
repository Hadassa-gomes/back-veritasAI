"""
models.py — Banco de dados SQLite com SQLAlchemy
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite local — sem configuração, arquivo gerado automaticamente
DATABASE_URL = "sqlite:///./veritais.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}   # necessário para SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Verification(Base):
    __tablename__ = "verifications"

    id           = Column(Integer, primary_key=True, index=True)
    input_type   = Column(String(10))              # "url" | "text" | "image"
    input_value  = Column(Text)                    # URL, texto ou nome do arquivo
    verdict      = Column(String(20))              # VERDADEIRO | FALSO | SUSPEITO | INCONCLUSIVO
    confidence   = Column(Integer, default=0)      # 0–100
    summary      = Column(Text)                    # Resumo em 1 frase
    analysis     = Column(Text)                    # Análise completa do Claude
    sources_found = Column(Text, default="[]")     # JSON: lista de fontes encontradas
    created_at   = Column(DateTime, default=datetime.now)


def init_db():
    """Cria as tabelas se não existirem."""
    Base.metadata.create_all(bind=engine)
