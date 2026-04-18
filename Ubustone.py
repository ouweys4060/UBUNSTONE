#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import subprocess
import time
import json
import socket

# ============================================================
# CONFIGURATION - MODIFIEZ CES VALEURS SELON VOTRE SERVEUR
# ============================================================

SERVEUR_DOSSIER    = "CHEMIN DU DOSSIER DE VOTRE SERVEUR"
SERVEUR_EXECUTABLE = "bedrock_server"
SCREEN_NOM         = "minecraft_bedrock"

# Fichiers de configuration du serveur Bedrock
WHITELIST_FICHIER      = os.path.join(SERVEUR_DOSSIER, "whitelist.json")
PERMISSIONS_FICHIER    = os.path.join(SERVEUR_DOSSIER, "permissions.json")
SERVER_PROPS_FICHIER   = os.path.join(SERVEUR_DOSSIER, "server.properties")

# ============================================================
# COULEURS
# ============================================================

class Couleurs:
    rouge  = '\033[91m'
    vert   = '\033[92m'
    jaune  = '\033[93m'
    blanc  = '\033[97m'
    reset  = '\033[0m'

r     = Couleurs.rouge
v     = Couleurs.vert
j     = Couleurs.jaune
b     = Couleurs.blanc
reset = Couleurs.reset

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def clear():
    os.system('clear')

def serveur_est_actif():
    """Vérifie si le serveur est actif via screen"""
    try:
        result = subprocess.run(
            ['screen', '-list'],
            capture_output=True,
            text=True
        )
        return SCREEN_NOM in result.stdout
    except Exception:
        return False

def afficher_statut():
    if serveur_est_actif():
        return f"{v}[EN LIGNE]{reset}"
    else:
        return f"{r}[HORS LIGNE]{reset}"

def attendre_entree():
    input(f"\n{v}Appuyez sur Entrée pour retourner au menu...{reset}")

# ============================================================
# FONCTIONS WHITELIST
# ============================================================

def whitelist_est_active():
    """Vérifie si la whitelist est activée dans server.properties"""
    try:
        with open(SERVER_PROPS_FICHIER, 'r') as f:
            for ligne in f:
                if ligne.startswith('white-list='):
                    return ligne.strip().split('=')[1].lower() == 'true'
    except Exception:
        return False
    return False

def afficher_statut_whitelist():
    """Retourne un texte coloré indiquant si la whitelist est ON ou OFF"""
    if whitelist_est_active():
        return f"{v}[ACTIVÉE]{reset}"
    else:
        return f"{r}[DÉSACTIVÉE]{reset}"

def lire_whitelist():
    """Lit le fichier whitelist.json et retourne la liste des joueurs"""
    try:
        if not os.path.exists(WHITELIST_FICHIER):
            with open(WHITELIST_FICHIER, 'w') as f:
                json.dump([], f)
            return []

        with open(WHITELIST_FICHIER, 'r') as f:
            contenu = f.read().strip()
            if not contenu:
                return []
            return json.loads(contenu)

    except Exception as e:
        print(f"{r}Erreur lecture whitelist : {e}{reset}")
        return []

def sauvegarder_whitelist(joueurs):
    """Sauvegarde la liste des joueurs dans whitelist.json"""
    try:
        with open(WHITELIST_FICHIER, 'w') as f:
            json.dump(joueurs, f, indent=4)
        return True
    except Exception as e:
        print(f"{r}Erreur sauvegarde whitelist : {e}{reset}")
        return False

def modifier_server_properties(cle, valeur):
    """Modifie une valeur dans server.properties"""
    try:
        with open(SERVER_PROPS_FICHIER, 'r') as f:
            lignes = f.readlines()

        nouvelle_lignes = []
        modifie = False

        for ligne in lignes:
            if ligne.startswith(f'{cle}='):
                nouvelle_lignes.append(f'{cle}={valeur}\n')
                modifie = True
            else:
                nouvelle_lignes.append(ligne)

        if not modifie:
            nouvelle_lignes.append(f'{cle}={valeur}\n')

        with open(SERVER_PROPS_FICHIER, 'w') as f:
            f.writelines(nouvelle_lignes)

        return True

    except Exception as e:
        print(f"{r}Erreur modification server.properties : {e}{reset}")
        return False

def envoyer_commande_serveur(commande):
    """Envoie une commande au serveur via screen si actif"""
    if serveur_est_actif():
        subprocess.run(
            ['screen', '-S', SCREEN_NOM, '-X', 'stuff', f'{commande}\n'],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    return False

# ============================================================
# FONCTIONS IP UTILES
# ============================================================

def obtenir_ip_locale():
    """Récupère l'IP locale du serveur"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except Exception:
            return "Introuvable"

def obtenir_ip_publique():
    """Récupère l'IP publique du serveur"""
    try:
        result = subprocess.run(
            ['curl', '-s', 'ifconfig.me'],
            capture_output=True,
            text=True,
            timeout=5
        )
        ip = result.stdout.strip()
        return ip if ip else "Introuvable"
    except Exception:
        try:
            result = subprocess.run(
                ['wget', '-qO-', 'ifconfig.me'],
                capture_output=True,
                text=True,
                timeout=5
            )
            ip = result.stdout.strip()
            return ip if ip else "Introuvable"
        except Exception:
            return "Introuvable"

def obtenir_port_serveur():
    """Récupère le port du serveur depuis server.properties"""
    try:
        with open(SERVER_PROPS_FICHIER, 'r') as f:
            for ligne in f:
                if ligne.startswith('server-port='):
                    return ligne.strip().split('=')[1]
    except Exception:
        return "19132"
    return "19132"

# ============================================================
# MENU
# ============================================================

def afficher_menu():
    clear()
    statut    = afficher_statut()
    statut_wl = afficher_statut_whitelist()

    print(f"""
                     {r}╔════════════════════════════════════════════════════╗{reset}
                     {r}║{b}                      UBUNSTONE                     {r}║{reset}
                     {r}║{b}             Gestionnaire Serveur Bedrock           {r}║{reset}
                     {r}╚════════════════════════════════════════════════════╝{reset}

                 Statut du serveur : {statut}    Whitelist : {statut_wl}

┌────── Serveur ───────┬───── Système ─────┬──── Whitelist ─────┬───── Utile ──────┐

  {r}[{b}01{r}]{b} Lancer  serveur    {r}[{b}04{r}]{b} Infos système    {r}[{b}07{r}]{b} Activer WL       {r}[{b}10{r}]{b} Voir IPs utiles
  {r}[{b}02{r}]{b} Arreter serveur    {r}[{b}05{r}]{b} WIP              {r}[{b}08{r}]{b} Désactiver WL    {r}[{b}11{r}]{b} WIP
  {r}[{b}03{r}]{b} Relancer serveur   {r}[{b}06{r}]{b} WIP              {r}[{b}09{r}]{b} Gérer joueurs    {r}[{b}12{r}]{b} WIP

└──────────────────────┴───────────────────┴────────────────────┴──────────────────┘

  {r}[{b}00{r}]{b} Quitter

""")

# ============================================================
# FONCTIONS SERVEUR
# ============================================================

def lancer_serveur():
    clear()
    print(f"{j}=== LANCER LE SERVEUR ==={reset}\n")

    if serveur_est_actif():
        print(f"{r}Le serveur est déjà en cours d'exécution !{reset}")
        attendre_entree()
        return

    if not os.path.exists(SERVEUR_DOSSIER):
        print(f"{r}Erreur : Le dossier du serveur est introuvable !{reset}")
        print(f"{j}Dossier configuré : {SERVEUR_DOSSIER}{reset}")
        attendre_entree()
        return

    chemin_exe = os.path.join(SERVEUR_DOSSIER, SERVEUR_EXECUTABLE)
    if not os.path.exists(chemin_exe):
        print(f"{r}Erreur : L'exécutable du serveur est introuvable !{reset}")
        print(f"{j}Fichier recherché : {chemin_exe}{reset}")
        attendre_entree()
        return

    try:
        print(f"{b}Démarrage du serveur en cours...{reset}")

        subprocess.Popen(
            [
                'screen', '-dmS', SCREEN_NOM,
                'bash', '-c',
                f'cd {SERVEUR_DOSSIER} && LD_LIBRARY_PATH=. ./{SERVEUR_EXECUTABLE}'
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print(f"{b}Vérification du démarrage...{reset}")
        time.sleep(2)

        if serveur_est_actif():
            print(f"{v}Serveur démarré avec succès !{reset}")
            print(f"\n{b}Commandes utiles :{reset}")
            print(f"  Voir la console    : {j}screen -r {SCREEN_NOM}{reset}")
            print(f"  Quitter la console : {j}Ctrl+A puis D{reset}")
        else:
            print(f"{r}Erreur : Le serveur n'a pas démarré correctement.{reset}")
            print(f"{j}Vérifiez les droits : chmod +x {chemin_exe}{reset}")

    except Exception as e:
        print(f"{r}Erreur inattendue : {e}{reset}")

    attendre_entree()


def arreter_serveur():
    clear()
    print(f"{j}=== ARRÊTER LE SERVEUR ==={reset}\n")

    if not serveur_est_actif():
        print(f"{r}Le serveur n'est pas en cours d'exécution !{reset}")
        attendre_entree()
        return

    confirmation = input(f"{r}Voulez-vous vraiment arrêter le serveur ? (o/n) : {reset}")

    if confirmation.lower() != 'o':
        print(f"{j}Annulé.{reset}")
        attendre_entree()
        return

    print(f"{b}Arrêt du serveur en cours...{reset}")

    subprocess.run(
        ['screen', '-S', SCREEN_NOM, '-X', 'stuff', 'stop\n'],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    for i in range(10):
        time.sleep(1)
        print(f"{b}Attente de l'arrêt... ({i+1}/10){reset}")
        if not serveur_est_actif():
            break

    if not serveur_est_actif():
        print(f"{v}Serveur arrêté avec succès !{reset}")
    else:
        print(f"{r}Le serveur ne répond pas, forçage de l'arrêt...{reset}")
        subprocess.run(
            ['screen', '-S', SCREEN_NOM, '-X', 'quit'],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"{v}Serveur forcé à s'arrêter.{reset}")

    attendre_entree()


def relancer_serveur():
    clear()
    print(f"{j}=== RELANCER LE SERVEUR ==={reset}\n")

    if serveur_est_actif():
        print(f"{b}Arrêt du serveur en cours...{reset}")

        subprocess.run(
            ['screen', '-S', SCREEN_NOM, '-X', 'stuff', 'stop\n'],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        for i in range(10):
            time.sleep(1)
            print(f"{b}Attente de l'arrêt... ({i+1}/10){reset}")
            if not serveur_est_actif():
                break

        if serveur_est_actif():
            subprocess.run(
                ['screen', '-S', SCREEN_NOM, '-X', 'quit'],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        print(f"{v}Serveur arrêté.{reset}")
    else:
        print(f"{j}Le serveur n'était pas actif, démarrage direct...{reset}")

    time.sleep(2)
    print(f"{b}Redémarrage du serveur...{reset}")

    subprocess.Popen(
        [
            'screen', '-dmS', SCREEN_NOM,
            'bash', '-c',
            f'cd {SERVEUR_DOSSIER} && LD_LIBRARY_PATH=. ./{SERVEUR_EXECUTABLE}'
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(2)

    if serveur_est_actif():
        print(f"{v}Serveur redémarré avec succès !{reset}")
        print(f"\n{b}Commandes utiles :{reset}")
        print(f"  Voir la console    : {j}screen -r {SCREEN_NOM}{reset}")
        print(f"  Quitter la console : {j}Ctrl+A puis D{reset}")
    else:
        print(f"{r}Erreur : Le serveur n'a pas redémarré correctement.{reset}")

    attendre_entree()

# ============================================================
# INFORMATIONS SYSTÈME
# ============================================================

def info_systeme():
    clear()
    print(f"{j}=== INFORMATIONS SYSTÈME ==={reset}\n")

    print(f"{b}OS          : {reset}{platform.system()} {platform.release()}")
    print(f"{b}Architecture: {reset}{platform.machine()}")
    print(f"{b}Hostname    : {reset}{platform.node()}")
    print(f"{b}Processeur  : {reset}{platform.processor()}")

    print(f"\n{j}--- Mémoire RAM ---{reset}")
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"{r}Erreur RAM : {e}{reset}")

    print(f"{j}--- Espace Disque ---{reset}")
    try:
        result = subprocess.run(['df', '-h', SERVEUR_DOSSIER], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"{r}Erreur Disque : {e}{reset}")

    print(f"{j}--- Statut Serveur ---{reset}")
    print(f"Serveur Bedrock : {afficher_statut()}")
    print(f"Whitelist       : {afficher_statut_whitelist()}")

    attendre_entree()

# ============================================================
# FONCTIONS WHITELIST
# ============================================================

def activer_whitelist():
    clear()
    print(f"{j}=== ACTIVER LA WHITELIST ==={reset}\n")

    if whitelist_est_active():
        print(f"{r}La whitelist est déjà activée !{reset}")
        attendre_entree()
        return

    print(f"{b}Activation de la whitelist...{reset}")
    
    if modifier_server_properties('white-list', 'true'):
        print(f"{v}✓ Whitelist activée dans server.properties{reset}")
        
        # Si le serveur est en ligne, on recharge la whitelist
        if serveur_est_actif():
            print(f"{b}Rechargement de la whitelist sur le serveur...{reset}")
            envoyer_commande_serveur('whitelist reload')
            time.sleep(0.5)
            print(f"{v}✓ Whitelist rechargée sur le serveur en ligne{reset}")
        else:
            print(f"{j}⚠ Serveur hors ligne - les changements seront appliqués au prochain démarrage{reset}")
        
        print(f"\n{v}La whitelist est maintenant ACTIVÉE !{reset}")
    else:
        print(f"{r}✗ Erreur lors de l'activation de la whitelist.{reset}")

    attendre_entree()


def desactiver_whitelist():
    clear()
    print(f"{j}=== DÉSACTIVER LA WHITELIST ==={reset}\n")

    if not whitelist_est_active():
        print(f"{r}La whitelist est déjà désactivée !{reset}")
        attendre_entree()
        return

    confirmation = input(f"{r}Voulez-vous vraiment désactiver la whitelist ? (o/n) : {reset}")

    if confirmation.lower() != 'o':
        print(f"{j}Annulé.{reset}")
        attendre_entree()
        return

    print(f"{b}Désactivation de la whitelist...{reset}")

    if modifier_server_properties('white-list', 'false'):
        print(f"{v}✓ Whitelist désactivée dans server.properties{reset}")
        
        if serveur_est_actif():
            print(f"{b}Rechargement de la whitelist sur le serveur...{reset}")
            envoyer_commande_serveur('whitelist reload')
            time.sleep(0.5)
            print(f"{v}✓ Whitelist rechargée sur le serveur en ligne{reset}")
        else:
            print(f"{j}⚠ Serveur hors ligne - les changements seront appliqués au prochain démarrage{reset}")
            
        print(f"\n{v}La whitelist est maintenant DÉSACTIVÉE !{reset}")
    else:
        print(f"{r}✗ Erreur lors de la désactivation de la whitelist.{reset}")

    attendre_entree()


def gerer_joueurs():
    """Menu de gestion des joueurs de la whitelist"""
    while True:
        clear()
        joueurs = lire_whitelist()
        
        print(f"{j}=== GÉRER LA WHITELIST ==={reset}\n")
        print(f"{b}Statut : {afficher_statut_whitelist()}")
        print(f"{b}Joueurs dans la liste : {len(joueurs)}{reset}\n")
        
        print(f"  {r}[{b}1{r}]{b} Voir la liste des joueurs")
        print(f"  {r}[{b}2{r}]{b} Ajouter un joueur")
        print(f"  {r}[{b}3{r}]{b} Enlever un joueur")
        print(f"  {r}[{b}0{r}]{b} Retour au menu principal\n")

        choix = input(f"{b}Choisissez une option : {reset}").strip()

        if choix == '1':
            voir_whitelist()
        elif choix == '2':
            ajouter_joueur()
        elif choix == '3':
            enlever_joueur()
        elif choix == '0':
            break
        else:
            print(f"{r}Option invalide !{reset}")
            time.sleep(1)


def voir_whitelist():
    clear()
    print(f"{j}=== LISTE DE LA WHITELIST ==={reset}\n")

    joueurs = lire_whitelist()

    if not joueurs:
        print(f"{r}La whitelist est vide !{reset}")
        print(f"{j}Ajoutez des joueurs pour commencer.{reset}")
        attendre_entree()
        return

    print(f"{b}Joueurs dans la whitelist ({len(joueurs)}) :{reset}\n")

    for i, joueur in enumerate(joueurs, 1):
        nom  = joueur.get('name', 'Inconnu')
        xuid = joueur.get('xuid', 'N/A')
        ignore_limit = joueur.get('ignoresPlayerLimit', False)
        
        icone_limit = f"{v}[VIP]{reset}" if ignore_limit else ""
        print(f"  {r}[{b}{i:02d}{r}]{reset} {nom} {j}(XUID: {xuid}){reset} {icone_limit}")

    attendre_entree()


def ajouter_joueur():
    clear()
    print(f"{j}=== AJOUTER UN JOUEUR À LA WHITELIST ==={reset}\n")

    nom = input(f"{b}Entrez le nom du joueur (ou 0 pour annuler) : {reset}").strip()

    if not nom or nom == '0':
        print(f"{j}Annulé.{reset}")
        time.sleep(1)
        return

    joueurs = lire_whitelist()

    # Vérifie si le joueur existe déjà
    for joueur in joueurs:
        if joueur.get('name', '').lower() == nom.lower():
            print(f"{r}✗ Le joueur '{nom}' est déjà dans la whitelist !{reset}")
            attendre_entree()
            return

    # Création du nouveau joueur
    nouveau_joueur = {
        "ignoresPlayerLimit": False,
        "name": nom,
        "xuid": ""
    }

    joueurs.append(nouveau_joueur)

    if sauvegarder_whitelist(joueurs):
        print(f"{v}✓ Joueur '{nom}' ajouté à la whitelist avec succès !{reset}")
        
        # Recharge la whitelist sur le serveur si actif
        if serveur_est_actif():
            envoyer_commande_serveur('whitelist reload')
            print(f"{v}✓ Whitelist rechargée sur le serveur{reset}")
        else:
            print(f"{j}⚠ Serveur hors ligne - appliquez au prochain démarrage{reset}")
    else:
        print(f"{r}✗ Erreur lors de l'ajout du joueur.{reset}")

    attendre_entree()


def enlever_joueur():
    clear()
    print(f"{j}=== ENLEVER UN JOUEUR DE LA WHITELIST ==={reset}\n")

    joueurs = lire_whitelist()

    if not joueurs:
        print(f"{r}La whitelist est vide !{reset}")
        attendre_entree()
        return

    print(f"{b}Joueurs actuels dans la whitelist :{reset}\n")
    for i, joueur in enumerate(joueurs, 1):
        nom  = joueur.get('name', 'Inconnu')
        print(f"  {r}[{b}{i:02d}{r}]{reset} {nom}")

    print()
    nom = input(f"{b}Entrez le nom du joueur à enlever (ou 0 pour annuler) : {reset}").strip()

    if not nom or nom == '0':
        print(f"{j}Annulé.{reset}")
        time.sleep(1)
        return

    # Cherche et filtre le joueur
    joueurs_filtres = [j for j in joueurs if j.get('name', '').lower() != nom.lower()]

    if len(joueurs_filtres) == len(joueurs):
        print(f"{r}✗ Le joueur '{nom}' n'a pas été trouvé dans la whitelist !{reset}")
        attendre_entree()
        return

    if sauvegarder_whitelist(joueurs_filtres):
        print(f"{v}✓ Joueur '{nom}' retiré de la whitelist avec succès !{reset}")
        
        if serveur_est_actif():
            envoyer_commande_serveur('whitelist reload')
            print(f"{v}✓ Whitelist rechargée sur le serveur{reset}")
        else:
            print(f"{j}⚠ Serveur hors ligne - appliquez au prochain démarrage{reset}")
    else:
        print(f"{r}✗ Erreur lors de la suppression du joueur.{reset}")

    attendre_entree()

# ============================================================
# FONCTIONS UTILES
# ============================================================

def voir_ips_utiles():
    clear()
    print(f"{j}=== IPs UTILES POUR LA CONNEXION ==={reset}\n")

    print(f"{b}Récupération des informations...{reset}\n")

    # IP locale
    ip_locale = obtenir_ip_locale()
    print(f"{v}IP Locale (LAN)  : {reset}{ip_locale}")

    # IP publique
    print(f"{b}Récupération de l'IP publique...{reset}")
    ip_publique = obtenir_ip_publique()
    print(f"{v}IP Publique (WAN): {reset}{ip_publique}")

    # Port du serveur
    port = obtenir_port_serveur()
    print(f"{v}Port du serveur  : {reset}{port}")

    print(f"\n{j}─────────────────────────────────────────────────{reset}")
    print(f"\n{b}Pour se connecter :{reset}")
    print(f"\n  {j}▸ Depuis le réseau local (LAN) :{reset}")
    print(f"    {v}{ip_locale}:{port}{reset}")
    print(f"\n  {j}▸ Depuis Internet (WAN) :{reset}")
    print(f"    {v}{ip_publique}:{port}{reset}")
    print(f"\n{r}⚠ Pour les connexions Internet, pensez à :{reset}")
    print(f"  {b}• Ouvrir le port {port} sur votre routeur (port forwarding){reset}")
    print(f"  {b}• Vérifier les règles du pare-feu (ufw/iptables){reset}")

    attendre_entree()

# ============================================================
# FONCTION PRINCIPALE
# ============================================================

def main():
    while True:
        afficher_menu()
        choix = input(f"{b}Choisissez une option : {reset}").strip()

        options = {
            '1' : lancer_serveur,
            '01': lancer_serveur,
            '2' : arreter_serveur,
            '02': arreter_serveur,
            '3' : relancer_serveur,
            '03': relancer_serveur,
            '4' : info_systeme,
            '04': info_systeme,
            '7' : activer_whitelist,
            '07': activer_whitelist,
            '8' : desactiver_whitelist,
            '08': desactiver_whitelist,
            '9' : gerer_joueurs,
            '09': gerer_joueurs,
            '10': voir_ips_utiles,
            '0' : lambda: exit(0),
            '00': lambda: exit(0),
        }

        if choix in options:
            options[choix]()
        else:
            print(f"{r}Option invalide !{reset}")
            time.sleep(1)

# ============================================================
# POINT D'ENTRÉE
# ============================================================

if __name__ == "__main__":
    try:
        subprocess.run(['screen', '--version'], capture_output=True)
    except FileNotFoundError:
        print(f"{r}ERREUR : 'screen' n'est pas installé !{reset}")
        print(f"{j}Installez-le avec : sudo apt install screen{reset}")
        exit(1)

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{v}Au revoir !{reset}")
        exit(0)
