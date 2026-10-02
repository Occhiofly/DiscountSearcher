#Importazioni
import customtkinter
import tkinter as tk
import datetime
import json
import os
import re
import sys
import socket
import webbrowser
import api_client
import strings
import version
from strings import t
from backend import STORES, GENRES, DISCOUNT, get_deals, get_game_genres

#Stesso controllo del server (api/models.py): un indirizzo Gmail completo, dall'inizio alla fine
GMAIL_ADDRESS = re.compile(r"[A-Za-z0-9._%+-]+@gmail\.com", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Sessione salvata sul computer
# ---------------------------------------------------------------------------
#Il token della sessione sta nella cartella dei dati delle app di Windows
#(%APPDATA%\DiscountSearcher), non nella "cartella corrente": quella cambia a
#seconda di come si avvia l'app (collegamento, doppio clic, dentro lo zip) e a
#volte non è scrivibile. Le versioni precedenti salvavano session.json nella
#cartella corrente: se c'è ancora, viene letto una volta e spostato qui.
SESSION_DIR = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "DiscountSearcher")
SESSION_FILE = os.path.join(SESSION_DIR, "session.json")
SETTINGS_FILE = os.path.join(SESSION_DIR, "settings.json") #lingua scelta
LEGACY_SESSION_FILE = os.path.abspath("session.json")


def _remove_quietly(path):
    try:
        os.remove(path)
    except OSError:
        pass


def load_saved_token():
    """
    Il token salvato, oppure None. Un file vuoto, rovinato o con un contenuto
    inatteso (per esempio dopo uno spegnimento del PC durante il salvataggio)
    viene cancellato: altrimenti l'app si chiuderebbe a ogni avvio.
    """
    for path in (SESSION_FILE, LEGACY_SESSION_FILE):
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                token = json.load(f)["access_token"]
            if isinstance(token, str) and token:
                return token
        except (OSError, ValueError, TypeError, KeyError):
            pass
        _remove_quietly(path) #Contenuto non valido: lo togliamo di mezzo
    return None


def save_token(token):
    """
    Salva il token. Scrive prima un file temporaneo e poi lo rinomina: così non
    resta mai un session.json scritto a metà. Restituisce False se non ci riesce.
    """
    try:
        os.makedirs(SESSION_DIR, exist_ok=True)
        temp_path = SESSION_FILE + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump({"access_token": token}, f)
        os.replace(temp_path, SESSION_FILE)
    except OSError:
        return False
    if os.path.exists(LEGACY_SESSION_FILE):
        _remove_quietly(LEGACY_SESSION_FILE) #Spostato nella cartella nuova
    return True


def delete_saved_token():
    for path in (SESSION_FILE, LEGACY_SESSION_FILE):
        if os.path.exists(path):
            _remove_quietly(path)

def resource_path(relative_path):
    """
    Restituisce il percorso assoluto di una risorsa (es. l'icona), funzionando sia
    quando l'app gira da codice sorgente sia quando è compilata in un .exe:
    - PyInstaller estrae i file inclusi in una cartella temporanea (sys._MEIPASS);
    - Nuitka (build_app.py) li mette accanto al modulo, cioè in __file__.
    Da sorgente vale la cartella di main.py, non quella da cui si avvia l'app.
    """
    base_path = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

#Colore accent viola/indaco
customtkinter.set_appearance_mode("dark") #Tema scuro
customtkinter.set_default_color_theme("dark-blue") #Tema colore

class App(customtkinter.CTk): #Finestra pricipale
    def __init__(self): #Metodo apertura del programma
        """
        Questa funzione é il programma pricipale la sezione login e registrazione
        Informazioni utili:
        self=finestra
        relx=orizzontale
        rely=verticale relativa alla finestra
        anchor=indica quale punto dell'elemento si attacca alle coordinate che dai
        """
        super().__init__() #avvio finestra
        self.access_token = None #Token della sessione corrente, impostato al login o al ripristino da session.json
        self.title("Discount Searcher") #Titolo della finestra
        self.geometry("1000x600") #Grandezza iniziale della finestra
        #Finestra ingrandibile e a schermo intero: i pannelli sono posizionati in
        #percentuale (relx/rely), quindi si adattano da soli. Sotto i 900x560 i campi
        #si sovrapporrebbero, perciò quello è il minimo.
        self.resizable(True, True)
        self.minsize(900, 560)
        #Ingrandita, non "schermo intero" senza bordi: la barra del titolo resta, così
        #si riduce o si chiude come una finestra qualsiasi.
        self._maximized = False
        self._sblocco_attesa = None #Pulsante Ingrandisci/Riduci spento mentre cambia la scala
        self.bind("<F11>", lambda event: self._toggle_maximized())
        #Ingrandendo la finestra devono crescere anche scritte e comandi, altrimenti
        #restano minuscoli in mezzo al vuoto (vedi _adatta_alla_finestra).
        self._scala = 1.0
        self._scala_attesa = None
        self._colonne_modulo = [] #colonne di accesso e registrazione, da tenere centrate
        self.bind("<Configure>", self._on_resize)
        try:
            self.iconbitmap(resource_path("assets/logo.ico")) #Icona ufficiale, mostrata nel titolo e nella barra delle applicazioni
        except Exception:
            pass #Se l'icona manca o non si carica, l'app parte comunque: non è un problema bloccante

        self._searching = False #True mentre una ricerca è in corso (vedi _handle_search)
        strings.init(SETTINGS_FILE) #Lingua salvata, altrimenti quella di Windows
        #Chi aveva lasciato l'app a schermo intero la ritrova così. Dopo la comparsa
        #della finestra (after), altrimenti Windows la mostra di dimensione sbagliata.
        if strings.read_setting("maximized", False):
            self.after(120, self._maximize)
        api_client.language_provider = strings.current #Il server risponde nella stessa lingua

        #Login e registrazione si creano sempre: la finestra compare subito, anche se
        #il ripristino della sessione salvata deve aspettare il server (fino a un minuto
        #quando si sta avviando).
        self._create_panels()
        self._create_login()
        self._create_register()

        #Al primo avvio la lingua la sceglie l'utente. Quella di Windows è solo il
        #suggerimento: chi usa un Windows in inglese può preferire l'italiano, e
        #viceversa. Dalla seconda volta in poi si riparte dalla scelta salvata.
        if not strings.chosen():
            self._create_language_panel()

        #Manutenzione: qualsiasi risposta "aggiornamento in corso" del server, in qualsiasi
        #schermata, mostra l'avviso a schermo intero (vedi api_client.on_maintenance)
        api_client.on_maintenance = lambda message: self.after(0, lambda: self._show_maintenance(message))
        #Il controllo all'avvio aspetta che la finestra sia disegnata: se il server tarda,
        #l'utente vede l'app invece di una finestra vuota
        self.after(150, self._check_service_at_startup)

    def _check_service_at_startup(self):
        """Primo contatto col server: se il team sta aggiornando, lo dice subito."""
        self.update()
        try:
            status = api_client.get_status()
        except (api_client.APIError, api_client.ConnectionErrorAPI):
            status = None #Server irraggiungibile: si prosegue, l'accesso mostrerà il suo messaggio
        if status and status.get("maintenance"):
            self._show_maintenance(status.get("message"))
            return
        if strings.chosen():
            self._start_session() #Al primo avvio parte invece dopo la scelta della lingua
        #Versione nuova pubblicata? Lo dice il server insieme allo stato (api/release.py).
        #Si mostra dopo l'accesso, così non copre la schermata di login.
        self.after(600, lambda: self._check_update(status))

    def _check_update(self, status):
        """Avviso se il server dice che c'è una versione più recente di questa."""
        info = (status or {}).get("app") or {}
        nuova = info.get("version")
        if not version.is_newer(nuova):
            return #Già aggiornata, o il server non dice niente
        if strings.read_setting("update_skipped") == nuova:
            return #L'utente ha già detto di non ricordarglielo per questa versione
        self._show_update_panel(nuova, info.get("url"), info.get("notes") or [])

    def _show_update_panel(self, nuova, url, note):
        """Riquadro a schermo intero con le novità: si chiude e l'app resta usabile."""
        pannello = customtkinter.CTkFrame(self, corner_radius=0)
        self.update_frame = pannello
        customtkinter.CTkLabel(pannello, text=t("update_title"), font=("Arial", 26, "bold")
                               ).place(relx=0.5, rely=0.14, anchor="center")
        customtkinter.CTkLabel(pannello, text=t("update_desc", attuale=version.APP_VERSION, nuova=nuova),
                               font=("Arial", 12), text_color="gray", wraplength=520
                               ).place(relx=0.5, rely=0.25, anchor="center")
        #Le novità arrivano dal server: si mostrano come elenco puntato, testo semplice
        elenco = "\n".join(f"•  {riga}" for riga in note[:6])
        customtkinter.CTkLabel(pannello, text=elenco, font=("Arial", 13), justify="left", wraplength=560
                               ).place(relx=0.5, rely=0.45, anchor="center")
        customtkinter.CTkButton(pannello, text=t("update_download"), width=280, height=38,
                                fg_color="#5B5EA6", hover_color="#4a4d8f",
                                command=lambda: webbrowser.open(url or "https://discountsearcher.it/")
                                ).place(relx=0.5, rely=0.68, anchor="center")
        customtkinter.CTkButton(pannello, text=t("update_later"), width=280, height=35,
                                command=self._close_update_panel).place(relx=0.5, rely=0.77, anchor="center")
        customtkinter.CTkButton(pannello, text=t("update_skip"), width=280, height=32,
                                fg_color="transparent", hover_color="#2b2b2b", text_color="gray",
                                command=lambda: self._close_update_panel(ricorda=nuova)
                                ).place(relx=0.5, rely=0.85, anchor="center")
        pannello.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _close_update_panel(self, ricorda=None):
        """`ricorda`: versione da non segnalare più (il pulsante "Non ricordarmelo")."""
        if ricorda:
            strings.write_setting("update_skipped", ricorda)
        pannello = getattr(self, "update_frame", None)
        if pannello is not None and pannello.winfo_exists():
            pannello.destroy()
        self.update_frame = None

    def _show_maintenance(self, message=None):
        """Avviso a schermo intero mentre il team aggiorna il servizio: blocca tutta l'app."""
        testo = message or t("maintenance_text")
        esistente = getattr(self, "maintenance_frame", None)
        if esistente is not None and esistente.winfo_exists():
            self.maintenance_text.configure(text=testo)
            esistente.lift()
            return
        self.maintenance_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.maintenance_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.maintenance_frame.lift()
        try:
            from PIL import Image
            self._maintenance_logo = customtkinter.CTkImage(Image.open(resource_path("assets/logo.png")), size=(96, 96))
            customtkinter.CTkLabel(self.maintenance_frame, image=self._maintenance_logo, text=""
                                   ).place(relx=0.5, rely=0.26, anchor="center")
        except Exception:
            pass #Senza logo l'avviso funziona lo stesso
        customtkinter.CTkLabel(self.maintenance_frame, text=t("maintenance_title"),
                               font=("Arial", 28, "bold")).place(relx=0.5, rely=0.42, anchor="center")
        self.maintenance_text = customtkinter.CTkLabel(self.maintenance_frame, text=testo, font=("Arial", 13),
                                                       text_color="gray", wraplength=520, justify="center")
        self.maintenance_text.place(relx=0.5, rely=0.52, anchor="center")
        self.maintenance_button = customtkinter.CTkButton(self.maintenance_frame, text=t("maintenance_retry"),
                                                          width=220, height=38, fg_color="#5B5EA6",
                                                          hover_color="#4a4d8f", command=self._retry_after_maintenance)
        self.maintenance_button.place(relx=0.5, rely=0.64, anchor="center")
        self.maintenance_note = customtkinter.CTkLabel(self.maintenance_frame, text="", font=("Arial", 11),
                                                       text_color="gray")
        self.maintenance_note.place(relx=0.5, rely=0.71, anchor="center")

    def _retry_after_maintenance(self):
        """Richiede lo stato: se l'aggiornamento è finito toglie l'avviso e si riprende da dove si era."""
        self.maintenance_note.configure(text=t("maintenance_checking"))
        self.update()
        try:
            status = api_client.get_status()
        except (api_client.APIError, api_client.ConnectionErrorAPI):
            self.maintenance_note.configure(text=t("maintenance_offline"))
            return
        if status.get("maintenance"):
            self.maintenance_text.configure(text=status.get("message") or t("maintenance_text"))
            self.maintenance_note.configure(text=t("maintenance_still"))
            return
        self.maintenance_frame.destroy()
        self.maintenance_frame = None
        #Chi non era ancora entrato riprova l'accesso automatico (se aveva una sessione
        #salvata); chi era già dentro ritrova la schermata com'era
        if self.access_token is None and strings.chosen():
            self._start_session()

    def _start_session(self):
        """Riapre la sessione salvata, se c'è: è il normale avvio dell'app."""
        saved_token = load_saved_token()
        if saved_token:
            self.login_error.configure(text_color="gray", text=t("auto_login"))
            self.after(100, lambda: self._restore_session(saved_token))

    def _create_language_panel(self):
        """
        Schermata del primo avvio: due pulsanti, uno per lingua. È scritta nelle
        due lingue insieme, perché chi la legge non ne ha ancora scelta una.
        Il pulsante evidenziato è quello della lingua di Windows: un suggerimento,
        non una decisione già presa.
        """
        suggerita = strings.system_language()
        self.language_frame = customtkinter.CTkFrame(self, corner_radius=0) #Pannello a schermo intero, sopra login e registrazione
        self.language_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        #Logo dell'app: è la prima schermata che si vede, tanto vale farsi riconoscere
        try:
            from PIL import Image
            self._language_logo = customtkinter.CTkImage(Image.open(resource_path("assets/logo.png")), size=(104, 104))
            customtkinter.CTkLabel(self.language_frame, image=self._language_logo, text=""
                                   ).place(relx=0.5, rely=0.22, anchor="center")
        except Exception:
            pass #Senza logo la schermata funziona lo stesso

        customtkinter.CTkLabel(self.language_frame, text="Discount Searcher",
                               font=("Arial", 30, "bold")).place(relx=0.5, rely=0.38, anchor="center")
        customtkinter.CTkLabel(self.language_frame, text="Scegli la lingua · Choose your language",
                               font=("Arial", 15), text_color="gray").place(relx=0.5, rely=0.46, anchor="center")

        stile_scelto = {"fg_color": "#5B5EA6", "hover_color": "#4a4d8f", "text_color": "white"}
        stile_altro = {"fg_color": "transparent", "hover_color": "#3a3a3a", "text_color": "#c9c9d1",
                       "border_width": 1, "border_color": "#5B5EA6"}

        self.language_it_button = customtkinter.CTkButton(
            self.language_frame, text="Italiano", width=190, height=48, font=("Arial", 15),
            command=lambda: self._choose_language("it"),
            **(stile_scelto if suggerita == "it" else stile_altro))
        self.language_it_button.place(relx=0.35, rely=0.59, anchor="center")

        self.language_en_button = customtkinter.CTkButton(
            self.language_frame, text="English", width=190, height=48, font=("Arial", 15),
            command=lambda: self._choose_language("en"),
            **(stile_scelto if suggerita == "en" else stile_altro))
        self.language_en_button.place(relx=0.65, rely=0.59, anchor="center")

        customtkinter.CTkLabel(self.language_frame, font=("Arial", 11), text_color="gray",
                               text="Puoi cambiarla quando vuoi, dal selettore in alto a destra nella schermata di accesso."
                               ).place(relx=0.5, rely=0.73, anchor="center")
        customtkinter.CTkLabel(self.language_frame, font=("Arial", 11), text_color="gray",
                               text="You can change it any time, from the switch at the top right of the sign-in screen."
                               ).place(relx=0.5, rely=0.775, anchor="center")

        #Invio sceglie la lingua suggerita: chi è d'accordo non deve nemmeno cercare il mouse
        self.bind("<Return>", lambda event: self._choose_language(suggerita))
        (self.language_it_button if suggerita == "it" else self.language_en_button).focus_set()

    def _choose_language(self, lang):
        """Salva la lingua scelta al primo avvio e lascia partire l'app."""
        cambia = lang != strings.current()
        strings.set_language(lang) #Da qui in poi l'app non lo chiede più
        self.unbind("<Return>")
        self.language_frame.destroy()
        if cambia:
            #I testi dei widget sono fissati alla creazione: si rifanno, come nel cambio lingua
            for widget in self.winfo_children():
                widget.destroy()
            self._create_panels()
            self._create_login()
            self._create_register()
        self._start_session()

    def _restore_session(self, token):
        """Riapre la sessione salvata, se il server la considera ancora valida."""
        self.update() #Mostra la finestra e il messaggio prima dell'attesa del server
        try:
            self.current_user = api_client.get_me(token) #Verifichiamo che il token sia ancora valido, e recuperiamo i dati utente
        except api_client.APIError as e:
            if e.status_code in (401, 403):
                #Sessione scaduta o chiusa (es. password cambiata da un altro computer)
                delete_saved_token()
                self.login_error.configure(text_color="orange", text=t("saved_session_invalid"))
            else:
                #Problema momentaneo del server: il token resta salvato, si riprova al prossimo avvio
                self.login_error.configure(text_color="orange", text=t("server_problem"))
            return
        except api_client.ConnectionErrorAPI:
            self.login_error.configure(text_color="orange", text=t("connection_error"))
            return
        self.access_token = token
        save_token(token) #Se era nel vecchio percorso, lo sposta in quello nuovo
        self.login_error.configure(text="")
        self.login_frame.place_forget() #Nascondiamo login
        self.register_frame.place_forget() #Nascondiamo registrazione
        self._create_main_menu() #Mostriamo direttamente il menu principale

    def _create_panels(self):
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=0) #Creazione pannello del login sulla finestra
        self.login_frame.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0) #Posizione pannello a sinistra, metà finestra partendo dall'angolo in alto a sinistra!
        self.register_frame = customtkinter.CTkFrame(self, corner_radius=0) #Creazione pannello della registrazione sulla finestra
        self.register_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1.0) #Posizione pannello a meta finestra
        self._create_verify_email_panel() #Pannello (a schermo intero, nascosto) per l'inserimento del codice di verifica email
        self._create_forgot_password_panel() #Pannello (a schermo intero, nascosto) per la procedura "Password dimenticata"

    def _create_verify_email_panel(self):
        self.verify_email_frame = customtkinter.CTkFrame(self, corner_radius=0) #Pannello a schermo intero, sopra login+registrazione
        self.verify_email_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.verify_email_title = customtkinter.CTkLabel(self.verify_email_frame, text=t("verify_title"), font=("Arial", 28, "bold")) #Titolo
        self.verify_email_title.place(relx=0.5, rely=0.30, anchor="center")
        self.verify_email_desc_label = customtkinter.CTkLabel(self.verify_email_frame, text="", font=("Arial", 12), text_color="gray", wraplength=520) #Descrizione, riempita di volta in volta con l'email a cui abbiamo scritto
        self.verify_email_desc_label.place(relx=0.5, rely=0.40, anchor="center")
        self.verify_email_code_label = customtkinter.CTkLabel(self.verify_email_frame, text=t("verify_code_label"), font=("Arial", 14)) #Etichetta campo codice
        self.verify_email_code_label.place(relx=0.5, rely=0.49, anchor="center")
        self.verify_email_code_entry = customtkinter.CTkEntry(self.verify_email_frame, width=250, height=35, justify="center") #Campo codice
        self.verify_email_code_entry.place(relx=0.5, rely=0.55, anchor="center")
        self.verify_email_message = customtkinter.CTkLabel(self.verify_email_frame, text="", font=("Arial", 12), wraplength=420) #Messaggio di stato/errore
        self.verify_email_message.place(relx=0.5, rely=0.62, anchor="center")
        self.verify_email_confirm_button = customtkinter.CTkButton(self.verify_email_frame, text=t("verify_button"), width=250, height=35, fg_color="#5B5EA6", hover_color="#4a4d8f", command=self._handle_verify_email_code) #Bottone Verifica
        self.verify_email_confirm_button.place(relx=0.5, rely=0.70, anchor="center")
        self.verify_email_resend_button = customtkinter.CTkButton(self.verify_email_frame, text=t("resend_button"), width=250, height=35, command=self._handle_resend_code) #Bottone reinvio codice
        self.verify_email_resend_button.place(relx=0.5, rely=0.78, anchor="center")
        self.verify_email_back_button = customtkinter.CTkButton(self.verify_email_frame, text=t("back_to_login"), width=250, height=35, command=self._cancel_verify_email) #Bottone Indietro
        self.verify_email_back_button.place(relx=0.5, rely=0.86, anchor="center")
        self.verify_email_frame.place_forget() #Nascondiamo il pannello di verifica all'avvio

    def _create_forgot_password_panel(self):
        self.forgot_password_frame = customtkinter.CTkFrame(self, corner_radius=0) #Pannello a schermo intero, sopra login+registrazione
        self.forgot_password_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.forgot_password_title = customtkinter.CTkLabel(self.forgot_password_frame, text=t("forgot_title"), font=("Arial", 28, "bold")) #Titolo
        self.forgot_password_title.place(relx=0.5, rely=0.10, anchor="center")
        self.forgot_password_desc = customtkinter.CTkLabel(self.forgot_password_frame, text=t("forgot_desc"), font=("Arial", 12), text_color="gray", wraplength=450) #Descrizione
        self.forgot_password_desc.place(relx=0.5, rely=0.18, anchor="center")
        self.forgot_password_username_label = customtkinter.CTkLabel(self.forgot_password_frame, text=t("username"), font=("Arial", 14)) #Etichetta username
        self.forgot_password_username_label.place(relx=0.5, rely=0.26, anchor="center")
        self.forgot_password_username_entry = customtkinter.CTkEntry(self.forgot_password_frame, width=250, height=35) #Campo username
        self.forgot_password_username_entry.place(relx=0.5, rely=0.31, anchor="center")
        self.forgot_password_send_button = customtkinter.CTkButton(self.forgot_password_frame, text=t("forgot_send"), width=250, height=35, command=self._handle_forgot_password_send) #Bottone invio codice
        self.forgot_password_send_button.place(relx=0.5, rely=0.38, anchor="center")
        self.forgot_password_message = customtkinter.CTkLabel(self.forgot_password_frame, text="", font=("Arial", 12), wraplength=420) #Messaggio di stato/errore, condiviso da entrambi i passaggi
        self.forgot_password_message.place(relx=0.5, rely=0.45, anchor="center")
        self.forgot_password_code_label = customtkinter.CTkLabel(self.forgot_password_frame, text=t("code_received"), font=("Arial", 14)) #Etichetta codice
        self.forgot_password_code_label.place(relx=0.5, rely=0.52, anchor="center")
        self.forgot_password_code_entry = customtkinter.CTkEntry(self.forgot_password_frame, width=250, height=35, justify="center") #Campo codice
        self.forgot_password_code_entry.place(relx=0.5, rely=0.57, anchor="center")
        self.forgot_password_new_password_label = customtkinter.CTkLabel(self.forgot_password_frame, text=t("new_password"), font=("Arial", 14)) #Etichetta nuova password
        self.forgot_password_new_password_label.place(relx=0.5, rely=0.64, anchor="center")
        self.forgot_password_new_password_entry = self._create_password_field(self.forgot_password_frame, rely=0.69) #Campo nuova password con lucchetto
        self.forgot_password_reset_button = customtkinter.CTkButton(self.forgot_password_frame, text=t("reset_button"), width=250, height=35, fg_color="#5B5EA6", hover_color="#4a4d8f", command=self._handle_forgot_password_reset) #Bottone conferma reset
        self.forgot_password_reset_button.place(relx=0.5, rely=0.76, anchor="center")
        self.forgot_password_back_button = customtkinter.CTkButton(self.forgot_password_frame, text=t("back_to_login"), width=250, height=35, command=self._cancel_forgot_password) #Bottone Indietro
        self.forgot_password_back_button.place(relx=0.5, rely=0.85, anchor="center")
        self.forgot_password_frame.place_forget() #Nascondiamo il pannello all'avvio

    def _create_password_field(self, parent, rely=None, width=250, height=35,
                               placeholder_text=None, pady=None):
        """
        Crea un campo password con il lucchetto per mostrarla/nasconderla mentre si digita.
        Restituisce l'entry (per leggere il valore con .get() come sempre) — il resto
        (il contenitore, il simbolo) è gestito internamente e non serve toccarlo altrove.

        Con `rely` si posiziona da solo nel pannello (schermate costruite con place);
        con `pady` si impila nella colonna del genitore (accesso e registrazione).
        """
        row = customtkinter.CTkFrame(parent, fg_color="transparent", width=width, height=height)
        if rely is not None:
            row.place(relx=0.5, rely=rely, anchor="center")
        else:
            row.pack(pady=pady if pady is not None else 0)
        row.pack_propagate(False) #Mantiene fissa la dimensione del contenitore, anche se dentro c'è meno spazio

        entry = customtkinter.CTkEntry(row, show="*", placeholder_text=placeholder_text)
        entry.pack(fill="both", expand=True)

        #Il lucchetto sta DENTRO la casella, sul bordo destro: fuori renderebbe il campo
        #password più corto di tutti gli altri, e le caselle non sarebbero più allineate.
        toggle = customtkinter.CTkLabel(row, text="🔒", width=20, cursor="hand2", font=("Arial", 14)) #🔒 all'avvio: coerente con show="*" (nascosta)
        toggle.place(relx=1.0, rely=0.5, anchor="e", x=-8)
        toggle.bind("<Button-1>", lambda event: self._toggle_password_visibility(entry, toggle))

        return entry

    def _toggle_password_visibility(self, entry, toggle_label):
        if entry.cget("show") == "": #Attualmente visibile in chiaro: la nascondiamo di nuovo
            entry.configure(show="*")
            toggle_label.configure(text="🔒")
        else: #Attualmente nascosta: la mostriamo in chiaro
            entry.configure(show="")
            toggle_label.configure(text="🔓")

    def _make_digit_var(self, max_length, max_value=None):
        """
        Crea una StringVar collegata a un CTkEntry che si autocorregge in tempo reale:
        solo cifre, massimo max_length caratteri, e se max_value è specificato il numero
        non può superarlo (es. Giorno<=31, Mese<=12, Anno<=2026).
        """
        var = tk.StringVar()
        var.trace_add("write", lambda *args: self._enforce_max_digits(var, max_length, max_value))
        return var

    def _enforce_max_digits(self, var, max_length, max_value=None):
        value = var.get()
        fixed = "".join(ch for ch in value if ch.isdigit())[:max_length] #Solo cifre, massimo max_length caratteri

        if max_value is not None and fixed and int(fixed) > max_value:
            fixed = str(max_value) #Il numero supera il massimo consentito: lo riportiamo al limite

        if fixed != value:
            var.set(fixed) #Corregge il campo mentre l'utente digita

    #Spazi della colonna di accesso e registrazione, in unità di widget: CustomTkinter
    #li moltiplica per la scala, quindi restano in proporzione a qualsiasi dimensione.
    #Erano percentuali dell'altezza della finestra, e con le caselle alte 35 le etichette
    #finivano addosso al campo sopra.
    _SPAZIO_SOPRA_ETICHETTA = 14
    _SPAZIO_SOTTO_ETICHETTA = 4

    def _crea_colonna(self, parent):
        """
        Colonna centrata in cui impilare i campi. Lo spazio tra una voce e l'altra lo
        decide pack a partire dall'altezza vera dei widget: niente più sovrapposizioni
        quando la finestra è bassa o quando le scritte crescono.
        """
        colonna = customtkinter.CTkFrame(parent, fg_color="transparent")
        #Ancorata in alto e non al centro: le due colonne (accesso e registrazione) hanno
        #altezze diverse, e centrandole ciascuna sul proprio contenuto i due titoli
        #finirebbero a quote diverse. Partono dalla stessa riga, decisa da _centra_colonne.
        colonna.place(relx=0.5, rely=0.14, anchor="n")
        self._colonne_modulo.append(colonna)
        return colonna

    def _centra_colonne(self):
        """
        Mette le due colonne alla stessa altezza, centrando la più alta nella finestra.
        Si rifà a ogni ridimensionamento: con una finestra bassa una quota fissa farebbe
        uscire la registrazione dal bordo, con una alta la lascerebbe tutta in cima.
        """
        colonne = [c for c in self._colonne_modulo if c.winfo_exists()]
        self._colonne_modulo = colonne
        if not colonne:
            return
        self.update_idletasks() #servono le altezze vere del contenuto
        altezza = self.winfo_height()
        if altezza <= 1:
            return
        piu_alta = max(c.winfo_reqheight() for c in colonne)
        #Almeno un po' d'aria in cima; se il contenuto non ci sta, si parte comunque dall'alto
        rely = max(0.02, (altezza - piu_alta) / 2 / altezza)
        for colonna in colonne:
            colonna.place(relx=0.5, rely=rely, anchor="n")

    def _crea_etichetta_campo(self, colonna, testo, primo=False):
        """Etichetta sopra una casella, con l'aria giusta: più sopra, poca sotto."""
        etichetta = customtkinter.CTkLabel(colonna, text=testo, font=("Arial", 14))
        etichetta.pack(pady=(0 if primo else self._SPAZIO_SOPRA_ETICHETTA, self._SPAZIO_SOTTO_ETICHETTA))
        return etichetta

    def _create_login(self):
        colonna = self._crea_colonna(self.login_frame)
        self.login_title = customtkinter.CTkLabel(colonna, text=t("login_title"), font=("Arial", 28, "bold")) #Titolo della colonna
        self.login_title.pack(pady=(0, 18))
        self.login_username = self._crea_etichetta_campo(colonna, t("username"), primo=True)
        self.login_username_entry = customtkinter.CTkEntry(colonna, width=250, height=35) #Casella dove utente puo scrivere
        self.login_username_entry.pack()
        self.login_password = self._crea_etichetta_campo(colonna, t("password"))
        self.login_password_entry = self._create_password_field(colonna) #Campo password con lucchetto
        self.login_button = customtkinter.CTkButton(colonna, text=t("login_title"), width=250, height=35, fg_color="#5B5EA6", hover_color="#4a4d8f", command=self._handle_login) #Bottone Accedi
        self.login_button.pack(pady=(22, 0))
        self.login_footer = customtkinter.CTkLabel(colonna, text=t("login_footer"), font=("Arial", 11), text_color="gray") #Creazione footer
        self.login_footer.pack(pady=(14, 0))
        self.login_forgot_password = customtkinter.CTkLabel(colonna, text=t("forgot_link"), font=("Arial", 11), text_color="gray", cursor="hand2") #Link password dimenticata
        self.login_forgot_password.pack(pady=(6, 0))
        self.login_forgot_password.bind("<Button-1>", lambda event: self._open_forgot_password_panel()) #Click apre il pannello di reset
        #Cambio lingua: sempre visibile anche prima di accedere, in alto a destra come nella
        #maggior parte delle applicazioni. Sta nel pannello di registrazione, così sparisce
        #sotto le schermate a tutta finestra (verifica email, password dimenticata).
        self.language_selector = self._create_language_selector(self.register_frame)
        self.language_selector.place(relx=0.96, rely=0.05, anchor="ne")
        self.login_error = customtkinter.CTkLabel(colonna, text="", text_color="red", font=("Arial", 12)) #Errore
        self.login_error.pack(pady=(12, 0))

    def _create_language_selector(self, parent, width=180, font_size=12):
        """
        Selettore "Italiano | English": la lingua attiva è evidenziata, l'altra si sceglie
        con un clic. I nomi restano ciascuno nella propria lingua, così chiunque trova la sua.
        """
        selettore = customtkinter.CTkSegmentedButton(
            parent, values=["Italiano", "English"], width=width, height=28, font=("Arial", font_size),
            selected_color="#5B5EA6", selected_hover_color="#4a4d8f",
            unselected_color="#2b2b2b", unselected_hover_color="#3a3a3a",
            command=lambda scelta: self._switch_language("it" if scelta == "Italiano" else "en"))
        selettore.set("Italiano" if strings.current() == "it" else "English")
        return selettore

    def _switch_language(self, target=None):
        """
        Passa alla lingua indicata (o all'altra) e ricostruisce la finestra: i testi dei
        widget di CustomTkinter si fissano alla creazione, quindi ricrearli è il modo più
        semplice e sicuro per tradurre tutto, compreso quello che è già a schermo.
        """
        target = target or strings.other()
        if target == strings.current():
            return #Clic sulla lingua già attiva: niente da fare
        if self._searching:
            #A metà ricerca i pannelli sono in uso: il selettore torna sulla lingua attuale
            for nome in ("language_selector", "sidebar_language_selector"):
                selettore = getattr(self, nome, None)
                if selettore is not None and selettore.winfo_exists():
                    selettore.set("Italiano" if strings.current() == "it" else "English")
            return
        strings.set_language(target)
        logged_in = self.access_token is not None
        for widget in self.winfo_children():
            widget.destroy()
        self._create_panels()
        self._create_login()
        self._create_register()
        if logged_in:
            self.login_frame.place_forget()
            self.register_frame.place_forget()
            self._create_main_menu()

    def _handle_login(self):
        username = self.login_username_entry.get() #Prendiamo il Username
        password = self.login_password_entry.get() #Prendiamo la password

        #Messaggio mostrato subito: se il server si sta avviando la risposta può
        #richiedere fino a un minuto, e senza sembrerebbe che il clic non abbia fatto niente
        self.login_error.configure(text_color="gray", text=t("login_in_progress"))
        self.update()

        try:
            result = api_client.login(username, password, device_info=socket.gethostname()) #Chiamata all'API
            token = result["access_token"]
            self.current_user = api_client.get_me(token) #Recuperiamo i dati completi dell'utente
            self.access_token = token
            saved = save_token(token) #Per non chiedere il login al prossimo avvio
            self.login_error.configure(text_color="green", text=t("login_done")) #Messaggio di login
            self.login_frame.place_forget() #nascondiamo login
            self.register_frame.place_forget() #nascondiamo registrazione
            self._create_main_menu() #mostriamo menu principale
            if not saved:
                #L'accesso funziona lo stesso: si perde solo l'accesso automatico
                self.status_label.configure(text_color="orange", text=t("session_not_saved"))
        except api_client.APIError as e:
            if e.error_code == "email_not_verified":
                #Credenziali corrette ma email non ancora verificata: mandiamo un nuovo codice e apriamo la schermata di verifica
                self._pending_verification_username = username
                self._pending_verification_email = e.email
                try:
                    resend_result = api_client.resend_code(username)
                    send_error = None if resend_result.get("email_sent", True) else "invio email non riuscito"
                except api_client.APIError as resend_err:
                    send_error = str(resend_err)
                self._open_verify_email_panel(send_error)
            elif e.status_code == 429:
                #Troppi tentativi falliti: mostriamo il messaggio reale del server (include l'attesa),
                #non il generico "credenziali errate", altrimenti l'utente non capirebbe cosa sta succedendo
                self.login_error.configure(text_color="red", text=str(e))
            else:
                self.login_error.configure(text_color="red", text=t("login_failed")) #Log Errore
        except api_client.ConnectionErrorAPI:
            self.login_error.configure(text_color="red", text=t("connection_error"))

    def _create_register(self):
        colonna = self._crea_colonna(self.register_frame)
        self.register_title = customtkinter.CTkLabel(colonna, text=t("register_title"), font=("Arial", 28, "bold")) #Titolo della colonna
        self.register_title.pack(pady=(0, 18))
        self.register_username = self._crea_etichetta_campo(colonna, t("username"), primo=True)
        self.register_username_entry = customtkinter.CTkEntry(colonna, width=250, height=35) #Casella dove utente puo scrivere
        self.register_username_entry.pack()
        self.register_password = self._crea_etichetta_campo(colonna, t("password"))
        self.register_password_entry = self._create_password_field(colonna) #Campo password con lucchetto
        self.register_email = self._crea_etichetta_campo(colonna, t("email"))
        self.register_email_entry = customtkinter.CTkEntry(colonna, width=250, height=35) #Casella dove utente puo scrivere la sua email
        self.register_email_entry.pack()
        self.register_birth_date = self._crea_etichetta_campo(colonna, t("birth_date"))

        #Giorno, mese e anno affiancati: una riga con tre colonnine, così restano
        #allineati tra loro qualunque sia la larghezza della finestra.
        riga_data = customtkinter.CTkFrame(colonna, fg_color="transparent")
        riga_data.pack()
        self.register_day_var = self._make_digit_var(2, max_value=31) #Massimo 2 cifre, e non oltre 31
        self.register_month_var = self._make_digit_var(2, max_value=12) #Massimo 2 cifre, e non oltre 12
        self.register_year_var = self._make_digit_var(4, max_value=datetime.date.today().year) #Massimo 4 cifre, e non oltre l'anno corrente
        pezzi = [("day", "register_day", "register_day_entry", self.register_day_var, 60),
                 ("month", "register_month", "register_month_entry", self.register_month_var, 60),
                 ("year", "register_year", "register_year_entry", self.register_year_var, 90)]
        for chiave, nome_etichetta, nome_casella, variabile, larghezza in pezzi:
            colonnina = customtkinter.CTkFrame(riga_data, fg_color="transparent")
            colonnina.pack(side="left", padx=6)
            etichetta = customtkinter.CTkLabel(colonnina, text=t(chiave), font=("Arial", 12))
            etichetta.pack(pady=(0, self._SPAZIO_SOTTO_ETICHETTA))
            casella = customtkinter.CTkEntry(colonnina, width=larghezza, height=35, textvariable=variabile)
            casella.pack()
            setattr(self, nome_etichetta, etichetta)
            setattr(self, nome_casella, casella)

        self.register_button = customtkinter.CTkButton(colonna, text=t("register_title"), width=250, height=35, fg_color="#5B5EA6", hover_color="#4a4d8f", command=self._handle_register) #Bottone Registrati
        self.register_button.pack(pady=(22, 0))
        self.register_error = customtkinter.CTkLabel(colonna, text="", text_color="red", font=("Arial", 12)) #Errore registrazione
        self.register_error.pack(pady=(12, 0))
        #Il selettore della lingua nasce con il pannello di accesso, quindi sta SOTTO la
        #colonna appena creata: la colonna è trasparente ma disegna lo sfondo, e lo
        #coprirebbe a metà. lift() lo riporta in cima.
        selettore = getattr(self, "language_selector", None)
        if selettore is not None and selettore.winfo_exists():
            selettore.lift()
        #Appena la finestra ha disegnato: le due colonne alla stessa altezza, centrate
        self.after(80, self._centra_colonne)

    def _handle_register(self):
        username = self.register_username_entry.get() #Prendiamo il username
        password = self.register_password_entry.get() #Prendiamo la password
        email = self.register_email_entry.get() #Prendiamo l'email
        day = self.register_day_entry.get() #Prendiamo il giorno
        month = self.register_month_entry.get() #Prendiamo il mese
        year = self.register_year_entry.get() #Prendiamo l'anno

        #Controllo campi vuoti
        if not username or not password or not email or not day or not month or not year:
            self.register_error.configure(text_color="red", text=t("fill_all_fields")) #Errore campi vuoti
            return

        #Controllo che l'email sia un indirizzo Gmail
        if not GMAIL_ADDRESS.fullmatch(email.strip()):
            self.register_error.configure(text_color="red", text=t("gmail_required")) #Errore email non Gmail
            return

        #L'API si aspetta la data in formato ISO (AAAA-MM-GG): aggiungiamo gli zeri
        #davanti se mancano (es. "5" diventa "05"), altrimenti il formato non è valido
        birth_date = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"

        try:
            api_client.register(username, password, email, birth_date) #Registrazione (account creato ma non ancora verificato, codice inviato dal server)
        except api_client.APIError as e:
            #409 vuol dire "qualcosa è già in uso": l'username oppure l'email. Quale dei
            #due lo dice il server, nella lingua dell'app, quindi si mostra il suo
            #messaggio; t("username_taken") resta come riserva se non ne manda uno.
            self.register_error.configure(text_color="red", text=str(e).strip() or t("username_taken"))
            return
        except api_client.ConnectionErrorAPI:
            self.register_error.configure(text_color="red", text=t("connection_error"))
            return

        #Salviamo i dati dell'account appena creato, servono per la schermata di verifica
        self._pending_verification_username = username
        self._pending_verification_email = email

        #Non sappiamo se l'invio dell'email sia andato a buon fine: se ne occupa il server,
        #che non ce lo comunica in fase di registrazione (solo per il reinvio, vedi resend_code)
        self._open_verify_email_panel()

    def _open_verify_email_panel(self, error_message=None):
        self.login_frame.place_forget() #Nascondiamo login
        self.register_frame.place_forget() #Nascondiamo registrazione
        self.verify_email_code_entry.delete(0, "end") #Svuotiamo il campo codice
        self.verify_email_desc_label.configure(text=t("verify_desc", email=self._pending_verification_email))
        if error_message: #L'invio dell'email è fallito: l'account esiste comunque, informiamo l'utente
            self.verify_email_message.configure(text_color="orange", text=t("send_failed", reason=error_message))
        else:
            self.verify_email_message.configure(text_color="gray", text="")
        self.verify_email_frame.place(relx=0, rely=0, relwidth=1, relheight=1) #Mostriamo il pannello di verifica

    def _handle_verify_email_code(self):
        code = self.verify_email_code_entry.get().strip() #Prendiamo il codice inserito

        #Controllo campo vuoto
        if not code:
            self.verify_email_message.configure(text_color="red", text=t("enter_code"))
            return

        try:
            api_client.verify_email(self._pending_verification_username, code) #Verifichiamo il codice
        except api_client.APIError as e:
            self.verify_email_message.configure(text_color="red", text=str(e)) #Codice errato o scaduto
            return
        except api_client.ConnectionErrorAPI:
            self.verify_email_message.configure(text_color="red", text=t("connection_error"))
            return

        #Verifica riuscita: torniamo al login, pronti per accedere
        self.verify_email_frame.place_forget() #Nascondiamo il pannello di verifica
        self.verify_email_code_entry.delete(0, "end") #Svuotiamo il campo codice
        self.login_frame.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0) #Rmostriamo login
        self.register_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1.0) #Rmostriamo registrazione
        self.login_username_entry.delete(0, "end") #Svuotiamo il campo username del login
        self.login_username_entry.insert(0, self._pending_verification_username) #Precompiliamo con lo username appena verificato
        self.login_error.configure(text_color="green", text=t("verify_done")) #Messaggio di successo

    def _handle_resend_code(self):
        try:
            result = api_client.resend_code(self._pending_verification_username) #Generiamo e inviamo un nuovo codice
        except api_client.APIError as e:
            self.verify_email_message.configure(text_color="red", text=str(e))
            return
        except api_client.ConnectionErrorAPI:
            self.verify_email_message.configure(text_color="red", text=t("connection_error"))
            return

        if result.get("email_sent", True):
            self.verify_email_message.configure(text_color="green", text=t("code_sent"))
        else:
            self.verify_email_message.configure(text_color="orange", text=t("code_not_sent"))

    def _cancel_verify_email(self):
        self.verify_email_frame.place_forget() #Nascondiamo il pannello di verifica
        self.verify_email_code_entry.delete(0, "end") #Svuotiamo il campo codice
        self.verify_email_message.configure(text="") #Azzeriamo l'eventuale messaggio
        self.login_frame.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0) #Rmostriamo login
        self.register_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1.0) #Rmostriamo registrazione

    def _open_forgot_password_panel(self):
        self.login_frame.place_forget() #Nascondiamo login
        self.register_frame.place_forget() #Nascondiamo registrazione
        self.forgot_password_username_entry.delete(0, "end") #Svuotiamo il campo username
        self.forgot_password_code_entry.delete(0, "end") #Svuotiamo il campo codice
        self.forgot_password_new_password_entry.delete(0, "end") #Svuotiamo il campo nuova password
        self.forgot_password_message.configure(text="") #Azzeriamo l'eventuale messaggio precedente
        self.forgot_password_frame.place(relx=0, rely=0, relwidth=1, relheight=1) #Mostriamo il pannello

    def _handle_forgot_password_send(self):
        username = self.forgot_password_username_entry.get().strip() #Prendiamo lo username

        if not username:
            self.forgot_password_message.configure(text_color="red", text=t("enter_username"))
            return

        try:
            result = api_client.forgot_password(username) #Chiediamo all'API di inviare il codice
            #Messaggio generico dal server (uguale sia che l'account esista o no): lo mostriamo così com'è
            self.forgot_password_message.configure(text_color="green", text=result.get("message", t("forgot_generic")))
        except api_client.APIError as e:
            self.forgot_password_message.configure(text_color="red", text=str(e))
        except api_client.ConnectionErrorAPI:
            self.forgot_password_message.configure(text_color="red", text=t("connection_error"))

    def _handle_forgot_password_reset(self):
        username = self.forgot_password_username_entry.get().strip() #Prendiamo lo username
        code = self.forgot_password_code_entry.get().strip() #Prendiamo il codice ricevuto
        new_password = self.forgot_password_new_password_entry.get() #Prendiamo la nuova password

        if not username or not code or not new_password:
            self.forgot_password_message.configure(text_color="red", text=t("fill_reset_fields"))
            return

        try:
            api_client.reset_password(username, code, new_password) #Verifica del codice e reimpostazione, in un'unica chiamata
        except api_client.APIError as e:
            self.forgot_password_message.configure(text_color="red", text=str(e)) #Codice errato/scaduto, o troppi tentativi
            return
        except api_client.ConnectionErrorAPI:
            self.forgot_password_message.configure(text_color="red", text=t("connection_error"))
            return

        #Reset riuscito: torniamo al login, pronti per accedere con la nuova password
        self.forgot_password_frame.place_forget() #Nascondiamo il pannello
        self.forgot_password_code_entry.delete(0, "end") #Svuotiamo il campo codice
        self.forgot_password_new_password_entry.delete(0, "end") #Svuotiamo il campo nuova password
        self.login_frame.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0) #Rmostriamo login
        self.register_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1.0) #Rmostriamo registrazione
        self.login_username_entry.delete(0, "end") #Svuotiamo il campo username del login
        self.login_username_entry.insert(0, username) #Precompiliamo con lo username appena usato
        self.login_error.configure(text_color="green", text=t("reset_done")) #Messaggio di successo

    def _cancel_forgot_password(self):
        self.forgot_password_frame.place_forget() #Nascondiamo il pannello
        self.forgot_password_username_entry.delete(0, "end") #Svuotiamo il campo username
        self.forgot_password_code_entry.delete(0, "end") #Svuotiamo il campo codice
        self.forgot_password_new_password_entry.delete(0, "end") #Svuotiamo il campo nuova password
        self.forgot_password_message.configure(text="") #Azzeriamo l'eventuale messaggio
        self.login_frame.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0) #Rmostriamo login
        self.register_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1.0) #Rmostriamo registrazione

    #Scala minima e massima dei widget. Sotto 1.0 i testi diventerebbero illeggibili;
    #oltre 1.6 i campi e i pulsanti diventano goffi e l'elenco mostra pochi giochi.
    _SCALA_MIN = 1.0
    _SCALA_MAX = 1.6
    #Dimensione di riferimento: la finestra piccola, dove la grafica è già giusta.
    _BASE_LARGHEZZA = 1000
    _BASE_ALTEZZA = 600

    def _on_resize(self, event):
        """
        Ridimensionamento: si aspetta che l'utente abbia finito di trascinare (250 ms)
        prima di ridisegnare tutto, altrimenti l'app ricalcolerebbe a ogni pixel.
        """
        if event.widget is not self:
            return #Arrivano anche gli eventi dei widget interni: ci interessa solo la finestra
        if self._scala_attesa is not None:
            self.after_cancel(self._scala_attesa)
        self._scala_attesa = self.after(250, self._adatta_alla_finestra)

    def _e_davvero_ingrandita(self):
        """
        True se la finestra occupa davvero lo schermo. Non basta chiedere lo stato a Tk:
        dopo un cambio di scala dice ancora "zoomed" anche quando Windows l'ha già ridotta.
        """
        return self.state() == "zoomed" and self.winfo_width() >= self.winfo_screenwidth() - 80

    def _sincronizza_stato_finestra(self):
        """
        La finestra si ingrandisce e si riduce anche dai pulsanti della barra del titolo,
        che l'app non intercetta: senza questo controllo continuerebbe a credersi
        ingrandita, con il pulsante che dice il contrario di quello che fa.
        """
        if self._sblocco_attesa is not None:
            return #Cambio di scala in corso: le dimensioni non sono ancora attendibili
        reale = self._e_davvero_ingrandita()
        if reale == self._maximized:
            return
        self._maximized = reale
        self._update_window_button()
        strings.write_setting("maximized", reale)

    def _adatta_alla_finestra(self):
        """Scritte e comandi crescono con la finestra, restando in proporzione."""
        self._scala_attesa = None
        larghezza, altezza = self.winfo_width(), self.winfo_height()
        if larghezza <= 1 or altezza <= 1:
            return #Finestra non ancora disegnata
        self._sincronizza_stato_finestra()
        #Il lato più "stretto" decide: così niente esce dai bordi in una finestra bassa e larga
        voluta = min(larghezza / self._BASE_LARGHEZZA, altezza / self._BASE_ALTEZZA)
        voluta = max(self._SCALA_MIN, min(self._SCALA_MAX, voluta))
        #Ridisegnare tutto costa: si fa solo se il cambiamento si vede davvero. Le colonne
        #però vanno ricentrate comunque: la finestra è cambiata anche se la scala no.
        if abs(voluta - self._scala) < 0.05:
            self._centra_colonne()
            return
        self._scala = voluta
        customtkinter.set_widget_scaling(voluta)
        #CustomTkinter, quando cambia scala, blocca minimo e massimo della finestra per un
        #secondo (ctk_tk.py) e le impone una dimensione: premendo Ingrandisci/Riduci in
        #quell'attimo la finestra non ubbidirebbe e il pulsante direbbe il falso. Quindi il
        #pulsante resta spento finché il blocco non passa.
        self._blocca_pulsante_finestra()
        self._aggiorna_margini_righe()
        self._centra_colonne()

    #Larghezza massima di una riga di risultato. Su uno schermo largo, senza questo
    #limite, il titolo del gioco e il suo "Link" finiscono ai due lati opposti e
    #l'occhio deve attraversare mezzo schermo per collegarli.
    _MAX_LARGHEZZA_RIGA = 1000

    def _aggiorna_margini_righe(self):
        """
        Le righe già a schermo tengono i margini calcolati per la finestra di prima:
        ridimensionando, vanno ricalcolati, altrimenti restano strette e spostate.
        """
        elenco = getattr(self, "results_frame", None)
        if elenco is None or not elenco.winfo_exists():
            return
        self.update_idletasks() #Serve la larghezza nuova dell'elenco
        margine = self._margine_righe()
        for riga in elenco.winfo_children():
            if riga.winfo_manager() == "pack":
                #pack() e non pack_configure(): solo pack() applica la scala dei widget e
                #aggiorna quella che CustomTkinter riapplica al prossimo cambio di scala.
                #La riga resta al suo posto nell'elenco.
                riga.pack(fill="x", padx=margine, pady=6)

    def _margine_righe(self):
        """Spazio ai lati delle righe, per tenerle in una colonna centrata e leggibile."""
        elenco = getattr(self, "results_frame", None)
        larghezza = elenco.winfo_width() if elenco is not None and elenco.winfo_exists() else 0
        if larghezza <= 1:
            return 10 #Elenco non ancora disegnato: il margine di sempre
        #winfo_width() è in pixel veri, mentre padx passato a pack() viene poi moltiplicato
        #da CustomTkinter per la scala EFFETTIVA, che comprende anche l'ingrandimento di
        #Windows (125%, 150%...) oltre alla nostra. Qui si lavora quindi in "unità di
        #widget": pixel veri diviso quella scala.
        effettiva = customtkinter.ScalingTracker.get_widget_scaling(self)
        larghezza_widget = larghezza / max(effettiva, 0.1)
        return max(10, int((larghezza_widget - self._MAX_LARGHEZZA_RIGA) / 2))

    def _blocca_pulsante_finestra(self, millisecondi=1100):
        """Spegne per un attimo il pulsante Ingrandisci/Riduci, mentre la scala cambia."""
        pulsante = getattr(self, "window_button", None)
        if pulsante is None or not pulsante.winfo_exists():
            return
        pulsante.configure(state="disabled")
        if getattr(self, "_sblocco_attesa", None) is not None:
            self.after_cancel(self._sblocco_attesa)
        self._sblocco_attesa = self.after(millisecondi, self._sblocca_pulsante_finestra)

    def _sblocca_pulsante_finestra(self):
        self._sblocco_attesa = None
        pulsante = getattr(self, "window_button", None)
        if pulsante is not None and pulsante.winfo_exists():
            pulsante.configure(state="normal")
        #Durante il cambio di scala CustomTkinter impone una dimensione alla finestra e
        #può farla uscire dallo stato "ingrandita": se l'utente l'aveva chiesta grande,
        #si riprova adesso, una volta sola.
        if self._maximized and not self._e_davvero_ingrandita():
            self.state("zoomed")
        else:
            self._sincronizza_stato_finestra()

    def _toggle_maximized(self):
        """
        F11 o pulsante: ingrandisce la finestra a tutto lo schermo, o la rimpicciolisce.
        Mentre la scala sta cambiando la finestra non ubbidirebbe, quindi si aspetta.
        """
        if getattr(self, "_sblocco_attesa", None) is not None:
            return
        if self._maximized:
            self._restore_window()
        else:
            self._maximize()

    def _maximize(self):
        """Come il pulsante "Ingrandisci" di Windows: la barra del titolo resta al suo posto."""
        self.state("zoomed")
        self._maximized = True
        self._update_window_button()
        strings.write_setting("maximized", True)
        self._ricalcola_scala_subito()

    def _restore_window(self):
        self.state("normal")
        self._maximized = False
        self._update_window_button()
        strings.write_setting("maximized", False)
        self._ricalcola_scala_subito()

    def _ricalcola_scala_subito(self):
        """
        Dopo ingrandisci/riduci la nuova dimensione va applicata subito: aspettare il
        ritardo previsto per il trascinamento lascerebbe per un attimo comandi enormi
        in una finestra piccola, tutti sovrapposti.
        """
        if self._scala_attesa is not None:
            self.after_cancel(self._scala_attesa)
            self._scala_attesa = None
        self.update_idletasks() #Serve la dimensione nuova, non quella di un istante fa
        self._adatta_alla_finestra()
        #Windows a volte comunica la dimensione nuova un attimo dopo: si ricontrolla,
        #altrimenti resterebbe la scala della finestra di prima.
        self._scala_attesa = self.after(200, self._adatta_alla_finestra)

    def _update_window_button(self):
        """Il pulsante dice cosa succede premendolo, non lo stato attuale."""
        button = getattr(self, "window_button", None)
        if button is not None and button.winfo_exists():
            button.configure(text=t("restore_window") if self._maximized else t("maximize"))

    def _create_main_menu(self):
        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="#2b2b2b") #Creazione pannello sideba
        self.sidebar_frame.place(relx=0.0, rely=0.0, relwidth=0.2, relheight=1.0) #Posizione sidebar a sinistra
        self.sidebar_main_frame = customtkinter.CTkFrame(self, corner_radius=0) #Creazione pannello principale
        self.sidebar_main_frame.place(relx=0.2, rely=0, relwidth=0.8, relheight=1.0) #Posizione pannello principale a destra
        #Ingrandisci/riduci la finestra: il pulsante sta in alto a destra, sopra i risultati.
        #Vale anche F11, e restano i pulsanti della barra del titolo di Windows.
        self.window_button = customtkinter.CTkButton(self.sidebar_main_frame, text=t("maximize"), width=150, height=28,
                                                     font=("Arial", 11), fg_color="#3a3a3a", hover_color="#4a4a4a",
                                                     command=self._toggle_maximized)
        self.window_button.place(relx=0.985, rely=0.02, anchor="ne")
        self._update_window_button()
        self.sidebar_title = customtkinter.CTkLabel(self.sidebar_frame, text=t("history"), text_color="white", font=("Arial", 18, "bold")) #Titolo Cronologia
        self.sidebar_title.place(relx=0.5, rely=0.05, anchor="center") #Posizione Titolo Cronologia
        self.history_frame = customtkinter.CTkScrollableFrame(self.sidebar_frame, fg_color="#1e1e1e") #Area scrollabile cronologia
        self.history_frame.place(relx=0.5, rely=0.12, relwidth=0.95, relheight=0.68, anchor="n") #Posizione tra il titolo e il selettore di lingua

        #Pannello profilo a schermo intero (figlio di self, inizialmente nascosto)
        self.profile_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.profile_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.profile_title_label = customtkinter.CTkLabel(self.profile_frame, text=t("profile"), font=("Arial", 28, "bold")) #Titolo
        self.profile_title_label.place(relx=0.5, rely=0.18, anchor="center")
        self.profile_desc_label = customtkinter.CTkLabel(self.profile_frame, text=t("profile_desc"), font=("Arial", 12), text_color="gray", wraplength=400) #Descrizione
        self.profile_desc_label.place(relx=0.5, rely=0.26, anchor="center")
        self.profile_username_label = customtkinter.CTkLabel(self.profile_frame, text=t("username"), font=("Arial", 14)) #Etichetta username
        self.profile_username_label.place(relx=0.5, rely=0.34, anchor="center")
        self.profile_username_entry = customtkinter.CTkEntry(self.profile_frame, width=250, height=35) #Campo username
        self.profile_username_entry.place(relx=0.5, rely=0.40, anchor="center")
        self.profile_email_label = customtkinter.CTkLabel(self.profile_frame, text=t("email"), font=("Arial", 14)) #Etichetta email
        self.profile_email_label.place(relx=0.5, rely=0.47, anchor="center")
        self.profile_email_entry = customtkinter.CTkEntry(self.profile_frame, width=250, height=35) #Campo email
        self.profile_email_entry.place(relx=0.5, rely=0.53, anchor="center")
        self.profile_password_label = customtkinter.CTkLabel(self.profile_frame, text=t("new_password"), font=("Arial", 14)) #Etichetta nuova password
        self.profile_password_label.place(relx=0.5, rely=0.60, anchor="center")
        self.profile_password_entry = self._create_password_field(self.profile_frame, rely=0.66, placeholder_text=t("password_placeholder")) #Campo nuova password con lucchetto
        self.profile_message = customtkinter.CTkLabel(self.profile_frame, text="", font=("Arial", 12), wraplength=350) #Messaggio di stato
        self.profile_message.place(relx=0.5, rely=0.73, anchor="center")
        self.profile_save_button = customtkinter.CTkButton(self.profile_frame, text=t("save"), width=250, height=35, fg_color="#5B5EA6", hover_color="#4a4d8f", command=self._handle_update_profile) #Bottone Salva
        self.profile_save_button.place(relx=0.5, rely=0.80, anchor="center")
        self.profile_back_button = customtkinter.CTkButton(self.profile_frame, text=t("back_to_search"), width=250, height=35, command=self._close_profile_panel) #Bottone Indietro
        self.profile_back_button.place(relx=0.5, rely=0.88, anchor="center")
        self.profile_frame.place_forget() #Nascondiamo il pannello profilo all'avvio

        #Pannello di conferma password a schermo intero (secondo step, mostrato solo se sono state modificate delle informazioni)
        self.profile_confirm_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.profile_confirm_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.profile_confirm_title_label = customtkinter.CTkLabel(self.profile_confirm_frame, text=t("confirm_title"), font=("Arial", 28, "bold")) #Titolo
        self.profile_confirm_title_label.place(relx=0.5, rely=0.32, anchor="center")
        self.profile_confirm_desc_label = customtkinter.CTkLabel(self.profile_confirm_frame, text=t("confirm_desc"), font=("Arial", 12), text_color="gray", wraplength=400) #Descrizione
        self.profile_confirm_desc_label.place(relx=0.5, rely=0.42, anchor="center")
        self.profile_confirm_password_label = customtkinter.CTkLabel(self.profile_confirm_frame, text=t("current_password"), font=("Arial", 14)) #Etichetta password attuale
        self.profile_confirm_password_label.place(relx=0.5, rely=0.51, anchor="center")
        self.profile_confirm_password_entry = self._create_password_field(self.profile_confirm_frame, rely=0.57) #Campo password attuale con lucchetto
        self.profile_confirm_message = customtkinter.CTkLabel(self.profile_confirm_frame, text="", font=("Arial", 12), wraplength=350) #Messaggio di stato/errore
        self.profile_confirm_message.place(relx=0.5, rely=0.64, anchor="center")
        self.profile_confirm_save_button = customtkinter.CTkButton(self.profile_confirm_frame, text=t("save"), width=250, height=35, fg_color="#5B5EA6", hover_color="#4a4d8f", command=self._handle_confirm_profile_update) #Bottone Salva definitivo
        self.profile_confirm_save_button.place(relx=0.5, rely=0.72, anchor="center")
        self.profile_confirm_cancel_button = customtkinter.CTkButton(self.profile_confirm_frame, text=t("cancel"), width=250, height=35, command=self._cancel_profile_confirm) #Bottone Annulla, torna alla schermata Profilo senza salvare
        self.profile_confirm_cancel_button.place(relx=0.5, rely=0.80, anchor="center")
        self.profile_confirm_frame.place_forget() #Nascondiamo il pannello di conferma all'avvio

        self.sidebar_profile = customtkinter.CTkLabel(self.sidebar_frame, text=f"👤 {self.current_user['username']}", font=("Arial", 16, "bold"), cursor="hand2") #Sezione profilo con username (cliccabile)
        self.sidebar_profile.place(relx=0.5, rely=0.90, anchor="center") #Posizionamento della sezione profilo
        self.sidebar_profile.bind("<Button-1>", lambda event: self._open_profile_panel()) #Click apre il pannello profilo
        self.sidebar_language_selector = self._create_language_selector(self.sidebar_frame, width=150, font_size=11) #Cambio lingua
        self.sidebar_language_selector.place(relx=0.5, rely=0.845, anchor="center")
        self.sidebar_logout = customtkinter.CTkLabel(self.sidebar_frame, text=t("logout"), font=("Arial", 11), text_color="gray", cursor="hand2") #Pulsante logout
        self.sidebar_logout.place(relx=0.5, rely=0.96, anchor="center") #Posizionamento logout
        self.sidebar_logout.bind("<Button-1>", lambda event: self._handle_logout()) #Click esegue logout
        self.sidebar_entry =customtkinter.CTkEntry(self.sidebar_main_frame, width=400, height=30,placeholder_text=t("search_placeholder")) #Creazione Barra di ricerca
        self.sidebar_entry.place(relx=0.5, rely=0.05, anchor="center") #Posizione barra di ricerca
        self.sidebar_menu = customtkinter.CTkOptionMenu(self.sidebar_main_frame, values=list(STORES.keys())) #Creazione menu a tendica per gli store
        self.sidebar_menu.place(relx=0.3, rely=0.15, anchor="center") #Posizione del menu a tendina
        #Il primo valore ("Tutti") è l'unico da tradurre: gli altri sono i generi come li chiama Steam
        self.sidebar_genre_menu = customtkinter.CTkOptionMenu(self.sidebar_main_frame, values=[t("all")] + list(GENRES[1:])) #Creazione menu a tendina per i generi
        self.sidebar_genre_menu.place(relx=0.5, rely=0.15, anchor="center") #Posizionamento Menu per i generi di videogioco
        self.sidebar_discount_menu = customtkinter.CTkOptionMenu(self.sidebar_main_frame, values=[t("all")] + list(DISCOUNT[1:])) #Creazione del menu a tendina per gli sconti
        self.sidebar_discount_menu.place(relx=0.7, rely=0.15, anchor="center") #Posizionamente Menu a tendina per gli sconti
        self.sidebar_title_menu = customtkinter.CTkLabel(self.sidebar_main_frame, text=t("store"), text_color="white", font=("Arial", 14)) #Titolo Store
        self.sidebar_title_menu.place(relx=0.3, rely=0.10, anchor="center") #Posizione Titolo Store
        self.sidebar_title_genre_menu = customtkinter.CTkLabel(self.sidebar_main_frame, text=t("genre"), text_color="white", font=("Arial", 14)) #Titolo dell Genere
        self.sidebar_title_genre_menu.place(relx=0.5, rely=0.10, anchor="center") #Posizionamento Dell Genere
        self.sidebar_title_discount_menu = customtkinter.CTkLabel(self.sidebar_main_frame, text=t("discount"), text_color="white", font=("Arial", 14)) #Titolo Sconto
        self.sidebar_title_discount_menu.place(relx=0.7, rely=0.10, anchor="center") #Posizionamento dello Sconto
        self.search_button = customtkinter.CTkButton(self.sidebar_main_frame, text=t("search_button"), width=130, height=30, fg_color="#4a4d8f", command=self._handle_search) #Pulsante Cerca
        self.search_button.place(relx=0.15, rely=0.05, anchor="center") #Posizionamento dell Pulsante Cerca
        self.results_frame = customtkinter.CTkScrollableFrame(self.sidebar_main_frame) #Area scrollabile
        #Ancorato in alto (anchor "n") subito sotto i filtri: ingrandendo la finestra o
        #passando a schermo intero l'elenco cresce insieme a lei, invece di lasciare
        #una fascia vuota nel mezzo.
        self.results_frame.place(relx=0.5, rely=0.22, relwidth=0.95, relheight=0.72, anchor="n") #Posizionamento
        self.status_label = customtkinter.CTkLabel(self.sidebar_main_frame, text="", text_color="gray", font=("Arial", 12))
        self.status_label.place(relx=0.5, rely=0.32, anchor="center")
        self.credits_label = customtkinter.CTkLabel(self.sidebar_main_frame, text=t("credits"), font=("Arial", 10), text_color="Dark Slate Blue") #Footer crediti
        self.credits_label.place(relx=0.5, rely=0.98, anchor="center")
        self._load_history() #Carichiamo la cronologia al primo avvio

    def _handle_search(self):
        #Durante la ricerca la finestra continua a gestire i clic (self.update() più
        #sotto, per non sembrare bloccata): senza questo controllo un secondo clic su
        #"Cerca" avvierebbe un'altra ricerca sopra quella in corso, mescolando i risultati.
        if self._searching:
            return
        self._searching = True
        self.search_button.configure(state="disabled")
        try:
            self._run_search()
        finally:
            self._searching = False
            if self.search_button.winfo_exists():
                self.search_button.configure(state="normal")

    def _run_search(self):
        store_name = self.sidebar_menu.get() #Prendiamo Lo store selezionato dall utente
        store_id = STORES[store_name] #Convertiamo il nome in ID
        genre_value = self.sidebar_genre_menu.get() #Prendiamo il genere selezionato

        #Mostriamo il messaggio di ricerca in corso
        self.status_label.configure(text_color="gray", text=t("searching"))
        self.update() #Forziamo l'aggiornamento della finestra per mostrare subito il messaggio

        try:
            deals = get_deals(store_id) #Chiamiamo l'API

            #Prendiamo il valore dello sconto selezionato
            discount_value = self.sidebar_discount_menu.get()
            if discount_value != t("all"):
                min_discount = int(discount_value.replace("%", "").replace("+", "")) #Convertiamo "50%+" in 50
            else:
                min_discount = 0 #Nessun filtro sullo sconto

            #Puliamo i risultati precedenti
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            results_count = 0 #Contatore dei risultati mostrati
            margine = self._margine_righe() #Righe centrate: su schermi larghi non si allungano all'infinito
            search_text = self.sidebar_entry.get().strip().lower() #Testo cercato dall'utente

            #Creiamo una label per ogni gioco che rispetta i filtri
            for deal in deals:
                if deal['savings'] < min_discount:
                    continue #Saltiamo questo gioco, sconto troppo basso

                #Filtro testo (solo se l'utente ha scritto qualcosa): lo controlliamo PRIMA del
                #genere apposta, perché è un controllo locale istantaneo, mentre il genere
                #richiede una chiamata di rete a Steam — così evitiamo di sprecarla per giochi
                #che il filtro testo avrebbe comunque scartato.
                if search_text and search_text not in deal['title'].lower():
                    continue

                #Filtro Genere (solo se non è "Tutti")
                if genre_value != t("all"):
                    game_genres = get_game_genres(deal['steamAppID']) #Chiediamo a Steam il genere (con cache)
                    self.update() #Manteniamo la finestra reattiva: senza, con molti giochi da controllare sembrerebbe bloccata
                    if genre_value not in game_genres:
                        continue

                #Creiamo una riga (contenitore) per ogni gioco
                row_frame = customtkinter.CTkFrame(self.results_frame, fg_color="#2b2b2b", corner_radius=8)
                row_frame.pack(fill="x", padx=margine, pady=6)

                #CheapShark restituisce i prezzi in dollari statunitensi: il simbolo deve essere "$"
                text = f"{deal['title']} — ${deal['salePrice']} (-{int(deal['savings'])}%)"
                label = customtkinter.CTkLabel(row_frame, text=text, anchor="w")
                label.pack(side="left", fill="x", expand=True, padx=12, pady=10)

                link_label = customtkinter.CTkLabel(row_frame, text=t("link"), text_color="#5B5EA6", cursor="hand2") #cursor="hand2" mostra la manina
                link_label.pack(side="right", padx=12, pady=10)
                link_label.bind("<Button-1>", lambda event, d=deal: self._open_game(d)) #Click apre il link

                results_count += 1 #Aumentiamo il contatore

            #Se nessun gioco rispetta i filtri, mostriamo un messaggio
            if results_count == 0:
                no_results_label = customtkinter.CTkLabel(self.results_frame, text=t("no_results"), text_color="gray")
                no_results_label.pack(pady=20)

            #Puliamo il messaggio di stato
            self.status_label.configure(text="")
        except ConnectionError:
            #get_deals solleva ConnectionError in caso di problemi di rete: senza questo except,
            #in una build .exe --windowed (senza console) l'utente resterebbe bloccato sul messaggio
            #"Ricerca in corso..." per sempre, senza nessun modo di capire cosa sia successo.
            self.status_label.configure(text_color="red", text=t("search_connection_error"))
        except Exception:
            #Rete di sicurezza per qualsiasi altro errore imprevisto durante la ricerca:
            #meglio un messaggio generico che un blocco silenzioso dell'interfaccia.
            self.status_label.configure(text_color="red", text=t("search_unexpected_error"))

    def _open_game(self, deal):
        url = f"https://www.cheapshark.com/redirect?dealID={deal['dealID']}" #Link al gioco
        webbrowser.open(url) #Apriamo il link nel browser predefinito
        try:
            api_client.add_history(self.access_token, deal['title'], deal['dealID']) #Salviamo il click nella cronologia
        except api_client.APIError as e:
            if self._is_session_lost(e):
                self._session_lost()
                return
            #Altri errori: il link si è comunque aperto, non blocchiamo l'utente
        except api_client.ConnectionErrorAPI:
            pass #Il link si è comunque aperto: non blocchiamo l'utente se solo il salvataggio in cronologia fallisce
        self._load_history() #Aggiorniamo la lista cronologia

    @staticmethod
    def _is_session_lost(error):
        """
        True se il server ha rifiutato il token: sessione scaduta, revocata o
        inesistente. Si guarda il codice "session_lost" e non il testo del
        messaggio, che cambia con la lingua.
        """
        return error.error_code == "session_lost"

    def _session_lost(self):
        """
        La sessione non vale più (password cambiata o reimpostata, "Esci" da un altro
        computer, scadenza): si torna al login spiegando il perché, invece di restare
        in un'app che sembra collegata ma non salva più niente.
        """
        self._handle_logout(call_server=False)
        self.login_error.configure(text_color="orange", text=t("session_lost"))

    def _load_history(self):
        #Puliamo i widget precedenti nella cronologia
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        try:
            result = api_client.get_history(self.access_token) #Carichiamo le ultime offerte visitate dall'utente
        except api_client.APIError as e:
            if self._is_session_lost(e):
                #Rimandato di un attimo: _load_history viene chiamata anche mentre il menu
                #principale è ancora in costruzione
                self.after(10, self._session_lost)
            return #Se la cronologia non si carica, la lasciamo semplicemente vuota
        except api_client.ConnectionErrorAPI:
            return #Se la cronologia non si carica, la lasciamo semplicemente vuota

        for entry in result["history"]:
            title = entry["title"]
            deal_id = entry["deal_id"]

            row_frame = customtkinter.CTkFrame(self.history_frame, fg_color="transparent") #Riga contenitore
            row_frame.pack(fill="x", padx=5, pady=3)

            title_label = customtkinter.CTkLabel(row_frame, text=title, anchor="w", wraplength=110) #Titolo gioco
            title_label.pack(side="left", fill="x", expand=True)

            link_label = customtkinter.CTkLabel(row_frame, text=t("link"), text_color="#5B5EA6", cursor="hand2") #Link cliccabile
            link_label.pack(side="right", padx=5)
            link_label.bind("<Button-1>", lambda event, d=deal_id: webbrowser.open(f"https://www.cheapshark.com/redirect?dealID={d}")) #Click apre il link

    def _handle_logout(self, call_server=True):
        if self._searching:
            #Uscire a metà ricerca distruggerebbe i pannelli mentre la ricerca li sta
            #ancora riempiendo: si esce quando la ricerca è finita
            self.status_label.configure(text_color="orange", text=t("wait_for_search"))
            return
        if call_server:
            try:
                api_client.logout(self.access_token) #Revochiamo la sessione lato server
            except (api_client.APIError, api_client.ConnectionErrorAPI):
                pass #Anche se la revoca lato server fallisce, disconnettiamo comunque in locale
        self.access_token = None
        delete_saved_token() #Eliminiamo la sessione salvata se esiste
        self.sidebar_frame.destroy() #Distruggiamo la sidebar
        self.sidebar_main_frame.destroy() #Distruggiamo il pannello principale
        self.profile_frame.destroy() #Distruggiamo il pannello profilo
        self.profile_confirm_frame.destroy() #Distruggiamo il pannello di conferma password

        if hasattr(self, "login_frame"): #Se i pannelli login/registrazione esistono già li rmostriamo
            self.login_frame.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0)
            self.register_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1.0)
            if hasattr(self, "verify_email_frame"): #Ci assicuriamo che il pannello di verifica email sia nascosto
                self.verify_email_frame.place_forget()
            if hasattr(self, "forgot_password_frame"): #Ci assicuriamo che il pannello password dimenticata sia nascosto
                self.forgot_password_frame.place_forget()
            if hasattr(self, "login_error"): #I widget interni esistono (login manuale precedente)
                self.login_error.configure(text="") #Puliamo l'eventuale messaggio di errore
                self.login_username_entry.delete(0, "end") #Svuotiamo il campo username
                self.login_password_entry.delete(0, "end") #Svuotiamo il campo password
            else: #I frame esistono ma i widget interni no (login da sessione salvata)
                self._create_login()
                self._create_register()
        else: #Altrimenti li creiamo da zero
            self._create_panels()
            self._create_login()
            self._create_register()

    def _open_profile_panel(self):
        self.sidebar_frame.place_forget() #Nascondiamo la sidebar
        self.sidebar_main_frame.place_forget() #Nascondiamo il pannello principale
        self.profile_confirm_frame.place_forget() #Ci assicuriamo che la schermata di conferma sia nascosta
        self.profile_username_entry.delete(0, "end") #Svuotiamo il campo username
        self.profile_username_entry.insert(0, self.current_user["username"]) #Precompiliamo con username attuale
        self.profile_email_entry.delete(0, "end") #Svuotiamo il campo email
        self.profile_email_entry.insert(0, self.current_user["email"]) #Precompiliamo con email attuale
        self.profile_password_entry.delete(0, "end") #Svuotiamo il campo password
        self.profile_message.configure(text="") #Azzeriamo il messaggio di stato
        self.profile_frame.place(relx=0, rely=0, relwidth=1, relheight=1) #Mostriamo il pannello profilo a schermo intero

    def _close_profile_panel(self):
        self.profile_frame.place_forget() #Nascondiamo il pannello profilo
        self.sidebar_frame.place(relx=0.0, rely=0.0, relwidth=0.2, relheight=1.0) #Rmostriamo la sidebar
        self.sidebar_main_frame.place(relx=0.2, rely=0, relwidth=0.8, relheight=1.0) #Rmostriamo il pannello principale

    def _handle_update_profile(self):
        username = self.profile_username_entry.get() #Prendiamo il nuovo username
        email = self.profile_email_entry.get() #Prendiamo la nuova email
        password = self.profile_password_entry.get() or None #Prendiamo la nuova password (None se vuota)

        #Controlliamo se è stato effettivamente modificato qualcosa rispetto ai dati attuali
        changed = (username != self.current_user["username"]) or (email != self.current_user["email"]) or (password is not None)
        if not changed:
            self.profile_message.configure(text_color="gray", text=t("no_changes"))
            return

        #Stessa regola della registrazione: anche qui l'email deve restare un indirizzo Gmail
        if not GMAIL_ADDRESS.fullmatch(email.strip()):
            self.profile_message.configure(text_color="red", text=t("gmail_required"))
            return

        #Salviamo temporaneamente i nuovi valori: verranno applicati solo dopo la conferma della password attuale
        self._pending_username = username
        self._pending_email = email
        self._pending_password = password

        #Passiamo alla schermata di conferma password
        self.profile_confirm_password_entry.delete(0, "end") #Svuotiamo il campo password di conferma
        self.profile_confirm_message.configure(text="") #Azzeriamo l'eventuale messaggio precedente
        self.profile_frame.place_forget() #Nascondiamo la schermata profilo
        self.profile_confirm_frame.place(relx=0, rely=0, relwidth=1, relheight=1) #Mostriamo la schermata di conferma

    def _handle_confirm_profile_update(self):
        current_password = self.profile_confirm_password_entry.get() #Prendiamo la password attuale inserita

        #Controllo campo vuoto
        if not current_password:
            self.profile_confirm_message.configure(text_color="red", text=t("enter_current_password"))
            return

        #Una sola chiamata all'API: verifica della password attuale e aggiornamento dei dati
        #avvengono insieme lato server (compresa la notifica di sicurezza via email, che il
        #server invia da solo — l'app non deve più occuparsene).
        try:
            result = api_client.update_profile(
                self.access_token, self._pending_username, self._pending_email,
                current_password, self._pending_password,
            ) or {}
        except api_client.APIError as e:
            if self._is_session_lost(e):
                #Sessione chiusa da un'altra parte: non è la password attuale a essere sbagliata
                self._session_lost()
                return
            if e.status_code == 401:
                self.profile_confirm_message.configure(text_color="red", text=t("wrong_current_password")) #Messaggio di errore
            elif e.status_code == 409:
                self.profile_confirm_message.configure(text_color="red", text=t("username_taken")) #Messaggio di errore
            else:
                self.profile_confirm_message.configure(text_color="red", text=str(e))
            self.profile_confirm_password_entry.delete(0, "end") #Svuotiamo il campo per sicurezza
            return
        except api_client.ConnectionErrorAPI:
            self.profile_confirm_message.configure(text_color="red", text=t("connection_error"))
            return

        #Aggiornamento riuscito: ricarichiamo i dati utente aggiornati dal server
        try:
            self.current_user = api_client.get_me(self.access_token)
        except (api_client.APIError, api_client.ConnectionErrorAPI):
            #Non dovrebbe succedere appena dopo un aggiornamento riuscito, ma per sicurezza
            #teniamo almeno i valori che avevamo appena inviato
            self.current_user = {"id": self.current_user["id"], "username": self._pending_username, "email": self._pending_email}

        self.sidebar_profile.configure(text=f"👤 {self.current_user['username']}", font=("Arial", 16, "bold")) #Aggiorniamo il nome nella sidebar
        #Nota: session.json contiene il token, non lo username, quindi non va riscritto qui
        #anche se lo username è cambiato — il token della sessione corrente resta valido
        #(il server revoca solo le ALTRE sessioni, quando cambia la password).

        #Torniamo alla schermata profilo mostrando l'esito positivo
        self.profile_confirm_password_entry.delete(0, "end") #Svuotiamo il campo password di conferma
        self.profile_confirm_frame.place_forget() #Nascondiamo la schermata di conferma
        #L'email non cambia con la sola password: il server ha mandato due codici (uno
        #all'indirizzo attuale, uno al nuovo) e aspetta la conferma (api/email_change.py)
        if result.get("email_pending"):
            self._show_email_change_panel(result)
            return
        self.profile_frame.place(relx=0, rely=0, relwidth=1, relheight=1) #Rmostriamo la schermata profilo
        self.profile_message.configure(text_color="green", text=t("profile_updated")) #Messaggio di successo

    def _show_email_change_panel(self, result):
        """Schermata per i due codici del cambio email. Creata al bisogno e distrutta dopo."""
        panel = customtkinter.CTkFrame(self, corner_radius=0)
        self.email_change_frame = panel
        customtkinter.CTkLabel(panel, text=t("email_change_title"), font=("Arial", 28, "bold")).place(relx=0.5, rely=0.16, anchor="center")
        customtkinter.CTkLabel(panel, text=t("email_change_desc", old=result.get("old_email_hint", ""), new=result.get("new_email_hint", "")),
                               font=("Arial", 12), text_color="gray", wraplength=480).place(relx=0.5, rely=0.26, anchor="center")
        customtkinter.CTkLabel(panel, text=t("email_change_old_code"), font=("Arial", 14)).place(relx=0.5, rely=0.36, anchor="center")
        self.email_change_old_entry = customtkinter.CTkEntry(panel, width=250, height=35, justify="center")
        self.email_change_old_entry.place(relx=0.5, rely=0.42, anchor="center")
        customtkinter.CTkLabel(panel, text=t("email_change_new_code"), font=("Arial", 14)).place(relx=0.5, rely=0.49, anchor="center")
        self.email_change_new_entry = customtkinter.CTkEntry(panel, width=250, height=35, justify="center")
        self.email_change_new_entry.place(relx=0.5, rely=0.55, anchor="center")
        self.email_change_message = customtkinter.CTkLabel(panel, text="", font=("Arial", 12), wraplength=420)
        self.email_change_message.place(relx=0.5, rely=0.62, anchor="center")
        if result.get("email_sent") is False:
            self.email_change_message.configure(text_color="orange", text=t("email_change_not_sent"))
        customtkinter.CTkButton(panel, text=t("email_change_confirm"), width=250, height=35, fg_color="#5B5EA6", hover_color="#4a4d8f",
                                command=self._handle_email_change_confirm).place(relx=0.5, rely=0.70, anchor="center")
        customtkinter.CTkButton(panel, text=t("cancel"), width=250, height=35,
                                command=self._close_email_change_panel).place(relx=0.5, rely=0.78, anchor="center")
        customtkinter.CTkLabel(panel, text=t("email_change_lost_old"), font=("Arial", 11), text_color="gray",
                               wraplength=460).place(relx=0.5, rely=0.87, anchor="center")
        panel.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.email_change_old_entry.focus_set()

    def _close_email_change_panel(self, message=None, color="green"):
        """Torna al Profilo. Annullando, il cambio resta in sospeso e scade da solo."""
        if getattr(self, "email_change_frame", None) is not None:
            self.email_change_frame.destroy()
            self.email_change_frame = None
        self._open_profile_panel()
        if message:
            self.profile_message.configure(text_color=color, text=message)

    def _handle_email_change_confirm(self):
        old_code = self.email_change_old_entry.get().strip()
        new_code = self.email_change_new_entry.get().strip()
        if not (old_code.isdigit() and len(old_code) == 6 and new_code.isdigit() and len(new_code) == 6):
            self.email_change_message.configure(text_color="red", text=t("email_change_codes_needed"))
            return
        try:
            api_client.confirm_email_change(self.access_token, old_code, new_code)
        except api_client.APIError as e:
            if self._is_session_lost(e):
                self._session_lost()
                return
            if e.status_code == 410: #Scaduto o annullato: si riparte dal Profilo
                self._close_email_change_panel(str(e), "red")
                return
            self.email_change_message.configure(text_color="red", text=str(e))
            return
        except api_client.ConnectionErrorAPI:
            self.email_change_message.configure(text_color="red", text=t("connection_error"))
            return
        try:
            self.current_user = api_client.get_me(self.access_token)
        except (api_client.APIError, api_client.ConnectionErrorAPI):
            self.current_user = {**self.current_user, "email": self._pending_email}
        self._close_email_change_panel(t("email_change_done"))

    def _cancel_profile_confirm(self):
        self.profile_confirm_password_entry.delete(0, "end") #Svuotiamo il campo password di conferma
        self.profile_confirm_message.configure(text="") #Azzeriamo l'eventuale messaggio di errore
        self.profile_confirm_frame.place_forget() #Nascondiamo la schermata di conferma
        self.profile_frame.place(relx=0, rely=0, relwidth=1, relheight=1) #Torniamo alla schermata profilo senza salvare

app = App() #Crea finestra
app.mainloop() #la tiene in ascolto cioé aperta