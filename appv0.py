import base64
import hashlib
import telebot
from telebot import types
import mysql.connector
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
from database_connection import DatabaseConnection
from config import TOKEN, CINETPAY_API_KEY
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Token API Telegram
config = configparser.ConfigParser()
config.read('config.ini')
#CINETPAY_API_KEY = config['API_KEYS']['CINETPAY_API_KEY']
DATABASE_HOST = config['DATABASE']['HOST']
DATABASE_USER = config['DATABASE']['USER']
DATABASE_PASSWORD = config['DATABASE']['PASSWORD']
DATABASE_NAME = config['DATABASE']['NAME']
#TOKEN = config['API_KEYS']['TOKEN']


conn = database_connection.connect_to_database()

if conn is not None:
    logging.info("Connexion à la base de données établie avec succès.")
    
    # Essayez d'exécuter une requête pour vérifier la connexion
    try:
        cursor = conn.cursor()
        # Exemple de requête (remplacez-la par votre propre requête)
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        logging.info(f"Version de la base de données : {version}")
        
        # Fermez le curseur après utilisation
        cursor.close()
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution d'une requête : {e}")
        # Autres actions en cas d'échec d'exécution de requête
else:
    logging.error("La connexion à la base de données a échoué.")
    # Autres actions en cas d'échec de connexion
    
# Crée l'instance du bot
bot = telebot.TeleBot(TOKEN)

# Dictionnaire pour stocker le panier de chaque utilisateur
user_carts = {}
command_info = {}


# Gère la commande /start
# Définissez la fonction pour le bouton d'aide
def handle_help(message):
    # Créez le texte d'aide avec des emojis
    help_text = "Bienvenue sur notre service d'achat en ligne! 🌟 Voici comment utiliser notre bot:\n\n" \
                "1️⃣ Enregistrez vos informations en utilisant le bouton 'Enregistrer les informations 💾'.\n" \
                "2️⃣ Achetez vos produits en appuyant sur 'Acheter 🛍️'.\n" \
                "3️⃣ Confirmez la livraison en scannant le QR code de votre commande avec 'Scanner QR code 📷'.\n\n" \
                "Pour toute autre question, n'hésitez pas à nous contacter en utilisant le bouton 'Contactez-nous ☎️'."

    # Créez le clavier personnalisé avec le bouton "Retour" pour revenir au menu principal
    markup = types.ReplyKeyboardMarkup(row_width=1)
    btn_retour = types.KeyboardButton("Retour ↩️")
    markup.add(btn_retour)

    # Envoyez le message d'aide avec le clavier personnalisé
    bot.send_message(message.chat.id, help_text, reply_markup=markup)

# Dans la fonction handle_start, ajoutez le bouton d'aide avec la fonction associée
@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn_acheter = types.KeyboardButton("Acheter 🛍️")
    btn_scanner_qr = types.KeyboardButton("Scanner QR code 📷")
    btn_panier = types.KeyboardButton("🛒 Voir Panier")
    btn_aide = types.KeyboardButton("Aide ℹ️")
    btn_contact = types.KeyboardButton("Contactez-nous ☎️")
    btn_course = types.KeyboardButton("Course 🏃‍♂️")
    btn_quitter = types.KeyboardButton("Quitter ❌")
    btn_enregistrer = types.KeyboardButton("Enregistrer les informations 💾") 
    #btn_who = types.KeyboardButton("Qui sommes-nous ?") 
    markup.add(btn_acheter, btn_scanner_qr, btn_panier, btn_aide, btn_contact, btn_quitter, btn_enregistrer, btn_course)
    bot.send_message(message.chat.id, "Bienvenue sur notre service d'achat en ligne! 🌟 Voici comment utiliser notre bot:\n\n" \
                "1️⃣ Enregistrez vos informations en utilisant le bouton 'Enregistrer les informations 💾'.\n" \
                "2️⃣ Achetez vos produits en appuyant sur 'Acheter 🛍️'.\n" \
                "3️⃣ Confirmez la livraison en scannant le QR code de votre commande avec 'Scanner QR code 📷'.\n\n" \
                "Pour toute autre question, n'hésitez pas à nous contacter en utilisant le bouton 'Contactez-nous ☎️'.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Qui sommes-nous ?")
def handle_who_we_are(message):
    video_path = get_spot_video()

    if video_path:
        # Envoyer la vidéo spot
        with open(video_path, 'rb') as video:
            bot.send_video(message.chat.id, video)
    else:
        bot.send_message(message.chat.id, "Désolé, la vidéo spot n'est pas disponible pour le moment.")


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
            
# Fonction de démarrage de la commande de livraison
@bot.message_handler(func=lambda message: message.text.startswith("Course"))
def handle_coursew(message):
    bot.reply_to(message, "Veuillez saisir le nom complet de votre client/structure :")
    bot.register_next_step_handler(message, process_nom_expediteur)

photo_colis = None
# Fonction de traitement du nom complet de l'expéditeur
def process_nom_expediteur(message):
    global nom_expediteur
    nom_expediteur = message.text
    bot.reply_to(message, "Veuillez saisir le numero du client/structure :")
    bot.register_next_step_handler(message, process_numero_expediteur)


# Fonction de traitement du numéro de téléphone de l'expéditeur
def process_numero_expediteur(message):
    global numero_expediteur
    numero_expediteur = message.text
    bot.reply_to(message, "Veuillez choisir le lieu de ramassage du colis :")
    bot.register_next_step_handler(message, process_ramassage)

# Fonction de traitement du numéro de téléphone du destinataire
def process_ramassage(message):
    global lieu_recuperation
    lieu_recuperation = message.text
    bot.reply_to(message, "Veuillez choisir le lieu de livraison du colis :",reply_markup=create_location_keyboard("Recuperation"))
    bot.register_next_step_handler(message, process_lieu_livraison)


# Création du clavier pour le choix du lieu (Récupération ou Livraison)
def create_location_keyboard(location_type):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    if location_type == "Recuperation":
        locations = ["Yaounde I", "Yaounde II", "Yaounde III", "Yaounde IV", "Yaounde V", "Yaounde VI", "Yaounde VII"]
    elif location_type == "Livraison":
        locations = ["Yaounde I", "Yaounde II", "Yaounde III", "Yaounde IV", "Yaounde V", "Yaounde VI", "Yaounde VII"
                     
                     ]  # Mettez ici vos lieux de livraison
    else:
        locations = []  # Au cas où le type de lieu n'est pas reconnu, pas de boutons affichés
    for location in locations:
        markup.add(types.KeyboardButton(location))
    return markup


# Fonction de traitement du lieu de livraison du colis
def process_lieu_livraison(message):
    global lieu_livraison
    lieu_livraison = message.text
    bot.send_message(message.chat.id, "Veuillez entrer une heure de ramassage :")
    bot.register_next_step_handler(message, process_heure_ramssage)

# Fonction de traitement du lieu de récupération du colis
def process_heure_ramssage(message):
    global heure_ramassage
    heure_ramassage = message.text
    bot.send_message(message.chat.id, "Veuillez entrer une description du colis :")
    bot.register_next_step_handler(message, process_description_colis)

# Fonction de traitement de la description du colis
def process_description_colis(message):
    global description_colis
    description_colis = message.text
     # Envoyer le message avec le clavier Oui/Non
    bot.reply_to(message, "Voulez-vous ajouter une photo de votre colis ?", reply_markup=create_yes_no_keyboard())
    bot.register_next_step_handler(message, process_user_choice)

def create_yes_no_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("Oui"), types.KeyboardButton("Non"))
    return markup

# Fonction pour traiter le choix de l'utilisateur (Oui/Non)
def process_user_choice(message):
    global photo_colis
    if message.text.lower() == 'oui':
        bot.reply_to(message, "Veuillez envoyer une photo du colis :")
        bot.register_next_step_handler(message, process_photo_colis)
    elif message.text.lower() == 'non': 
        photo_colis = None       
        send_colis_info(message)
    else:
        bot.reply_to(message, "Choix non valide. Veuillez choisir Oui ou Non.")
        bot.register_next_step_handler(message, process_user_choice)

# Fonction pour traiter la photo du colis
def process_photo_colis(message):
    global photo_colis
    if message.photo:
        photo_colis = message.photo[-1].file_id
        
        bot.send_photo(message.chat.id, photo_colis)
        send_colis_info(message)
        photo_colis = photo_colis = message.photo[-1]
    else:
        bot.reply_to(message, "Veuillez envoyer une photo valide du colis.")
        bot.register_next_step_handler(message, process_photo_colis)



# Fonction pour envoyer les informations du colis
def send_colis_info(message):
    global description_colis, nom_expediteur, heure_ramassage, lieu_recuperation, lieu_livraison
    bot.reply_to(message,
                 f"Voulez-vous livrer ce colis ?\n"
                 f"Description : {description_colis}\n"
                 f"Expéditeur : {nom_expediteur}\n"
                 f"Heure de ramassage : {heure_ramassage}\n"
                 f"Lieu de ramassage : {lieu_recuperation}\n"
                 f"Lieu de livraison : {lieu_livraison}",
                 reply_markup=create_delivery_options())
# Création du clavier pour les options de livraison
def create_delivery_options():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(types.KeyboardButton("Livraison Standard"), types.KeyboardButton("Livraison Express"))
    return markup

# Fonction de traitement du choix de livraison (message_handler)
@bot.message_handler(func=lambda message: message.text in ["Livraison Standard", "Livraison Express"])
def handle_delivery_choice(message):
    global choix_livraison
    global montant_livraison
    
    choix_livraison = message.text
    if choix_livraison == "Livraison Standard":
        id_recu = random.randint(100000, 999999)
        montant_livraison = calculate_standard_delivery_price()
        lien_paiement = generate_cinetpay_payment_link(montant_livraison, id_recu, message.chat.id)
        #markup = telebot.types.ReplyKeyboardMarkup()
        #markup.row('Payer')
        bot.reply_to(message, f"ID de reçu : {id_recu}\nPrix de livraison : {montant_livraison} XAF\n\nNous sommes ravis de vous accompagner dans votre commande ! 🎉\n\nPour finaliser votre achat en toute sécurité, veuillez cliquer sur le bouton 'Payer' ci-dessous. Vous serez redirigé vers une page sécurisée pour effectuer votre paiement mobile. Merci pour votre confiance ! 😊", reply_markup=create_payment_link_button(lien_paiement))
    elif choix_livraison == "Livraison Express":
        id_recu = random.randint(100000, 999999)
        montant_livraison = calculate_express_delivery_price()
        #markup = telebot.types.ReplyKeyboardMarkup()
        #markup.row('Payer')
        lien_paiement = generate_cinetpay_payment_link(montant_livraison, id_recu, message.chat.id)
        bot.reply_to(message, f"Prix de livraison express : {montant_livraison} XAF\n\nNous sommes ravis de vous accompagner dans votre commande ! 🎉\n\nPour finaliser votre achat en toute sécurité, veuillez cliquer sur le bouton 'Payer' ci-dessous. Vous serez redirigé vers une page sécurisée pour effectuer votre paiement mobile. Merci pour votre confiance ! 😊", reply_markup=create_payment_link_button(lien_paiement))

# Calcul du prix de livraison standard en fonction des lieux
def calculate_standard_delivery_price():
    if lieu_recuperation == lieu_livraison:
        if "Yaounde VI" in [lieu_recuperation, lieu_livraison] or "Yaounde VII" in [lieu_recuperation, lieu_livraison]:
            return 2500
        else:
            return 1500
    else:
        return 1500

# Calcul du prix de livraison express en fonction des lieux
def calculate_express_delivery_price():
    if lieu_recuperation == lieu_livraison:
        return 2000
    elif "Yaounde VI" in [lieu_recuperation, lieu_livraison] or "Yaounde VII" in [lieu_recuperation, lieu_livraison]:
        return 3000
    else:
        return 2500

# Fonction pour créer un bouton de lien de paiement
def create_payment_link_button(url):
    markup = types.InlineKeyboardMarkup()
    payment_button = types.InlineKeyboardButton(text="Paiement Mobile", url=url)
    cash_payment_button = types.InlineKeyboardButton(text="Paiement en Cash", callback_data="cash_payment")
    markup.row(payment_button, cash_payment_button)
    return markup






# Fonction pour traiter le choix de paiement en cash
@bot.callback_query_handler(func=lambda call: call.data == "cash_payment")
def process_cash_payment(call):
    # Traitement du paiement


    user_id = call.message.chat.id
    global photo_exists
    # Récupération des informations nécessaires à partir des variables globales
    global nom_expediteur, choix_livraison, lieu_recuperation, lieu_livraison, montant_livraison, photo_colis

    # Vérification de l'existence de la photo du colis
    if photo_colis:
        photo_exists = True
    else:
        photo_exists = False

    # Enregistrement des informations nécessaires pour le traitement du paiement
    command_info[user_id] = {
        "id_recu": random.randint(100000, 999999),
        "nom_expediteur": nom_expediteur,
        #"nom_destinataire": nom_destinataire,
        "numero_expediteur": numero_expediteur,
        #"numero_destinataire": numero_destinataire,
        "lieu_recuperation": lieu_recuperation,
        "lieu_livraison": lieu_livraison,
        "description_colis": description_colis,
        "photo_exists": photo_exists,
        "choix_livraison": choix_livraison,
        "verified": False,
        "montant_livraison": montant_livraison  # Marquez le paiement comme non vérifié pour l'instant
        # Ajoutez d'autres informations nécessaires à la vérification du paiement
    }

    # Lors de la génération du lien de paiement
    #lien_paiement = generate_cinetpay_payment_link(montant_livraison, command_info[user_id]["id_recu"], user_id)

    # Message chaleureux avec un emoji et le bouton pour le lien de paiement
    #message_text = "🛒 Félicitations ! Votre commande a été enregistrée avec succès. Vous êtes sur le point d'être redirigé vers une page sécurisée où vous pourrez effectuer votre paiement en toute confiance. Cliquez sur le bouton ci-dessous pour accéder au paiement :"
    #bot.send_message(user_id, message_text, reply_markup=create_payment_link_button(lien_paiement))

    # Démarrage de la vérification périodique du paiement
    #verify_course_payment_periodically(user_id, montant_livraison)
    message_text = (
        "🚚 **Frais d'Assurance de Transport** 🚚\n\n"
        "Cher client,\n\n"
        "Afin de garantir la sécurité et l'acheminement efficace de votre colis, "
        "nous proposons une option d'assurance de transport. En choisissant le paiement en espèces, "
        "vous acceptez de régler des frais d'assurance de transport d'un montant de 2500 FCFA. Ces frais "
        "supplémentaires sont destinés à couvrir les coûts associés à l'acheminement sécurisé de votre "
        "colis jusqu'à sa destination finale.\n\n"
        "Nous tenons à vous assurer que cette mesure vise à protéger votre colis et à garantir sa livraison "
        "dans les meilleures conditions possibles. Votre sécurité et la sécurité de votre colis sont notre "
        "priorité absolue.\n\n"
        "Pour assurer votre colis, veuillez cliquer sur le bouton ci-dessous :"
    )

    markup = types.InlineKeyboardMarkup()
    assure_button = types.InlineKeyboardButton("Assurer le colis", callback_data="assurer_colis")
    markup.add(assure_button)

    bot.send_message(call.message.chat.id, message_text, reply_markup=markup)

# Fonction pour traiter le choix d'assurer le colis
@bot.callback_query_handler(func=lambda call: call.data == "assurer_colis")
def process_assurer_colis(call):
    montant_depot = 100  # Montant des frais d'assurance
    transaction_id = random.randint(100000, 999999)  # Génération d'un identifiant de transaction unique
    client_id = call.message.chat.id  # Utilisation de l'identifiant de chat comme identifiant client
    lien_paiement = generate_cinetpay_payment_link(montant_depot, transaction_id, client_id)
    markup = types.InlineKeyboardMarkup()
    payment_button = types.InlineKeyboardButton(text="Paiement Mobile", url=lien_paiement)
    
    markup.row(payment_button)
    
    if lien_paiement:
        bot.send_message(call.message.chat.id, "Votre colis est maintenant assuré. Veuillez cliquer sur le lien ci-dessous pour effectuer le paiement :", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Une erreur s'est produite lors de la génération du lien de paiement pour l'assurance du colis. Veuillez réessayer plus tard.")

    verify_course_payment_periodically(client_id, montant_depot)

def verify_course_payment_periodically(user_id, montant):
    global photo_exists
    site_id = 607207
    verification_attempts = 0
    invoice_saved = False
    amount_str = str(montant)  # Convertir l'entier en chaîne de caractères
    id_recu_str = str(command_info[user_id]["id_recu"]) 
    while not command_info[user_id]["verified"] and verification_attempts < 3 and not invoice_saved:
        
        if verify_cinetpay_transaction("401370", site_id, CINETPAY_API_KEY, "100"):
            invoice_saved = True
            command_info[user_id]["verified"] = True
            etat_course = "en_cours"
            # Enregistrer la course dans la base de données si la transaction est réussie
            save_course(
                command_info[user_id]["nom_expediteur"],
                #command_info[user_id]["nom_destinataire"],
                command_info[user_id]["numero_expediteur"],
                command_info[user_id]["lieu_recuperation"],
                command_info[user_id]["lieu_livraison"],
                command_info[user_id]["description_colis"],
                command_info[user_id]["heure_ramassage"],
                photo_colis if photo_exists else None,
                command_info[user_id]["choix_livraison"],
                user_id,
                etat_course,
                amount_str
            )
            bot.send_message(user_id, "Transaction réussie : La course a été enregistrée.")
        else:
            bot.send_message(user_id, "Veuillez vérifier votre paiement.")
            verification_attempts += 1
            if verification_attempts < 3:
                bot.send_message(user_id, f"Tentative de vérification #{verification_attempts}. Attendez 1 minute avant la prochaine vérification.")
            time.sleep(60)  # Attendre 1 minute avant la prochaine vérification
            
    if verification_attempts >= 3 and not command_info[user_id]["verified"]:
        bot.send_message(user_id, "Transaction annulée : Le paiement n'a pas été vérifié après 3 tentatives. Veuillez réessayer plus tard.")
        command_info.pop(user_id, None)
        countdown_timers.pop(user_id, None)
    else:
        # Génération du QR code personnalisé
        commande_id = command_info[user_id]["id_recu"]
        qr_code_data_h = f"Commande ID: {commande_id}, Client ID: {user_id}"
        qr_code_data = hashlib.sha256(qr_code_data_h.encode()).hexdigest()
        qr_code_filename = generate_qr_code(qr_code_data, f"qr_code_commande_{commande_id}.png")

        # Enregistrement du nom du fichier QR code dans la base de données
        try:
            if not conn.is_connected():
                # Si la connexion n'est pas active, rétablissez-la
                conn.reconnect() 
            cursor = conn.cursor()
            cursor.execute("UPDATE courses SET qr_code = %s WHERE id_course = %s", (qr_code_filename, commande_id))
            conn.commit()
            cursor.close()
        except (Exception, mysql.connector.Error) as error:
            print("Erreur lors de l'enregistrement du QR code dans la base de données:", error)

        # Génération du PDF de la facture
        pdf_filename = generate_invoicec_pdf(commande_id, user_id, command_info[user_id]["nom_expediteur"],  command_info[user_id]["lieu_livraison"], montant_livraison)

        # Envoi du code QR et de la facture au client
        with open(qr_code_filename, "rb") as file:
            qr_code_img = io.BytesIO(file.read())
            qr_code_img.name = 'qr_code.png'
            bot.send_photo(user_id, qr_code_img)
        send_invoice(user_id, pdf_filename)






    
        
# Associez la fonction handle_help au bouton d'aide
@bot.message_handler(func=lambda message: message.text == "Aide ℹ️")
def handle_help_button(message):
    handle_help(message)

# Associez la fonction handle_start au bouton "Retour" dans l'écran d'aide
@bot.message_handler(func=lambda message: message.text == "Retour ↩️")
def handle_back_button(message):
    handle_start(message)

@bot.message_handler(func=lambda message: message.text.startswith("Quitter"))
def handle_quitter(message):
    user_id = message.from_user.id

    # Supprime le panier de l'utilisateur
    clear_cart(user_id)

    # Masque le menu des catégories
    markup = types.ReplyKeyboardRemove()

    # Affiche le message d'au revoir
    bot.reply_to(message, "Au revoir ! Pour commencer, appuyez sur /start.", reply_markup=markup)

# Gère l'action du bouton "/enregistrer_informations"

def handle_enregistrer_informations(message):
    client_id = message.chat.id  # ID du client (ID du chat)
    bot.reply_to(message, "Veuillez saisir votre nom :")
    bot.register_next_step_handler(message, process_name, client_id)


# Variables globales pour stocker les informations du client
temp_name = None
temp_prenom = None
temp_adresse = None
temp_client_id = None
temp_email = None

# Fonction de traitement du nom
def process_name(message):
    global temp_name
    temp_name = message.text
    bot.reply_to(message, "Veuillez saisir votre prénom :")
    bot.register_next_step_handler(message, process_prenom)


# Fonction de traitement du prénom
def process_prenom(message):
    global temp_prenom
    temp_prenom = message.text
    bot.reply_to(message, "Veuillez saisir votre adresse :")
    bot.register_next_step_handler(message, process_adresse)

# Fonction de traitement de l'adresse
def process_adresse(message):
    global temp_adresse
    temp_adresse = message.text
    bot.reply_to(message, "Veuillez saisir votre email :")
    bot.register_next_step_handler(message, process_email)

def process_email(message):
    global temp_email
    temp_email = message.text
    bot.reply_to(message, "Veuillez saisir votre téléphone :")
    bot.register_next_step_handler(message, process_telephone)

# Fonction de traitement du téléphone
def process_telephone(message):
    global temp_client_id
    telephone = message.text
    # Assurez-vous que client_id est un entier
    client_id = message.chat.id
    try:
        cursor = conn.cursor()

        # Vérifier si l'utilisateur existe déjà
        check_query = "SELECT * FROM clients WHERE id_client = %s"
        cursor.execute(check_query, (client_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Utiliser la requête UPDATE pour mettre à jour les informations
            update_query = "UPDATE clients SET nom = %s, prenom = %s, quartier = %s, telephone = %s, email = %s WHERE id_client = %s"
            update_values = (temp_name, temp_prenom, temp_adresse, telephone, temp_email, client_id)
            cursor.execute(update_query, update_values)
        else:
            # Utiliser la requête INSERT INTO pour insérer de nouvelles informations
            insert_query = "INSERT INTO clients (id_client, nom, prenom, quartier, telephone, email) VALUES (%s, %s, %s, %s, %s, %s)"
            insert_values = (client_id, temp_name, temp_prenom, temp_adresse, telephone, temp_email)
            cursor.execute(insert_query, insert_values)

        conn.commit()
        cursor.close()
        bot.reply_to(message, "Informations enregistrées avec succès !")
    except (Exception, mysql.connector.Error) as error:
        bot.reply_to(message, error)



# Gère les messages textuels
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text.startswith('/add'):
        product_name = message
        user_id = message.from_user.id
        if product_name:
            add_product_to_cart(user_id, product_name)
            bot.reply_to(message, f"Produit {product_name} ajouté au panier avec succès.")
        else:
            bot.reply_to(message, "Veuillez spécifier le nom du produit à ajouter au panier.")
    elif message.text in get_categories():
        category = message.text
        # Récupère les produits de la catégorie sélectionnée depuis la base de données
        products = get_products_by_category(category)
        markup = None
        # Traite les données des produits comme tu le souhaites
        sent_products = []  # Liste pour stocker les produits déjà envoyés

        for product in products:
            product_name = product[0]
            response = f"Nom : {product_name}\nDescription : {product[1]}\nPrix : {product[2]} FCFA\n"
            images = get_product_images(product_name)

            if images:
                media_group = []
                for image_path in images:
                    with open(image_path, 'rb') as photo:
                        file_data = photo.read()
                        media = types.InputMediaPhoto(media=file_data)
                        media_group.append(media)

                # Envoyer le carrousel d'images
                bot.send_media_group(message.chat.id, media_group)

            # Envoyer le message du produit uniquement s'il n'a pas été déjà envoyé
            if product_name not in sent_products:
                if images:
                    # Ajouter le bouton "Ajouter au panier"
                    btn_add_to_cart = types.InlineKeyboardButton("Ajouter au panier", callback_data=f"add_to_cart {product_name}")
                    markup = types.InlineKeyboardMarkup().add(btn_add_to_cart)
                    bot.send_message(message.chat.id, text=response, reply_markup=markup)
                else:
                    # Envoyer le message sans les images mais avec le bouton "Ajouter au panier"
                    btn_add_to_cart = types.InlineKeyboardButton("Ajouter au panier", callback_data=f"add_to_cart {product_name}")
                    markup = types.InlineKeyboardMarkup().add(btn_add_to_cart)
                    bot.send_message(message.chat.id, text=response, reply_markup=markup)

            sent_products.append(product_name)  # Ajouter le produit à la liste des produits envoyés
    elif message.text == "🛒 Voir Panier":
        handle_voir_panier(message)
    elif message.text.startswith("Scanner QR code"):
        handle_scanner_qrcode(message)
    elif message.text.startswith("Contactez-nous"):
        handle_contactez_nous(message)
    elif message.text.startswith("Enregistrer les informations"):
        handle_enregistrer_informations(message)
    elif message.text.startswith("Acheter"):
        handle_acheter(message)
    else:
        # Répondre en cas de message non reconnu
        bot.reply_to(message, 'Je ne comprends pas votre demande.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart'))
def handle_add_to_cart(call):
    user_id = call.from_user.id
    callback_data = call.data.split()
    product_name = " ".join(callback_data[1:])
    add_product_to_cart(user_id, product_name)
    bot.answer_callback_query(call.id, f"Produit {product_name} ajouté au panier.")




@bot.callback_query_handler(func=lambda call: call.data == 'confirm_payment')
def handle_confirm_payment(call):
    # Message simplifié sur le processus de paiement sécurisé
    # Modifiez le message de paiement pour le rendre plus attrayant avec des emojis
    payment_message = (
        "🌟 Merci pour votre paiement! 🌟 En cliquant sur le bouton ci-dessous, vous serez redirigé "
        "vers une page web sécurisée pour finaliser votre paiement en toute sécurité.\n\n"
        "Appuyez sur 'Confirmer le paiement' pour continuer. 💳💰"
    )


    # Création du bouton
    btn_mobile = types.InlineKeyboardButton("Confirmer le paiement", callback_data="payment_mobile")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(btn_mobile)

    # Envoie du message avec le bouton
    bot.send_message(call.from_user.id, payment_message, reply_markup=markup)






def calculate_total_amount(user_id):
    cart_content = get_cart_content(user_id)
    total_amount = 0

    for product_name, quantity in cart_content.items():
        price = get_product_price(product_name)
        if price is not None:
            total_amount += price * quantity

    return total_amount


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
        print("Erreur lors de la récupération des informations de l'utilisateur :", e)
        return None



def generate_cinetpay_payment_link(montant_depot, transaction_id, client_id):
    # Récupère les informations du client depuis la base de données en utilisant le client_id
    client_info = get_client_info(client_id)   # À implémenter selon ta structure de base de données
    
    if client_info is None:
        print("Impossible de récupérer les informations du client depuis la base de données.")
        return None
    
    numero_destinataire = "656958696"  # Numéro de téléphone de destination
    api_url = "https://api-checkout.cinetpay.com/v2/payment"
    amount = int(montant_depot)
    
    # Utilise les informations du client pour remplir les paramètres de la requête
    query_params = {
        "amount": amount,
        "currency": "XAF",
        "description": "Paiement de facture",
        "customer_name": client_info["nom"],  # Remplace avec le nom du client depuis la base de données
        "customer_surname": client_info["prenom"],  # Remplace avec le prénom du client depuis la base de données
        "customer_phone_number": numero_destinataire,
        #"customer_email": client_info["email"],  # Remplace avec l'adresse email du client depuis la base de données
        "return_url": "https://t.me/BEST_SELLER_UPbot",
        "notify_url": "https://t.me/BEST_SELLER_UPbot",
        "site_id": "607207",  # Remplace par l'identifiant de votre site CinetPay
        "transaction_id": transaction_id  # Remplace par un identifiant unique pour chaque transaction
    }
    
    # Ajoute la clé API aux paramètres de l'URL
    query_params["apikey"] = CINETPAY_API_KEY
    
    response = requests.post(api_url, params=query_params)
    
    if response.status_code == 200:  # Utilisez le code 201 pour indiquer "CREATED"
        data = response.json()
        if "data" in data and "payment_url" in data["data"]:
            return data["data"]["payment_url"]  # Retourne le lien de paiement
    else:
        print("Erreur lors de la génération du lien de paiement :", response.text, response.status_code)
        return None

def save_course(nom_expediteur, numero_expediteur, lieu_recuperation,
                lieu_livraison, description_colis,heure_ramassage, photo_colis, choix_livraison, user_id, etat_course, prix):
    global conn
    try:
        if not conn.is_connected():
            conn.reconnect()

        cursor = conn.cursor()

        insert_query = """
            INSERT INTO courses (nom_expediteur, numero_expediteur,
            lieu_recuperation, lieu_livraison, description_colis,heure_ramassge, photo_colis, choix_livraison, prix, client_id, etat_course)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (
            nom_expediteur, numero_expediteur, lieu_recuperation,
            lieu_livraison, description_colis,heure_ramassage, photo_colis, choix_livraison,prix, user_id, etat_course
        )

        cursor.execute(insert_query, data)
        conn.commit()
        print("La course a été enregistrée avec succès.")

    except (mysql.connector.Error, Exception) as error:
        print("Erreur lors de l'enregistrement de la course :", error)

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def save_invoice(facture_id, client_id, date_facture, montant, lieu_livraison, livre):
    global conn
    try:
        if not conn.is_connected():
            # Si la connexion n'est pas active, rétablissez-la
            conn.reconnect()
        # Création d'un curseur pour exécuter les requêtes SQL
        cursor = conn.cursor()
        site_id = '607207'
        amount_str = str(montant)  # Convertir l'entier en chaîne de caractères
        id_recu_str = str(facture_id) 
        # Vérifier l'état de la transaction avec CinetPay
        result = verify_cinetpay_transaction(id_recu_str, site_id, CINETPAY_API_KEY,amount_str)

        if result is True:
            # La transaction est réussie, enregistrer la facture dans la base de données
            insert_query = """
                INSERT INTO commandes (id_commande, lieu_livraison, prix, date, client_id, etat_commande)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            data = (facture_id, client_id, date_facture, montant, lieu_livraison, livre)

            cursor.execute(insert_query, data)
            conn.commit()
            print("La commande a été enregistrée avec succès .")
        else:
            # La transaction n'est pas réussie, demander à l'utilisateur de vérifier le paiement
            print("La transaction n'a pas été réussie. Veuillez vérifier votre paiement.")

    except (mysql.connector.Error, Exception) as error:
        # Gérer les erreurs liées à la base de données
        print("Erreur lors de l'enregistrement de la facture :", error)

    finally:
        # Fermer le curseur et la connexion à la base de données, même en cas d'exception
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def get_qr_code_from_database(commande_id):
    try:
        if not conn.is_connected():
            # Si la connexion n'est pas active, rétablissez-la
            conn.reconnect()

        cursor = conn.cursor()

        # Récupérer le nom du fichier du code QR pour la commande spécifiée
        select_query = "SELECT qr_code FROM commandes WHERE id_commande = %s"
        cursor.execute(select_query, (commande_id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  # Retourne le nom du fichier du code QR
        else:
            return None
    except mysql.connector.Error as error:
        print("Erreur lors de la récupération du QR code depuis la base de données :", error)
        return None
    
def display_qr_code_to_user(commande_id):
    qr_code_filename = f"qr_code_commande_{commande_id}.png"
    try:
        # Ouvrir le fichier du code QR directement
        with open(qr_code_filename, "rb") as file:
            encoded_image = base64.b64encode(file.read()).decode('utf-8')
            # Ici, vous devriez utiliser une méthode pour transmettre l'image encodée à votre interface utilisateur,
            # cela peut être via une API, une interface web, ou tout autre moyen d'interaction utilisateur.
            # En supposant une interface web, vous pouvez inclure l'image encodée dans une balise HTML <img>.
            print(f'<img src="data:image/png;base64,{encoded_image}">')
    except FileNotFoundError as e:
        print("Fichier du QR code introuvable :", e)

# Dictionnaire pour stocker les informations de paiement en cours
payment_info = {}

# Dictionnaire pour stocker les comptes à rebours
countdown_timers = {}

def verify_payment_periodically(user_id):
    site_id = 607207
    verification_attempts = 0
    invoice_saved = False
    amount_str = str(payment_info[user_id]["amount"])  # Convertir l'entier en chaîne de caractères
    id_recu_str = str(payment_info[user_id]["id_recu"]) 
    while not payment_info[user_id]["verified"] and verification_attempts < 3 and not invoice_saved:
        
        if verify_cinetpay_transaction(id_recu_str, site_id, CINETPAY_API_KEY, amount_str):
            invoice_saved = True
            payment_info[user_id]["verified"] = True
            # Enregistrer la facture dans la base de données si la transaction est réussie
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
            delivery_address = get_user_address(user_id)
            bools = "en_cours"
            save_invoice(payment_info[user_id]["id_recu"],delivery_address,payment_info[user_id]["amount"],current_datetime, user_id,bools)
            bot.send_message(user_id, "Transaction réussie : La facture a été enregistrée.")
        else:
            bot.send_message(user_id, "Veuillez vérifier votre paiement.")
            verification_attempts += 1
            if verification_attempts < 3:
                bot.send_message(user_id, f"Tentative de vérification #{verification_attempts}. Attendez 1 minute avant la prochaine vérification.")
            time.sleep(60)  # Attendre 1 minute avant la prochaine vérification
            
    if verification_attempts >= 3 and not payment_info[user_id]["verified"] :
        bot.send_message(user_id, "Transaction annulée : Le paiement n'a pas été vérifié après 3 tentatives. Veuillez réessayer plus tard.")
        payment_info.pop(user_id, None)
        countdown_timers.pop(user_id, None)
    else:
        # Génération du QR code personnalisé
        commande_id = payment_info[user_id]["id_recu"]
        qr_code_data_h = f"Commande ID: {commande_id}, Client ID: {user_id}"
        qr_code_data = hashlib.sha256(qr_code_data_h.encode()).hexdigest()
        #qr_code_image = generate_qr_code(qr_code_data)

    # Générer le code QR et obtenir le nom de fichier
        qr_code_filename = generate_qr_code(qr_code_data, f"qr_code_commande_{commande_id}.png")
        # Sauvegarde de l'image du QR code
        
        #qr_code_image.save(qr_code_filename)

        # Enregistrement du nom du fichier QR code dans la base de données
        try:
            if not conn.is_connected():
            # Si la connexion n'est pas active, rétablissez-la
                conn.reconnect() 
            cursor = conn.cursor()
            cursor.execute("UPDATE commandes SET qr_code = %s WHERE id_commande = %s", (qr_code_data, commande_id))
            conn.commit()
            cursor.close()
            
        except (Exception, mysql.connector.Error) as error:
            print("Erreur lors de l'enregistrement du QR code dans la base de données:", error)

        qr_code_data_h = f"Commande ID: {commande_id}, Client ID: {user_id}"
        #qr_code = qrcode.create(qr_code_data_h)
        qr_code_path = f"qr_code_commande_{commande_id}.png"
        #qr_code.png(qr_code_path, scale=10)
        client = get_client_info(user_id)
        client_name = client["nom"]
        client_surname = client["prenom"]
        pdf_filename = generate_invoice_pdf(commande_id,user_id, client_name, client_surname, delivery_address, payment_info[user_id]["amount"])

        with open(qr_code_path, "rb") as file:
            qr_code_img = io.BytesIO(file.read())
            qr_code_img.name = 'qr_code.png'
            bot.send_photo(user_id, qr_code_img)
        send_invoice(user_id, pdf_filename)
        

def send_invoice(user_id, pdf_filename):
    try:
        with open(pdf_filename, 'rb') as invoice_file:
            bot.send_document(user_id, invoice_file, caption="Voici votre facture.")
    except FileNotFoundError as e:
        print(f"Erreur: Fichier introuvable - {e}")


def generate_invoice_pdf(commande_id, client_id, client_name, client_surname, client_address, amount):
    pdf_filename = f"invoice_{commande_id}.pdf"

    # Crée un document PDF
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    # Dessine l'en-tête centré
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "NGDelivery Invoice")

    # Dessine des lignes pour chaque information de la facture
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"ID Commande: {commande_id}")
    c.drawString(50, 680, f"ID Client: {client_id}")
    c.drawString(50, 660, f"Nom: {client_name}")
    c.drawString(50, 640, f"Prénom: {client_surname}")
    c.drawString(50, 620, f"Adresse: {client_address}")
    c.drawString(50, 600, f"Montant: {amount} XAF")

    # Dessine des lignes horizontales pour séparer les sections
    c.line(30, 580, 570, 580)  # Ligne sous les informations de la facture
    c.line(30, 570, 570, 570)  # Ligne sous les lignes précédentes

    # Enregistrer et fermer le PDF
    c.save()

    return pdf_filename

def generate_invoicec_pdf(commande_id, client_id, client_name, client_address, amount):
    pdf_filename = f"invoice_{commande_id}.pdf"

    # Crée un document PDF
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    # Dessine l'en-tête centré
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "NGDelivery Invoice")

    # Dessine des lignes pour chaque information de la facture
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"ID Commande: {commande_id}")
    c.drawString(50, 680, f"ID Client: {client_id}")
    c.drawString(50, 660, f"Nom: {client_name}")
    c.drawString(50, 620, f"Adresse: {client_address}")
    c.drawString(50, 600, f"Montant: {amount} XAF")

    # Dessine des lignes horizontales pour séparer les sections
    c.line(30, 580, 570, 580)  # Ligne sous les informations de la facture
    c.line(30, 570, 570, 570)  # Ligne sous les lignes précédentes

    # Enregistrer et fermer le PDF
    c.save()

    return pdf_filename



@bot.callback_query_handler(func=lambda call: call.data == 'start_countdown')
def start_countdown_callback(call):
    user_id = call.from_user.id
    
    if user_id not in countdown_timers and user_id in payment_info and not payment_info[user_id]["verified"]:
        # Démarrer le compte à rebours de 2 minutes et la vérification périodique dans des threads distincts
        countdown_thread = threading.Thread(target=start_countdown, args=(user_id,))
        countdown_thread.start()
        countdown_timers[user_id] = countdown_thread

        verification_thread = threading.Thread(target=verify_payment_periodically, args=(user_id,))
        verification_thread.start()
        
        # Créer un bouton annuler
        cancel_button = types.InlineKeyboardButton("Annuler", callback_data="cancel")
        cancel_keyboard = types.InlineKeyboardMarkup()
        cancel_keyboard.row(cancel_button)
        bot.send_message(user_id, "Le compte à rebours a commencé. Cliquez sur le bouton 'Annuler' pour arrêter la transaction.", reply_markup=cancel_keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_transaction_callback(call):
    user_id = call.from_user.id
    if payment_info.get(user_id):
        payment_info.pop(user_id, None)
        if user_id in countdown_timers:
            countdown_timers[user_id].join()  # Attendre que le compte à rebours se termine
            countdown_timers.pop(user_id, None)
        bot.send_message(user_id, "Transaction annulée : Vous avez annulé la transaction en cours.")

def start_countdown(user_id):
    countdown_duration = 120  # 2 minutes en secondes
    end_time = time.time() + countdown_duration
    
    while time.time() < end_time:
        remaining_time = int(end_time - time.time())
        if payment_info[user_id]["verified"]:  # Vérifiez si la facture est sauvegardée
            break  # Sortez de la boucle si la facture est enregistrée
        bot.send_message(user_id, f"Temps restant : {remaining_time} secondes")
        time.sleep(10) 


@bot.callback_query_handler(func=lambda call: call.data == 'payment_mobile')
def process_mobile_payment(call):
    user_id = call.from_user.id

    amount = calculate_total_amount(user_id)
    amount = amount + 100
    id_recu = random.randint(100000, 999999)

    payment_info[user_id] = {
        "amount": amount,
        "id_recu": id_recu,
        "payment_url": generate_cinetpay_payment_link(amount, id_recu, user_id),
        "verified": False
    }
    ad = get_user_address(user_id)
    cd = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    et = "non_livree"
    #save_invoice(id_recu,ad,amount,cd,user_id,et)
        # Modifiez le message pour inclure des emojis
    message_text = f"🛍️ Vous allez payer {amount} XAF pour le reçu {id_recu}. 🛍️\n\n" \
                "En cas de problème avec votre commande, veuillez nous communiquer le numéro de votre reçu: " \
                f"{id_recu}.\n\n" \
                "N'hésitez pas à utiliser le bouton 'Contactez-nous ☎️' si vous avez des questions ou des préoccupations."
    bot.send_message(user_id, message_text)


    payment_button = types.InlineKeyboardButton("Cliquez ici pour effectuer le paiement", url=payment_info[user_id]["payment_url"])
    payment_keyboard = types.InlineKeyboardMarkup()
    payment_keyboard.row(payment_button)

    
    
    countdown_thread = threading.Thread(target=start_countdown, args=(user_id,))
    countdown_thread.start()
    countdown_timers[user_id] = countdown_thread
    
    # Store the transaction ID in the payment_info dictionary
    payment_info[user_id]["transaction_id"] = id_recu  # Replace this with your actual logic to get the transaction ID
    
    verification_thread = threading.Thread(target=verify_payment_periodically, args=(user_id,))
    verification_thread.start()
    
    # Send the payment link as a message
    bot.send_message(user_id, "Veuillez cliquer sur le lien suivant pour effectuer le paiement :", reply_markup=payment_keyboard)

# ...


@bot.message_handler(func=lambda message: message.text == "Annuler")
def cancel_transaction(message):
    user_id = message.from_user.id
    if payment_info.get(user_id):
        payment_info.pop(user_id, None)
        if user_id in countdown_timers:
            countdown_timers[user_id].join()  # Attendre que le compte à rebours se termine
            countdown_timers.pop(user_id, None)
        bot.send_message(user_id, "Transaction annulée : Vous avez annulé la transaction en cours.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay'))
def handle_payment(call):
    # Récupère le mode de paiement sélectionné
    #payment_method = call.data.split('_')[1]

    # Affiche un message avec le mode de paiement sélectionné
    #bot.send_message(call.from_user.id, f"Vous avez sélectionné le mode de paiement : {payment_method}")

    # Crée les boutons pour les options de récupération
    btn_delivery = types.InlineKeyboardButton("Se faire livrer", callback_data="delivery")
    btn_pickup = types.InlineKeyboardButton("Récupérer", callback_data="pickup")
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(btn_delivery, btn_pickup)

    # Envoie le message avec les options de récupération
    bot.send_message(call.from_user.id, "Comment souhaitez-vous récupérer votre produit :", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'delivery')
def handle_delivery(call):
    user_id = call.from_user.id
    address = get_user_address(user_id)

    if address:
        # Si le client a déjà une adresse enregistrée, demande de confirmation
        confirm_delivery_address(call.from_user.id, address)
    else:
        # Si le client n'a pas d'adresse enregistrée, demande d'entrer une adresse
        bot.send_message(call.from_user.id, "Veuillez entrer votre adresse de livraison :")
        bot.register_next_step_handler(call.message, process_delivery_address)

@bot.callback_query_handler(func=lambda call: call.data == 'pickup')
def handle_pickup(call):
    user_id = call.from_user.id
    pickup_address = get_user_address(user_id)

    if pickup_address:
        # Si l'adresse de récupération existe, demande de confirmation
        confirm_pickup_address(user_id, pickup_address)
    else:
        # Si l'adresse de récupération n'est pas disponible, envoie un message d'erreur
        bot.send_message(user_id, "L'adresse de récupération n'est pas disponible pour le moment.")
        bot.register_next_step_handler(call.message, process_delivery_address)
        # Vous pouvez également proposer d'autres options ou demander des informations supplémentaires

def get_user_address(user_id):
    try:
        if not conn.is_connected():
            # Si la connexion n'est pas active, rétablissez-la
            conn.reconnect()
        cursor = conn.cursor()
        query = "SELECT quartier FROM clients WHERE id_client = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]  # Retourne l'adresse du client
        else:
            return None  # Aucune adresse trouvée pour ce client

    except (Exception, mysql.connector.Error) as error:
        print("Erreur lors de la récupération de l'adresse du client :", error)
        return None


def confirm_pickup_address(user_id, address):
    # Crée les boutons de confirmation d'adresse
    btn_confirm = types.InlineKeyboardButton("Confirmer", callback_data="confirm_pickup")
    btn_change = types.InlineKeyboardButton("Changer", callback_data="change_address")
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(btn_confirm, btn_change)

    # Envoie le message avec l'adresse et les boutons de confirmation
    bot.send_message(user_id, f"Votre adresse de retrait :\n\n{address}\n\nConfirmez-vous cette adresse ?", reply_markup=markup)

def confirm_delivery_address(user_id, address):
    # Crée les boutons de confirmation d'adresse
    btn_confirm = types.InlineKeyboardButton("Confirmer", callback_data="confirm_address")
    btn_change = types.InlineKeyboardButton("Changer", callback_data="change_address")
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(btn_confirm, btn_change)

    # Envoie le message avec l'adresse et les boutons de confirmation
    bot.send_message(user_id, f"Votre adresse de livraison :\n\n{address}\n\nConfirmez-vous cette adresse ?", reply_markup=markup)

def process_delivery_address(message):
    user_id = message.from_user.id
    delivery_address = message.text

    # Vérifie si l'adresse de livraison est valide (vous pouvez ajouter vos critères de validation ici)
    if len(delivery_address) > 1:
        # L'adresse de livraison est valide, on peut l'utiliser
        update_user_address(user_id, delivery_address)
        bot.send_message(user_id, "Votre adresse de livraison a été enregistrée avec succès.")
    else:
        bot.send_message(user_id, "Adresse de livraison invalide. Veuillez entrer une adresse valide.")



def update_user_address(user_id, address):
    try:
        cursor = conn.cursor()
        query = "UPDATE clients SET quartier = %s WHERE id_client = %s"
        values = (address, user_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
    except (Exception, mysql.connector.Error) as error:
        print("Erreur lors de la mise à jour de l'adresse du client :", error)


@bot.callback_query_handler(func=lambda call: call.data == 'confirm_address')
def handle_confirm_address(call):
    user_id = call.from_user.id
    
    # Récupérer la date et l'heure actuelle
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Récupérer le montant total du panier
    total_amount = calculate_total_amount(user_id)
    
    # Récupérer l'adresse de livraison confirmée
    delivery_address = get_user_address(user_id)
    
    # Calculer le montant total du reçu
    receipt_amount = total_amount + 1000

    # Construire le message de réception
    receipt_message = f"Voici votre reçu :\n\n"
    receipt_message += f"Date et heure : {current_datetime}\n"
    receipt_message += f"Montant total du panier : {total_amount} FCFA\n"
    receipt_message += f"Adresse de livraison : {delivery_address}\n"
    receipt_message += f"Montant total du reçu : {receipt_amount} FCFA\n\n"
    
    # Créer le bouton de confirmation de paiement
    btn_confirm_payment = types.InlineKeyboardButton("Confirmer le paiement", callback_data="confirm_payment")
    markup = types.InlineKeyboardMarkup().add(btn_confirm_payment)
    
    # Envoyer le message de réception avec le bouton de confirmation de paiement
    bot.send_message(user_id, receipt_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_pickup')
def handle_confirm_pickup(call):
    user_id = call.from_user.id
    
    # Récupérer la date et l'heure actuelle
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Récupérer le montant total du panier
    total_amount = calculate_total_amount(user_id)
    
    # Récupérer l'adresse de livraison confirmée
    delivery_address = get_user_address(user_id)
    
    # Calculer le montant total du reçu
    receipt_amount = total_amount

    # Construire le message de réception
    receipt_message = f"Voici votre reçu :\n\n"
    receipt_message += f"Date et heure : {current_datetime}\n"
    receipt_message += f"Montant total du panier : {total_amount} FCFA\n"
    receipt_message += f"Adresse de livraison : {delivery_address}\n"
    receipt_message += f"Montant total du reçu : {receipt_amount} FCFA\n\n"
    
    # Créer le bouton de confirmation de paiement
    btn_confirm_payment = types.InlineKeyboardButton("Confirmer le paiement", callback_data="confirm_payment")
    markup = types.InlineKeyboardMarkup().add(btn_confirm_payment)
    
    # Envoyer le message de réception avec le bouton de confirmation de paiement
    bot.send_message(user_id, receipt_message, reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data == 'change_address')
def handle_change_address(call):
    # Demande au client d'entrer une nouvelle adresse
    bot.send_message(call.from_user.id, "Veuillez entrer votre nouvelle adresse de livraison :")
    bot.register_next_step_handler(call.message, process_delivery_address)



@bot.callback_query_handler(func=lambda call: call.data == 'delivery')
def handle_delivery(call):
    # Traite la récupération par livraison
    bot.send_message(call.from_user.id, "Vous avez choisi de vous faire livrer.")


@bot.callback_query_handler(func=lambda call: call.data == 'pickup')
def handle_pickup(call):
    # Traite la récupération en personne
    bot.send_message(call.from_user.id, "Vous avez choisi de récupérer en personne.")




@bot.callback_query_handler(func=lambda call: call.data == 'clear')
def handle_clear(call):
    user_id = call.from_user.id
    clear_cart(user_id)
    bot.answer_callback_query(call.id, "Le panier a été vidé.")


def clear_cart(user_id):
    if user_id in user_carts:
        user_carts[user_id] = {}


def get_categories():
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT categorie FROM produits")
    categories = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return categories


def calculate_total_amount(user_id):
    cart_content = get_cart_content(user_id)
    total_amount = 0

    for product_name, quantity in cart_content.items():
        price = get_product_price(product_name)
        if price is not None:
            total_amount += price * quantity

    return total_amount

def get_products_by_category(category):
    cursor = conn.cursor()
    query = "SELECT nom, description, prix_unitaire FROM produits WHERE categorie = %s"
    cursor.execute(query, (category,))
    products = cursor.fetchall()
    cursor.close()
    return products



def get_product_price(product_name):
    try:
        cursor = conn.cursor()
        query = "SELECT prix_unitaire FROM produits WHERE nom = %s"
        cursor.execute(query, (product_name,))
        price = cursor.fetchone()
        if price is not None:
            return price[0]
        else:
            logging.error("Produit non trouvé dans la base de données.")
            return None
    except (mysql.connector.Error, Exception) as error:
        logging.error("Erreur lors de la récupération du prix du produit :", exc_info=True)
        return None
    finally:
        cursor.close()



def handle_contactez_nous(message):
    contacts = {
        "Email": "defspsp@gmail.com",
        "Numéro de téléphone": "+237656958696"
    }
    
    contact_message = "Pour nous contacter :\n"
    for title, value in contacts.items():
        contact_message += f"{title}: {value}\n"
    
    # Envoie les informations de contact sans désactiver le clavier
    bot.reply_to(message, contact_message)



def add_product_to_cart(user_id, product_name):
    if user_id in user_carts:
        cart = user_carts[user_id]
        if product_name in cart:
            cart[product_name] += 1
        else:
            cart[product_name] = 1
    else:
        user_carts[user_id] = {product_name: 1}


def get_cart_content(user_id):
    return user_carts.get(user_id, {})


@bot.message_handler(func=lambda message: message.text.startswith("Acheter"))
def handle_acheter(message):
    if message.text == "🛒 Voir Panier":
        handle_voir_panier(message)  # Appelle directement la fonction handle_voir_panier
        return 
    # Récupère les catégories de produits depuis la base de données
    categories = get_categories()

    # Crée les boutons de catégories
    markup = types.ReplyKeyboardMarkup(row_width=2)
    buttons = [types.KeyboardButton(category) for category in categories]

    # Ajoute le bouton "Quitter"
    
    buttons.append(types.KeyboardButton("Retour ↩️"))
    buttons.append(types.KeyboardButton("Quitter"))
    buttons.append(types.KeyboardButton("🛒 Voir Panier"))
    markup.add(*buttons)

    # Envoie le message avec les boutons de catégories
    bot.reply_to(message, 'Veuillez sélectionner une catégorie :', reply_markup=markup)

    # Enregistre la prochaine étape pour traiter la catégorie sélectionnée
    bot.register_next_step_handler(message, process_selected_category)


def process_selected_category(message):
    category = message.text

    # Vérifie si la catégorie est valide en la comparant aux catégories disponibles
    categories = get_categories()
    if category in categories:
        # La catégorie est valide, on peut afficher les produits
        get_products_by_category(category)
    else:
        bot.send_message(message.chat.id, "Catégorie invalide. Veuillez sélectionner une catégorie valide.")


scanned_invoice_id = None

@bot.message_handler(func=lambda message: message.text.startswith("Scanner QR code"))
def handle_scanner_qrcode(message):
    user_id = message.from_user.id
    
    invoices = get_invoices_by_user(user_id)
    invoices_in_progress = [invoice for invoice in invoices if invoice[3] == 'en_cours']
    
    if invoices_in_progress:
        for invoice in invoices_in_progress:
            facture_id = invoice[0]
            client_id = invoice[1]
            lieu_livraison = invoice[2]
            etat = invoice[3]
            
            # Créer le message pour chaque facture avec les boutons
            response = f"Facture ID : {facture_id}\nClient ID : {client_id}\nLieu de livraison : {lieu_livraison}\nÉtat : {etat}\n\n"
            
            # Créer les boutons "Envoyer le code" et "Prendre une photo" pour chaque facture
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_send_code = types.InlineKeyboardButton("Envoyer le code", callback_data=f"send_code_{facture_id}")
            btn_take_photo = types.InlineKeyboardButton("Prendre une photo", callback_data=f"take_photo_{facture_id}")
            markup.row(btn_send_code, btn_take_photo)
            
            # Envoyer le message avec les boutons pour chaque facture
            bot.send_message(message.chat.id, response, reply_markup=markup)
    else:
        bot.reply_to(message, "Aucune livraison en cours.")

# Fonction pour gérer les actions des boutons
@bot.callback_query_handler(func=lambda call: True)
def handle_button_actions(call):
    if call.data.startswith("send_code_"):
        # Traitement pour le bouton "Envoyer le code"
        #facture_id = call.data.split("_")[1]
        handle_send_code(call)
    elif call.data.startswith("take_photo_"):
        # Traitement pour le bouton "Prendre une photo"
        #facture_id = call.data.split("_")[1]
        handle_take_photo_callback(call)



@bot.callback_query_handler(func=lambda call: call.data == "send_code")
def handle_send_code(call):
    message = call.message
    # Demander à l'utilisateur d'envoyer une photo
    bot.reply_to(message, "Veuillez envoyer une photo du code QR.")
    bot.register_next_step_handler(message, check_qr_code_photo)

    # Définir la fonction de vérification de la photo
def check_qr_code_photo(message):
    try:
        # Vérifie si le message a des données photo
        if message.photo:
            # Récupère les informations de la photo
            photo_info = message.photo[-1]
            photo_id = photo_info.file_id

            # Récupère la photo par son ID
            photo_file = bot.get_file(photo_id)
            photo_data = bot.download_file(photo_file.file_path)
            # Open the photo using PIL
            image = Image.open(io.BytesIO(photo_data))

            # Process the QR code in the image
            qr_code_data = decode_qr_code(image)

            if qr_code_data is not None:
                qr_code_text = qr_code_data.decode("utf-8")

                # Get the invoice ID from the QR code text
                user_generated_hash = str(qr_code_text)
            # Valider la photo du QR code
            if verify_qr_code_from_invoice(user_generated_hash):
                set_delivery_state(user_generated_hash, "livree")
                bot.reply_to(message, "Le code QR correspond. La livraison a été marquée comme livrée.")
            else:
                bot.reply_to(message, "Le code QR ne correspond pas. Veuillez réessayer.")
        else:
            bot.reply_to(message, "Aucune photo n'a été envoyée. Veuillez envoyer une photo contenant le code QR.")

    except Exception as api_exception:
        bot.reply_to(message, "Une erreur s'est produite lors du traitement de la photo. Veuillez réessayer.")
        print("Error while processing photo:", api_exception)

@bot.message_handler(func=lambda message: message.text == "🛒 Voir Panier")
def handle_voir_panier(message):
    try:
        user_id = message.from_user.id
        cart_content = get_cart_content(user_id)
        response = "Contenu du panier :\n\n"
        if cart_content:
            total_price = 0
            for product_name, quantity in cart_content.items():
                price = get_product_price(product_name)
                if price is not None:
                    item_price = price * quantity
                    response += f"Produit : {product_name}\nQuantité : {quantity}\nPrix unitaire : {price} FCFA\nPrix total : {item_price} FCFA\n\n"
                    total_price += item_price
                else:
                    response += f"Produit : {product_name}\nQuantité : {quantity}\nPrix unitaire : Prix inconnu\n\n"
            response += f"Total : {total_price} FCFA"
            # Ajoute le bouton "Payer" en dessous du total
            btn_pay = types.InlineKeyboardButton("Payer", callback_data="pay")
            markup = types.InlineKeyboardMarkup().add(btn_pay)

            # Ajoute le bouton "Vider" à côté du bouton "Payer"
            btn_clear = types.InlineKeyboardButton("Vider", callback_data="clear")
            markup.row(btn_clear)

            bot.reply_to(message, response, reply_markup=markup)
        else:
            response = "Votre panier est vide."
            bot.reply_to(message, response)
    except Exception as e:
        logging.error("Une erreur s'est produite lors de la gestion du panier :", exc_info=True)

def get_invoice_id_from_qrcode(client_id):
    try:
        cursor = conn.cursor()
        query = "SELECT id_commande FROM commandes WHERE client_id = %s"
        cursor.execute(query, (client_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]  # Retourne l'ID de la facture
        else:
            return None  # Aucune facture trouvée pour ce client

    except (Exception, mysql.connector.Error) as error:
        print("Erreur lors de la récupération de l'ID de la facture :", error)
        return None



@bot.callback_query_handler(func=lambda call: call.data == "take_photo")
def handle_take_photo_callback(call):
    message = call.message
    chat_id = message.chat.id

    # Ask the user to take a photo
    bot.send_message(chat_id, "Veuillez prendre une photo du QR code.")

    # Register the next step handler for processing the photo
    bot.register_next_step_handler(message, process_photo)


def verify_cinetpay_transaction(transaction_id, site_id, apikey,expected_amount):
    url = "https://api-checkout.cinetpay.com/v2/payment/check"
    headers = {'Content-Type': 'application/json'}
    data = {
        "transaction_id": transaction_id,
        "site_id": site_id,
        "apikey": apikey
    }

    response = requests.post(url, json=data, headers=headers)
    response_json = response.json()

    # Vérifier si la transaction a réussi en vérifiant le statut dans la réponse JSON
    if response_json.get("code") == "00" and response_json.get("data", {}).get("status") == "ACCEPTED":
        actual_amount = response_json.get("data", {}).get("amount")
        if actual_amount == expected_amount:
                return True
        else:
                print("Montant de la transaction ne correspond pas.")
                return False
    else:
            return False





def process_photo(message):
    if message.content_type == "photo":
        photo = message.photo[-1]  # Get the last photo sent by the user
        photo_id = photo.file_id
        client_id = message.chat.id
        # Get the photo file by its ID
        photo_file = bot.get_file(photo_id)
        photo_data = bot.download_file(photo_file.file_path)

        # Open the photo using PIL
        image = Image.open(io.BytesIO(photo_data))

        # Process the QR code in the image
        qr_code_data = decode_qr_code(image)

        if qr_code_data is not None:
            qr_code_text = qr_code_data.decode("utf-8")

            # Get the invoice ID from the QR code text
            user_generated_hash = str(qr_code_text)

            # Verify the invoice and update the delivery state if the QR code is correct
            if verify_qr_code_from_invoice(user_generated_hash):
                set_delivery_state(user_generated_hash, "livree")
                bot.reply_to(message, "Le QR code correspond. La livraison a été marquée comme livrée.")
            else:
                bot.reply_to(message, "Le QR code ne correspond pas à la facture en cours.")
        else:
            bot.reply_to(message, "Aucun QR code n'a été détecté dans la photo.")
    else:
        bot.reply_to(message, "Veuillez envoyer une photo contenant le QR code.")


def decode_qr_code(image):
    # Perform QR code decoding using the pyzbar library
    qr_code = pyzbar.decode(image)

    if qr_code:
        qr_code_data = qr_code[0].data
        return qr_code_data

    return None

def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename


def get_delivery_state(client_id):
    try:
        cursor = conn.cursor()
        query = "SELECT etat_commande FROM commandes WHERE client_id = %s)"
        cursor.execute(query, (client_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]  # Renvoie l'état de livraison
        else:
            return None  # Aucun résultat trouvé pour le client ID donné
    except (Exception, mysql.connector.Error) as error:
        print("Erreur lors de la récupération de l'état de livraison:", error)
        return None

def get_qr_code_hash_from_database(user_generated_hash):
    try:
        # Créez un curseur pour exécuter des requêtes SQL
        cursor = conn.cursor()

        # Exécutez la requête SQL pour récupérer le hash de la colonne qr_code pour l'ID de la facture donné
        query = "SELECT qr_code FROM commandes WHERE qr_code = %s"
        cursor.execute(query, (user_generated_hash,))

        # Récupérez le hash de la colonne qr_code de la base de données
        qr_code_hash = cursor.fetchone()
        
        # Fermez le curseur
        cursor.close()

        # Retournez le hash de la colonne qr_code
        return str(qr_code_hash[0]) if qr_code_hash else None

    except Exception as e:
        print(f"Erreur lors de la récupération du hash depuis la base de données : {e}")
        return None


def verify_qr_code_from_invoice( user_generated_hash):
    try:
        # Récupérer le hash de la colonne qr_code dans la base de données pour l'ID de la facture donné
        hash_from_database = get_qr_code_hash_from_database(user_generated_hash)

        # Comparer le hash des données du QR code envoyé par l'utilisateur avec le hash de la base de données
        if hash_from_database and user_generated_hash == hash_from_database:
            return True
        else:
            return False

    except Exception as e:
        print(f"Erreur lors de la vérification du code QR : {e}")
        return False



def get_invoices_by_user(user_id):
    try:
        cursor = conn.cursor()
        query = """
        SELECT f.id_commande, f.client_id, f.lieu_livraison, f.etat_commande
        FROM commandes f
        WHERE f.client_id = %s AND f.etat_commande = 'en_cours'
        """
        values = (user_id,)
        cursor.execute(query, values)
        invoices = cursor.fetchall()
        cursor.close()
        return invoices
    except (Exception, mysql.connector.Error) as error:
        print("Une erreur s'est produite lors de la récupération des factures :", error)
        return []



def set_delivery_state(user_generated_hash, etat):
    try:
        cursor = conn.cursor()
        query = "UPDATE commandes SET etat_commande = %s WHERE qr_code = %s"
        values = (etat, user_generated_hash)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return True
    except (Exception, mysql.connector.Error) as error:
        print("Erreur lors de la mise à jour de l'état de livraison :", error)
        return False


def confirm_delivery(invoice_id):
    try:
        cursor = conn.cursor()
        query = "UPDATE facture SET etat_facture = 'En cours' WHERE id_facture = %s"
        cursor.execute(query, (invoice_id,))
        conn.commit()
        cursor.close()
    except (Exception, mysql.connector.Error) as error:
        print("Erreur lors de la confirmation de la livraison :", error)

def get_spot_video():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT spot_video FROM info_generale LIMIT 1")  # Assurez-vous que la table et la colonne sont correctes
        video_path = cursor.fetchone()[0]
        cursor.close()

        base_path = r"Pictures/"  # Remplacez par le chemin correct
    except (Exception, mysql.connector.Error) as error:
        print("Erreur lors de la récupération de la vidéo spot :", error)

    return os.path.join(base_path, video_path) if video_path else None


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

def send_product_images(chat_id, images):
    for image in images:
        with open(image, 'rb') as photo:
            bot.send_photo(chat_id, photo)

try:
    while True:
        bot.polling(none_stop=True)
except KeyboardInterrupt:
    print("Arrêt du bot suite à une interruption manuelle.")
except Exception as e:
    print("Une erreur s'est produite lors de l'exécution du bot :", e)

