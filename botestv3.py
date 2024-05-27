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

# Charger les catégories à partir du fichier JSON contenant les produits
def load_categories_from_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            categories = set()
            for product in data:
                categories.add(product['categorie'])
            return list(categories)
    except Exception as e:
        logging.error(f"Erreur lors de la lecture du fichier JSON : {e}")
        return []

# Charger les catégories à partir du fichier JSON contenant les produits
categories = load_categories_from_json('products.json')

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

##FUNCTIONS##
###HELP###

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


###PROFILS###
def create_profile_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_nom = types.InlineKeyboardButton("Modifier Nom 👤", callback_data="modifier.nom")
    btn_prenom = types.InlineKeyboardButton("Modifier Prénom 🧑", callback_data="modifier.prenom")
    btn_quartier = types.InlineKeyboardButton("Modifier Quartier 🏘️", callback_data="modifier.quartier")
    btn_email = types.InlineKeyboardButton("Modifier Email 📧", callback_data="modifier.email")
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

###CATEGORIES###

def recuperer_produits_par_categorie(categorie):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produits WHERE categorie = %s", (categorie,))
        produits = cursor.fetchall()
        cursor.close()
        return produits
    except mysql.connector.Error as e:
        logging.error(f"Erreur lors de la récupération des produits par catégorie : {e}")
        return []
    


def get_products_by_category(category):
    try:
        cursor = conn.cursor()
        query = "SELECT nom, description, prix_unitaire FROM produits WHERE categorie = %s"
        cursor.execute(query, (category,))
        products = cursor.fetchall()
        cursor.close()
        return products
    except (mysql.connector.Error, Exception) as error:
        print("Erreur lors de la récupération des produits par catégorie :", error)
        return None


# Fonction pour récupérer les informations d'un produit par son nom depuis la base de données
def get_product_by_name(product_name):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produits WHERE nom = %s", (product_name,))
        product = cursor.fetchone()
        cursor.close()
        return product
    except mysql.connector.Error as e:
        logging.error(f"Erreur lors de la récupération du produit depuis la base de données : {e}")
        return None



def get_product_images(product_name):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT image1, image2, image3 FROM produits WHERE nom = %s", (product_name,))
        images = cursor.fetchall()
        cursor.close()

        base_path = r"Pictures/"  # Chemin de base de votre serveur local
    except (Exception, mysql.connector.Error) as error:
        print("erreur lors de la recuperation de l'image du produit:", error)

    return [os.path.join(base_path, image[0]) for image in images]


###CART###

def add_product_to_cart(user_id, product_name):
    try:
        if user_id in user_carts:
            cart = user_carts[user_id]
            if product_name in cart:
                cart[product_name] += 1
            else:
                cart[product_name] = 1
        else:
            user_carts[user_id] = {product_name: 1}
    except Exception as e:
        print("Une erreur est survenue lors de l'ajout du produit au panier :", e)


def create_cart_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_payer = types.InlineKeyboardButton("Payer", callback_data="payer")
    btn_vider = types.InlineKeyboardButton("Vider le panier", callback_data="vider_panier")
    btn_retour = types.InlineKeyboardButton("Retour", callback_data="retour_categories")
    keyboard.add(btn_payer, btn_vider, btn_retour)
    return keyboard


def clear_cart(user_id):
    if user_id in user_carts:
        user_carts[user_id] = {}


###COURSE###



# Fonction pour récupérer les informations du client
def get_client_info(client_id):
    conn = DatabaseConnection().conn
    try:
        cursor = conn.cursor()
        query = "SELECT nom, prenom, email FROM clients WHERE id_client = %s"
        cursor.execute(query, (client_id,))
        client_info = cursor.fetchall()
        
        if not client_info:
            # Supposons que vous avez une méthode pour obtenir les informations de l'utilisateur Telegram
            user_info = get_user_info_from_telegram_id(client_id)
            if user_info:
                nom = user_info.get('first_name', '')
                prenom = user_info.get('last_name', '')
                
                # Enregistrer les informations dans la base de données
                insert_query = "INSERT INTO clients (id_client, nom, prenom) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (client_id, nom, prenom))
                conn.commit()
                
                return {
                    "nom": nom,
                    "prenom": prenom,
                    "email": None  # Ajoutez le champ email si vous récupérez cette information
                }
            else:
                return None  # Impossible de récupérer les informations de l'utilisateur
        else:
            return {
                "nom": client_info[0][0],
                "prenom": client_info[0][1],
                "email": client_info[0][2]
            }
    except mysql.connector.Error as error:
        logging.error("Erreur lors de la récupération des informations du client : %s", error)
        return None
    


def get_user_info_from_telegram_id(user_id):
    try:
        # Utilisez get_user avec user_id
        user = bot.get_user(user_id)
        user_info = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name if user.last_name else '',
            'username': user.username if user.username else '',
            'is_bot': user.is_bot
            # Ajoutez d'autres informations que vous souhaitez récupérer
        }
        return user_info
    except telebot.apihelper.ApiException as e:
        error_message = "Une erreur s'est produite lors de la récupération des informations de l'utilisateur. Veuillez réessayer plus tard."
        print(error_message, e)
        return None    

def generate_cinetpay_payment_link(montant_depot, transaction_id, client_id):
    try:
        client_info = get_client_info(client_id)
        if client_info is None:
            logging.error("Impossible de récupérer les informations du client depuis la base de données.")
            return None
        
        numero_destinataire = "656958696"
        api_url = "https://api-checkout.cinetpay.com/v2/payment"
        amount = int(montant_depot)
        
        query_params = {
            "amount": amount,
            "currency": "XAF",
            "description": "Paiement de facture",
            "customer_name": client_info["nom"],
            "customer_surname": client_info["prenom"],
            "customer_phone_number": numero_destinataire,
            "return_url": "https://t.me/BEST_SELLER_UPbot",
            "notify_url": "https://t.me/BEST_SELLER_UPbot",
            "site_id": "607207",
            "transaction_id": transaction_id
        }
        
        query_params["apikey"] = CINETPAY_API_KEY
        
        response = requests.post(api_url, params=query_params)
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "payment_url" in data["data"]:
                return data["data"]["payment_url"]
        else:
            logging.error("Erreur lors de la génération du lien de paiement : %s, %s", response.text, response.status_code)
            return None
    except Exception as e:
        logging.error("Une erreur s'est produite lors de la génération du lien de paiement : %s", e)
        return None

def verify_cinetpay_transaction(transaction_id, site_id, apikey, expected_amount):
    try:
        url = "https://api-checkout.cinetpay.com/v2/payment/check"
        headers = {'Content-Type': 'application/json'}
        data = {
            "transaction_id": transaction_id,
            "site_id": site_id,
            "apikey": apikey
        }

        response = requests.post(url, json=data, headers=headers)
        response_json = response.json()

        if response_json.get("code") == "00" and response_json.get("data", {}).get("status") == "ACCEPTED":
            actual_amount = response_json.get("data", {}).get("amount")
            if actual_amount == expected_amount:
                return True
            else:
                print("Le montant de la transaction ne correspond pas.")
                return False
        else:
            return False

    except Exception as e:
        print("Erreur lors de la vérification de la transaction CinetPay:", e)
        return False

def save_course(commande_id, nom_expediteur, numero_expediteur, lieu_recuperation,
                lieu_livraison, description_colis, heure_ramassage, prix, photo_colis, choix_livraison, user_id, etat_course):
    global conn
    cursor = None
    try:
        if not conn.is_connected():
            conn.reconnect()

        cursor = conn.cursor()

        insert_query = """
            INSERT INTO courses (id_course, nom_expediteur, numero_expediteur,
            lieu_recuperation, lieu_livraison, description_colis, heure_ramassage, photo_colis, choix_livraison, prix, client_id, etat_course)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (
            commande_id, nom_expediteur, numero_expediteur, lieu_recuperation,
            lieu_livraison, description_colis, heure_ramassage, photo_colis, choix_livraison, prix, user_id, etat_course
        )

        cursor.execute(insert_query, data)
        conn.commit()
        logging.info("La course a été enregistrée avec succès.")

    except mysql.connector.Error as e:
        logging.error("Erreur lors de l'enregistrement de la course : %s", e)
    except Exception as e:
        logging.error("Une erreur s'est produite lors de l'enregistrement de la course : %s", e)

    finally:
        if cursor is not None:
            cursor.close()


def verify_payment_status(transaction_id, expected_amount, user_id):
    for _ in range(2):
        if verify_cinetpay_transaction(transaction_id, "607207", CINETPAY_API_KEY, expected_amount):
            save_course(
                transaction_id, course_details[user_id]['nom_expediteur'], course_details[user_id]['numero_expediteur'],
                course_details[user_id]['lieu_recuperation'], course_details[user_id]['lieu_livraison'], 
                course_details[user_id]['description_colis'], course_details[user_id]['heure_ramassage'], 
                course_details[user_id]['prix'], "", "mobile", user_id, "confirmée"
            )
            bot.send_message(user_id, "Votre paiement a été confirmé et votre course a été enregistrée.")
            return
        time.sleep(60)
    bot.send_message(user_id, "Le paiement n'a pas été confirmé. Veuillez réessayer.")
















@bot.message_handler(func=lambda message: message.text.startswith("Quitter"))
def handle_quitter(message):
    user_id = message.from_user.id

    # Supprime le panier de l'utilisateur
    clear_cart(user_id)

    # Masque le menu des catégories
    markup = types.ReplyKeyboardRemove()

    # Affiche le message d'au revoir avec un texte plus convivial
    bot.reply_to(message, "Merci de votre visite ! Votre panier a été vidé. Pour commencer une nouvelle session, appuyez sur /start.", reply_markup=markup)



# Gère le bouton "Retour" depuis la sélection d'une catégorie
@bot.message_handler(func=lambda message: message.text == "Retour")
def handle_return_to_main_menu(message):
    handle_start(message)



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
def call_help(message):
    handle_help(message)

    

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
    if call.data.startswith("modifier."):
        field = call.data.split(".")[1]
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

@bot.message_handler(func=lambda message: message.text in categories)
def handle_category_selection(message):
    try:
        category = message.text
        # Récupère les produits de la catégorie sélectionnée depuis la base de données
        products = get_products_by_category(category)
        
        if products:
            # Crée un clavier en ligne pour afficher les boutons des produits
            markup = types.InlineKeyboardMarkup(row_width=1)
            for product in products:
                product_name = product[0]
                btn_product = types.InlineKeyboardButton(product_name, callback_data=f"product_{product_name}")
                markup.add(btn_product)

            # Envoie le message avec les boutons des produits
            bot.send_message(message.chat.id, "Sélectionnez un produit :", reply_markup=markup)

            # Enregistre la catégorie sélectionnée et les produits associés dans le dictionnaire user_carts
            user_id = message.from_user.id
            user_carts[user_id] = {'category': category, 'products': products}
        else:
            bot.send_message(message.chat.id, "Aucun produit trouvé dans cette catégorie.")
    except Exception as e:
        logging.error(f"Erreur lors de la sélection de la catégorie : {e}")
        bot.send_message(message.chat.id, "Une erreur est survenue lors de la sélection de la catégorie.")






## New Course Details ##
course_details = {}


@bot.message_handler(func=lambda message: message.text == "Course 🏃‍♂️")
def handle_course(message):
    user_id = message.from_user.id
    client_info = get_client_info(user_id)
    if client_info:
        course_details[user_id] = {
            'nom_expediteur': client_info['nom'],
            'numero_expediteur': client_info['telephone']
        }
        bot.send_message(message.chat.id, f"Nom de l'expéditeur : {client_info['nom']}\nNuméro de l'expéditeur : {client_info['telephone']}")
        bot.send_message(message.chat.id, "Entrez le nom du destinataire :")
        bot.register_next_step_handler(message, process_recipient_name)
    else:
        bot.send_message(message.chat.id, "Erreur lors de la récupération des informations de l'expéditeur. Veuillez réessayer.")

def process_recipient_name(message):
    user_id = message.from_user.id
    course_details[user_id]['destinataire_nom'] = message.text
    bot.send_message(message.chat.id, "Entrez le numéro du destinataire :")
    bot.register_next_step_handler(message, process_recipient_number)

def process_recipient_number(message):
    user_id = message.from_user.id
    course_details[user_id]['destinataire_numero'] = message.text
    bot.send_message(message.chat.id, "Entrez la description du colis :")
    bot.register_next_step_handler(message, process_description)

def process_description(message):
    user_id = message.from_user.id
    course_details[user_id]['description_colis'] = message.text
    bot.send_message(message.chat.id, "Entrez l'heure de ramassage :")
    bot.register_next_step_handler(message, process_pickup_time)

def process_pickup_time(message):
    user_id = message.from_user.id
    course_details[user_id]['heure_ramassage'] = message.text
    bot.send_message(message.chat.id, "Entrez le lieu de ramassage :")
    bot.register_next_step_handler(message, process_pickup_location)

def process_pickup_location(message):
    user_id = message.from_user.id
    course_details[user_id]['lieu_recuperation'] = message.text
    bot.send_message(message.chat.id, "Entrez le lieu de livraison :")
    bot.register_next_step_handler(message, process_delivery_location)

def process_delivery_location(message):
    user_id = message.from_user.id
    course_details[user_id]['lieu_livraison'] = message.text
    bot.send_message(message.chat.id, "Entrez l'heure de livraison :")
    bot.register_next_step_handler(message, process_delivery_time)

def process_delivery_time(message):
    user_id = message.from_user.id
    course_details[user_id]['heure_livraison'] = message.text
    bot.send_message(message.chat.id, "Voulez-vous ajouter une photo du colis ? (Oui/Non)")
    bot.register_next_step_handler(message, process_photo_choice)

def process_photo_choice(message):
    user_id = message.from_user.id
    choice = message.text.lower()
    if choice == "oui":
        bot.send_message(message.chat.id, "Veuillez envoyer la photo du colis.")
        bot.register_next_step_handler(message, process_photo)
    elif choice == "non":
        # Si l'utilisateur ne souhaite pas ajouter de photo
        course_details[user_id]['photo_colis'] = None
        bot.send_message(message.chat.id, "Récapitulatif de la commande :")
        recap = generate_order_recap(course_details[user_id])
        bot.send_message(message.chat.id, recap)
        # Vous pouvez ajouter ici des boutons inline pour modifier chaque information
        bot.send_message(message.chat.id, "Confirmez-vous cette commande ? (Oui/Non)")
        bot.register_next_step_handler(message, confirm_order)
    else:
        bot.send_message(message.chat.id, "Veuillez répondre par 'Oui' ou 'Non'.")
        bot.register_next_step_handler(message, process_photo_choice)

def process_photo(message):
    try:
        user_id = message.from_user.id
        if message.photo:
            photo_id = message.photo[-1].file_id
            photo_info = bot.get_file(photo_id)
            photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{photo_info.file_path}"
            course_details[user_id]['photo_colis'] = photo_url
            bot.send_message(message.chat.id, "Photo du colis ajoutée avec succès.")
            bot.send_message(message.chat.id, "Récapitulatif de la commande :")
            recap = generate_order_recap(course_details[user_id])
            bot.send_message(message.chat.id, recap)
            # Vous pouvez ajouter ici des boutons inline pour modifier chaque information
            bot.send_message(message.chat.id, "Confirmez-vous cette commande ? (Oui/Non)")
            bot.register_next_step_handler(message, confirm_order)
        else:
            bot.send_message(message.chat.id, "Vous n'avez pas envoyé de photo. Veuillez réessayer.")
            bot.register_next_step_handler(message, process_photo)
    except Exception as e:
        bot.send_message(message.chat.id, "Une erreur s'est produite lors du traitement de la photo. Veuillez réessayer.")
        bot.register_next_step_handler(message, process_photo)

def generate_order_recap(details):
    recap = f"Nom de l'expéditeur : {details['nom_expediteur']}\n"
    recap += f"Numéro de l'expéditeur : {details['numero_expediteur']}\n"
    recap += f"Nom du destinataire : {details['destinataire_nom']}\n"
    recap += f"Numéro du destinataire : {details['destinataire_numero']}\n"
    recap += f"Description du colis : {details['description_colis']}\n"
    recap += f"Heure de ramassage : {details['heure_ramassage']}\n"
    recap += f"Lieu de ramassage : {details['lieu_recuperation']}\n"
    recap += f"Lieu de livraison : {details['lieu_livraison']}\n"
    recap += f"Heure de livraison : {details['heure_livraison']}\n"
    recap += "Photo du colis : " + (details['photo_colis'] if details['photo_colis'] else "Non ajoutée") + "\n"
    return recap

def confirm_order(message):
    user_id = message.from_user.id
    choice = message.text.lower()
    if choice == "oui":
        commande_id = f"cmd_{int(time.time())}"
        details = course_details[user_id]
        
        # Récupérer le prix et le choix de livraison à partir des détails de la commande
        prix = details['prix']
        choix_livraison = details['choix_livraison']
        
        # Sauvegarde de la commande dans la base de données
        save_course(commande_id, details['nom_expediteur'], details['numero_expediteur'],
                    details['lieu_recuperation'], details['lieu_livraison'], details['description_colis'],
                    details['heure_ramassage'], prix, details['photo_colis'], choix_livraison, user_id, "en cours",
                    details['destinataire_nom'], details['destinataire_numero'])
        bot.send_message(message.chat.id, "Votre commande a été confirmée.")
        # Demande le mode de livraison
        bot.send_message(message.chat.id, "Veuillez choisir un mode de livraison :", reply_markup=generate_delivery_mode_keyboard())
    elif choice == "non":
        bot.send_message(message.chat.id, "Votre commande a été annulée.")
        course_details.pop(user_id, None)
    else:
        bot.send_message(message.chat.id, "Veuillez répondre par 'Oui' ou 'Non'.")
        bot.register_next_step_handler(message, confirm_order)


def generate_delivery_mode_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton("Livraison Rapide", callback_data="delivery_fast"),
                 types.InlineKeyboardButton("Livraison Éclair", callback_data="delivery_express"))
    return keyboard

@bot.callback_query_handler(func=lambda call: True)
def handle_delivery_mode(callback_query):
    user_id = callback_query.from_user.id
    mode = callback_query.data
    if mode == "delivery_fast":
        prix = 1500
    elif mode == "delivery_express":
        prix = 3000
    else:
        bot.answer_callback_query(callback_query.id, "Option de livraison non valide.", show_alert=True)
        return
    course_details[user_id]['prix'] = prix
    bot.send_message(callback_query.message.chat.id, "Veuillez choisir un mode de paiement :", reply_markup=generate_payment_mode_keyboard())

def generate_payment_mode_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton("Paiement Mobile", callback_data="payment_mobile"),
                 types.InlineKeyboardButton("Paiement en Cash", callback_data="payment_cash"))
    return keyboard

@bot.callback_query_handler(func=lambda call: True)
def handle_payment_mode(callback_query):
    user_id = callback_query.from_user.id
    mode = callback_query.data
    if mode == "payment_mobile":
        # Génération du lien de paiement
        payment_link = generate_cinetpay_payment_link(course_details[user_id]['prix'], f"cmd_{int(time.time())}", user_id)
        if payment_link:
            bot.send_message(callback_query.message.chat.id, f"Veuillez procéder au paiement en utilisant le lien suivant :\n{payment_link}")
        else:
            bot.send_message(callback_query.message.chat.id, "Une erreur s'est produite lors de la génération du lien de paiement. Veuillez réessayer.")
    elif mode == "payment_cash":
        bot.send_message(callback_query.message.chat.id, "Veuillez effectuer le paiement en espèces lors de la livraison.")
    else:
        bot.answer_callback_query(callback_query.id, "Option de paiement non valide.", show_alert=True)




try:
    while True:
        bot.polling(none_stop=True)
except KeyboardInterrupt:
    print("Arrêt du bot suite à une interruption manuelle.")
except Exception as e:
    print("Une erreur s'est produite lors de l'exécution du bot :", e)
