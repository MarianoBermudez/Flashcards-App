import json
import streamlit as st
from supabase import create_client, Client
import sys

def upload_data():
    """
    Script de una sola vez para leer flashcards.json y subirlo a Supabase.
    """
    
    # --- 1. Conectarse a Supabase ---
    print("Conectando a Supabase...")
    try:
        supabase_url = st.secrets["supabase"]["url"]
        supabase_key = st.secrets["supabase"]["key"]
        supabase: Client = create_client(supabase_url, supabase_key)
        print("¡Conexión exitosa!")
    except Exception as e:
        print(f"Error al conectar con Supabase. Asegúrate de que .streamlit/secrets.toml esté configurado.")
        print(f"Error: {e}")
        sys.exit(1) # Salir del script si falla la conexión

    # --- 2. Leer el archivo JSON local ---
    print("Leyendo 'flashcards.json'...")
    try:
        with open('flashcards.json', 'r', encoding='utf-8') as f:
            data_to_upload = json.load(f)
        
        if not isinstance(data_to_upload, list):
             print("Error: El JSON no es una lista de tarjetas.")
             sys.exit(1)
             
        print(f"Se encontraron {len(data_to_upload)} tarjetas para subir.")
        
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'flashcards.json' en este directorio.")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el JSON: {e}")
        sys.exit(1)

    # --- 3. Subir los datos a Supabase ---
    # Usamos .insert() con la lista completa. 
    # Supabase es lo suficientemente inteligente para manejarlo como un lote.
    print("Iniciando subida a la tabla 'flashcards'...")
    try:
        response = supabase.table("flashcards").insert(data_to_upload).execute()
        
        # 'response.data' contendrá los datos insertados
        if response.data:
            print(f"¡ÉXITO! Se subieron {len(response.data)} tarjetas a Supabase.")
        else:
            print("La subida se completó, pero Supabase no devolvió datos. Revisa la tabla.")
            if response.error:
                print(f"Error de Supabase: {response.error}")

    except Exception as e:
        print(f"Error durante la subida a Supabase: {e}")
        
if __name__ == "__main__":
    upload_data()