import streamlit_authenticator as stauth

print("=== Generador de Contraseñas Hasheadas ===\n")

password = input("Ingresa la contraseña a hashear: ")

# Intentar con la nueva API primero
try:
    # API nueva (v0.3+)
    hashed = stauth.Hasher.hash(password)
    print(f"\n✅ Hash generado (copia esto en secrets.toml):")
    print(hashed)
except AttributeError:
    try:
        # API intermedia (v0.2+)
        hashed = stauth.Hasher([password]).generate()[0]
        print(f"\n✅ Hash generado (copia esto en secrets.toml):")
        print(hashed)
    except:
        # API antigua (v0.1)
        from passlib.hash import bcrypt
        hashed = bcrypt.hash(password)
        print(f"\n✅ Hash generado (copia esto en secrets.toml):")
        print(hashed)
