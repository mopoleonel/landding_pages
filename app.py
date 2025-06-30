import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv() # Charge les variables d'environnement du fichier .env

# Titre de l'application Streamlit
st.set_page_config(page_title="Générateur de Landing Page IA", layout="wide") # Utilisation de 'wide' pour un layout étendu

st.title("🚀 Générateur de Landing Page avec IA")
st.markdown("Décrivez la landing page que vous souhaitez, et notre IA la générera pour vous !")

# Création de deux colonnes pour l'interface
col1, col2 = st.columns([1, 2]) # La colonne de gauche (input) sera plus petite que celle de droite (aperçu)

with col1:
    st.header("Décrivez votre page")
    user_prompt = st.text_area(
        "Décrivez votre landing page ici (ex: 'Une landing page moderne et minimaliste pour un service de coaching en ligne, avec un bouton d'appel à l'action pour s'inscrire à une session gratuite, et des témoignages.')",
        height=250, # Augmentation de la hauteur pour une meilleure saisie
        placeholder="Décrivez le contenu, le style, les sections, et les appels à l'action de votre landing page..."
    )

    if st.button("Générer la Landing Page", type="primary"):
        if user_prompt:
            api_key = os.getenv('GEMINI_API_KEY')

            if not api_key:
                st.error("Erreur : La clé API Gemini (GEMINI_API_KEY) n'est pas configurée dans les variables d'environnement.")
                st.warning("Veuillez définir votre clé API en tant que variable d'environnement dans un fichier `.env` à la racine de votre projet.")
                st.stop()

            # Placeholder pour le message de chargement
            loading_message_placeholder = st.empty()
            loading_message_placeholder.info("Génération en cours... Veuillez patienter quelques instants. Cela peut prendre un certain temps.")
            
            try:
                gemini_prompt = f"""
                Générez le code HTML complet pour une landing page responsive et moderne en utilisant Tailwind CSS.
                Le contenu de la page doit être basé sur la description suivante :
                "{user_prompt}"

                Assurez-vous que le HTML inclut :
                1.  Une balise `<!DOCTYPE html>` et les balises `<html>`, `<head>`, `<body>`.
                2.  Le CDN de Tailwind CSS dans le `<head>`: `<script src="https://cdn.tailwindcss.com"></script>`.
                3.  Une balise `<meta name="viewport" content="width=device-width, initial-scale=1.0">`.
                4.  Un titre approprié dans la balise `<title>`.
                5.  Des sections claires (Hero, Fonctionnalités, Témoignages, Appel à l'action, Contact, Pied de page).
                6.  Des classes Tailwind CSS pour un design esthétique et responsive.
                7.  Des placeholders pour les images si nécessaire (e.g., https://placehold.co/800x500/A855F7/FFFFFF?text=Image).
                8.  Le HTML doit être valide et bien structuré.

                Ne générez PAS de JavaScript pour des fonctionnalités dynamiques (comme l'envoi de formulaire), sauf si c'est pour des animations CSS ou des interactions simples qui ne nécessitent pas de backend.
                Le code généré doit être UNIQUEMENT le HTML.
                """

                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": gemini_prompt}
                            ]
                        }
                    ]
                }

                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.post(api_url, headers=headers, data=json.dumps(payload))
                response.raise_for_status()

                result = response.json()

                generated_html = ""
                if result.get("candidates") and len(result["candidates"]) > 0 and \
                   result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts") and \
                   len(result["candidates"][0]["content"]["parts"]) > 0:
                    generated_html = result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    loading_message_placeholder.error("Désolé, je n'ai pas pu générer de contenu HTML. La réponse de l'API était inattendue.")
                    # st.json(result) # Optionnel: pour le débogage, décommenter si besoin
                    generated_html = "" # Assurez-vous que generated_html est vide en cas d'erreur
            
            except requests.exceptions.RequestException as e:
                loading_message_placeholder.error(f"Erreur lors de l'appel à l'API Gemini: {e}")
                st.error("Veuillez vérifier votre connexion Internet ou si votre clé API est valide et active.")
                generated_html = ""
            except json.JSONDecodeError:
                loading_message_placeholder.error("Erreur de décodage JSON de la réponse de l'API. La réponse n'est pas un JSON valide.")
                generated_html = ""
            except Exception as e:
                loading_message_placeholder.error(f"Une erreur inattendue est survenue: {e}")
                generated_html = ""
            finally:
                loading_message_placeholder.empty() # Efface le message de chargement une fois terminé
        else:
            st.warning("Veuillez saisir une description pour générer la landing page.")
            generated_html = "" # Assurez-vous que generated_html est vide si aucun prompt n'est fourni

        # Stocker le HTML généré dans la session d'état pour qu'il puisse être affiché par l'aperçu
        st.session_state.generated_html = generated_html
        st.session_state.show_preview = True # Flag pour indiquer que l'aperçu doit être affiché
    else:
        st.session_state.show_preview = False
        st.session_state.generated_html = ""


# Section de l'aperçu dans la deuxième colonne
with col2:
    st.header("Aperçu de la Landing Page")
    if "show_preview" in st.session_state and st.session_state.show_preview:
        if st.session_state.generated_html:
            st.success("Aperçu de la Landing Page générée :")
            st.components.v1.html(st.session_state.generated_html, height=800, scrolling=True)
        else:
            st.info("Aucun aperçu disponible. Veuillez générer une landing page.")
    else:
        st.info("Votre aperçu apparaîtra ici après la génération.")
