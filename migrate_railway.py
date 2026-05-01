#!/usr/bin/env python3
"""
Script para executar migrações no Railway
Execute este script uma vez após o deploy para adicionar as colunas necessárias
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from pitch_app.db import migrate_db, init_db

if __name__ == "__main__":
    print("🔄 Iniciando migrações do banco de dados...")
    
    try:
        # Inicializa o banco (cria tabelas se não existirem)
        print("📦 Inicializando banco de dados...")
        init_db()
        print("✅ Banco inicializado")
        
        # Executa migrações (adiciona colunas faltantes)
        print("🔧 Executando migrações...")
        migrate_db()
        print("✅ Migrações concluídas com sucesso!")
        
        print("\n✨ Banco de dados atualizado!")
        print("Agora você pode usar a funcionalidade de reset de senha.")
        
    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
