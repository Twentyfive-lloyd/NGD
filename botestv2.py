import base64
import hashlib
import telebot
from telebot import types
import mysql.connector
import json
import os
import pyzbar
from PIL import Image, ImageDraw, ImageFont
import io
import random
import requests
from telebot.apihelper import ApiException
import datetime
import threading
import time
import qrcode
import configparser
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import database_connection
import re
from database_connection import DatabaseConnection
from config import TOKEN, CINETPAY_API_KEY

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Token API Telegram
config = configparser.ConfigParser()
config.read('config.ini')

DATABASE_HOST = config['DATABASE']['HOST']
DATABASE_USER = config['DATABASE']['USER']
DATABASE_PASSWORD = config['DATABASE']['PASSWORD']
DATABASE_NAME = config['DATABASE']['NAME']



# Fonction pour charger les catégories à partir du fichier JSON
def load_categories_from_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            categories = set()
            for product in data:
                categories.add(product['categorie'])
            return list(categories)
    except Exception as e:
        logging.error(f"Erreur lors de la lecture du fichier JSON : {e}")
        return []





conn = database_connection.connect_to_database()

if conn is not None:
    logging.info("Connexion à la base de données établie avec succès.")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        logging.info(f"Version de la base de données : {version}")
        cursor.close()
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution d'une requête : {e}")
else:
    logging.error("La connexion à la base de données a échoué.")



bot = telebot.TeleBot(TOKEN)



user_carts = {}
command_info = {}



@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        btn_acheter = types.KeyboardButton("Acheter 🛍️")
        btn_scanner_qr = types.KeyboardButton("Scanner QR code 📷")
        btn_panier = types.KeyboardButton("🛒 Voir Panier")
        btn_aide = types.KeyboardButton("Aide ℹ️")
        btn_contact = types.KeyboardButton("Contactez-nous ☎️")
        btn_course = types.KeyboardButton("Course 🏃‍♂️")
        btn_quitter = types.KeyboardButton("Quitter ❌")
        btn_gestion_profil = types.KeyboardButton("Gestion du profil 📋")
        markup.add(btn_acheter, btn_scanner_qr, btn_panier, btn_aide, btn_contact, btn_quitter, btn_gestion_profil, btn_course)

        bot.send_message(message.chat.id, "🌟 Bienvenue sur notre service d'achat en ligne! 🌟\n\n" \
                         "Pour démarrer, voici ce que vous pouvez faire:\n\n" \
                         "1️⃣ Enregistrez vos informations pour une expérience d'achat plus rapide et facile.\n" \
                         "2️⃣ Parcourez nos produits et appuyez sur 'Acheter' pour ajouter des articles à votre panier.\n" \
                         "3️⃣ Lorsque vous avez terminé, confirmez votre commande en scannant le QR code.\n\n" \
                         "Si vous avez besoin d'aide ou d'assistance, n'hésitez pas à nous contacter!", reply_markup=markup)
    except Exception as e:
        logging.error(f"Erreur lors de la gestion de la commande start : {e}")



@bot.message_handler(func=lambda message: message.text == "Aide ℹ️")
def handle_help(message):
    try:
        help_text = "🌟 Bienvenue sur notre service d'achat en ligne! 🌟\n\n" \
                    "🛍️ Pour passer une commande, appuyez sur le bouton 'Acheter'.\n" \
                    "💾 Vous pouvez enregistrer vos informations en utilisant le bouton 'Enregistrer'.\n" \
                    "📷 Confirmez la livraison en scannant le QR code de votre commande.\n\n" \
                    "☎️ Pour toute assistance supplémentaire, n'hésitez pas à nous contacter en utilisant le bouton 'Contactez-nous'."

        bot.send_message(message.chat.id, help_text)
    except Exception as e:
        logging.error(f"Erreur lors de la gestion de la commande help : {e}")



def create_profile_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_nom = types.InlineKeyboardButton("Modifier Nom 👤", callback_data="modifier_nom")
    btn_prenom = types.InlineKeyboardButton("Modifier Prénom 🧑", callback_data="modifier_prenom")
    btn_quartier = types.InlineKeyboardButton("Modifier Quartier 🏘️", callback_data="modifier_quartier")
    btn_email = types.InlineKeyboardButton("Modifier Email 📧", callback_data="modifier_email")
    keyboard.add(btn_nom, btn_prenom, btn_quartier, btn_email)
    return keyboard



def get_user_info(user_id):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients WHERE id_client = %s", (user_id,))
        user_info = cursor.fetchone()
        cursor.close()
        return user_info
    except mysql.connector.Error as e:
        logging.error(f"Erreur de connexion à MySQL : {e}")
        return None



def update_user_info(user_id, field, value):
    try:
        cursor = conn.cursor()
        query = f"UPDATE clients SET {field} = %s WHERE id_client = %s"
        cursor.execute(query, (value, user_id))
        conn.commit()
        cursor.close()
    except mysql.connector.Error as e:
        logging.error(f"Erreur de connexion à MySQL : {e}")



user_steps = {}



@bot.message_handler(func=lambda message: message.text == "Gestion du profil 📋")
def gestion_du_profil(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    if user_info:
        info_msg = (f"📋 Informations de votre profil :\n"
                    f"👤 Nom : {user_info['nom']}\n"
                    f"🧑 Prénom : {user_info['prenom']}\n"
                    f"🏘️ Quartier : {user_info['quartier']}\n"
                    f"📞 Téléphone : {user_info['telephone']}\n"
                    f"📧 Email : {user_info['email']}")
    else:
        info_msg = "❌ Aucune information trouvée pour votre profil."

    bot.send_message(message.chat.id, info_msg, reply_markup=create_profile_keyboard())



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.from_user.id
    if call.data.startswith("modifier_"):
        field = call.data.split("_")[1]
        user_steps[user_id] = field
        bot.send_message(call.message.chat.id, f"Veuillez entrer votre nouveau {field} :")
        bot.register_next_step_handler(call.message, process_field_update)



def process_field_update(message):
    user_id = message.from_user.id
    if user_id in user_steps:
        field = user_steps[user_id]
        value = message.text
        update_user_info(user_id, field, value)
        bot.send_message(message.chat.id, f"Votre {field} a été mis à jour avec succès.")
        del user_steps[user_id]
    else:
        bot.send_message(message.chat.id, "Erreur : Veuillez réessayer.")





@bot.message_handler(func=lambda message: message.text == "Acheter 🛍️")
def handle_acheter(message):
    try:
        # Charger les catégories à partir du fichier JSON contenant les produits
        categories = load_categories_from_json('products.json')
        markup = types.ReplyKeyboardMarkup(row_width=2)
        for category in categories:
            btn_category = types.KeyboardButton(category)
            markup.add(btn_category)
        btn_retour = types.KeyboardButton("Retour")
        markup.add(btn_retour)

        bot.send_message(message.chat.id, "Sélectionnez une catégorie :", reply_markup=markup)
    except Exception as e:
        logging.error(f"Erreur lors de la gestion du message 'Acheter' : {e}")



@bot.message_handler(func=lambda message: message.text == "Retour")
def handle_mmenu(message):
    handle_start(message)



try:
    while True:
        bot.polling(none_stop=True)
except KeyboardInterrupt:
    print("Arrêt du bot suite à une interruption manuelle.")
except Exception as e:
    print("Une erreur s'est produite lors de l'exécution du bot :", e)

