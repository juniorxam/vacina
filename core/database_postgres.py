"""
database_postgres.py - Versão PostgreSQL para persistência em produção
"""

import os
import logging
from typing import Any, Dict, List, Optional, Sequence
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import streamlit as st

logger = logging.getLogger(__name__)


class PostgresDatabase:
    """
    Database manager para PostgreSQL (persistente no Streamlit Cloud)
    """
    
    def __init__(self, connection_string: str = None):
        """
        Inicializa conexão PostgreSQL
        
        Args:
            connection_string: String de conexão (ex: postgresql://user:pass@host/db)
        """
        if connection_string is None:
            # Tentar pegar dos secrets do Streamlit
            if hasattr(st, 'secrets') and 'postgresql' in st.secrets:
                connection_string = st.secrets['postgresql']['connection_string']
            else:
                connection_string = os.getenv('DATABASE_URL')
        
        if not connection_string:
            raise ValueError("String de conexão PostgreSQL não encontrada!")
        
        self.engine = create_engine(
            connection_string,
            poolclass=NullPool,  # Sem pooling para ambiente serverless
            echo=False
        )
        
        logger.info("Conectado ao PostgreSQL")
        self._init_schema()
    
    def _init_schema(self):
        """Inicializa schema no PostgreSQL"""
        with self.engine.connect() as conn:
            # Criar extensão UUID se não existir
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            
            # Tabela servidores
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS servidores (
                    id_comp TEXT PRIMARY KEY,
                    numfunc TEXT,
                    numvinc TEXT,
                    nome TEXT NOT NULL,
                    cpf TEXT UNIQUE,
                    data_nascimento DATE,
                    sexo TEXT,
                    cargo TEXT,
                    lotacao TEXT,
                    lotacao_fisica TEXT,
                    superintendencia TEXT,
                    telefone TEXT,
                    email TEXT,
                    data_admissao DATE,
                    tipo_vinculo TEXT,
                    situacao_funcional TEXT DEFAULT 'ATIVO',
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usuario_cadastro TEXT
                )
            """))
            
            # Tabela doses
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS doses (
                    id SERIAL PRIMARY KEY,
                    id_comp TEXT REFERENCES servidores(id_comp),
                    vacina TEXT NOT NULL,
                    tipo_vacina TEXT,
                    dose TEXT NOT NULL,
                    data_ap DATE NOT NULL,
                    data_ret DATE,
                    lote TEXT,
                    fabricante TEXT,
                    local_aplicacao TEXT,
                    via_aplicacao TEXT,
                    campanha_id INTEGER,
                    usuario_registro TEXT,
                    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id_comp, vacina, dose, data_ap)
                )
            """))
            
            # Tabela usuarios
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    login TEXT PRIMARY KEY,
                    senha TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    nivel_acesso TEXT CHECK(nivel_acesso IN ('ADMIN', 'OPERADOR', 'VISUALIZADOR')),
                    lotacao_permitida TEXT,
                    ativo INTEGER DEFAULT 1,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Tabela logs
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usuario TEXT,
                    modulo TEXT,
                    acao TEXT,
                    detalhes TEXT,
                    ip_address TEXT
                )
            """))
            
            conn.commit()
            
            # Criar usuário admin se não existir
            self._ensure_admin()
    
    def _ensure_admin(self):
        """Garante que existe um usuário admin"""
        from config import CONFIG
        from core.security import Security
        
        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT login FROM usuarios WHERE login = :login"),
                {"login": CONFIG.admin_login}
            ).fetchone()
            
            if not result:
                senha_hash = Security.sha256_hex(CONFIG.admin_password)
                conn.execute(
                    text("""
                        INSERT INTO usuarios (login, senha, nome, nivel_acesso, lotacao_permitida, ativo)
                        VALUES (:login, :senha, :nome, 'ADMIN', 'TODOS', 1)
                    """),
                    {
                        "login": CONFIG.admin_login,
                        "senha": senha_hash,
                        "nome": "Administrador"
                    }
                )
                conn.commit()
                logger.info("Usuário admin criado")
    
    def execute(self, query: str, params: Dict = None) -> int:
        """Executa INSERT/UPDATE/DELETE"""
        with self.engine.begin() as conn:
            result = conn.execute(text(query), params or {})
            return result.rowcount
    
    def fetchone(self, query: str, params: Dict = None) -> Optional[Dict]:
        """Busca um registro"""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {}).mappings().first()
            return dict(result) if result else None
    
    def fetchall(self, query: str, params: Dict = None) -> List[Dict]:
        """Busca múltiplos registros"""
        with self.engine.connect() as conn:
            results = conn.execute(text(query), params or {}).mappings().all()
            return [dict(r) for r in results]
    
    def read_sql(self, query: str, params: Dict = None) -> pd.DataFrame:
        """Executa query e retorna DataFrame"""
        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params or {})
