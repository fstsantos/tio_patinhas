#!/usr/bin/env python
import sys
sys.path.insert(0, '/home/fst/workspace/finorg/src')

try:
    from db import SessionLocal
    print("Testando conexao com banco de dados...")
    session = SessionLocal()
    print("✓ Conexao estabelecida com sucesso!")
    session.close()
except Exception as e:
    print(f"✗ Erro na conexao: {e}")
    sys.exit(1)
