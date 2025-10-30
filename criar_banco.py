from main import app, db, User

def criar_banco_dados():
    with app.app_context():
        # Criar tabelas
        db.create_all()
        
        # Verificar se já existe admin
        admin_existente = User.query.filter_by(email="admin@unifecaf.com").first()
        if not admin_existente:
            # Criar usuário admin
            admin = User(
                nome="Administrador",
                email="admin@unifecaf.com",
                modo=1
            )
            admin.set_senha("admin123")
            
            db.session.add(admin)
            db.session.commit()
            print("✅ Banco criado com sucesso!")
            print("👤 Admin: admin@unifecaf.com / admin123")
        else:
            print("✅ Banco já existe!")

if __name__ == '__main__':
    criar_banco_dados()