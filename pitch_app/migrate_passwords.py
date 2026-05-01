"""
Script para migrar senhas em texto plano para bcrypt hash
Execute este script uma vez após o deploy para atualizar as senhas existentes
"""
import sys
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pitch_app.db import SessionLocal
from pitch_app.services.auth_service import hash_password
from sqlalchemy import text


def migrate_passwords():
    """Migrar senhas em texto plano para bcrypt hash"""
    db = SessionLocal()
    
    try:
        # Buscar todos os usuários
        users = db.execute(text("""
            SELECT id, username, password FROM users
        """)).fetchall()
        
        print(f"Encontrados {len(users)} usuários para migrar")
        
        for user in users:
            # Verificar se a senha já está hasheada (bcrypt hash começa com $2)
            if user.password.startswith('$2'):
                print(f"✓ Usuário '{user.username}' já tem senha hasheada")
                continue
            
            # Hashear a senha em texto plano
            hashed = hash_password(user.password)
            
            # Atualizar no banco
            db.execute(text("""
                UPDATE users
                SET password = :password
                WHERE id = :id
            """), {
                "password": hashed,
                "id": user.id
            })
            
            print(f"✓ Senha do usuário '{user.username}' migrada com sucesso")
        
        db.commit()
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 Iniciando migração de senhas...\n")
    migrate_passwords()

# Made with Bob
