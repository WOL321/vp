"""
Advanced i18n system with auto-detection and context-aware translations
"""

import re
from typing import Optional

class I18n:
    """Advanced internationalization with auto-detection"""
    
    def __init__(self):
        self.translations = {
            "en": self._english(),
            "es": self._spanish()
        }
        self.user_langs = {}
        self.auto_detect_patterns = {
            "es": [
                r'\b(hola|buenos|buenas|gracias|por favor|cómo|qué|cuándo|dónde)\b',
                r'[áéíóúñ]',
            ]
        }
    
    def _english(self) -> dict:
        """English translations"""
        return {
            # Welcome
            "welcome_title": "🇨🇴 Welcome to Colombia, {user}!",
            "welcome_desc": "Comrade, you have reached our shores. Whether you come to build a home, stand alongside our people, or speak on behalf of another nation, there is a place for you here.\n\nA nation is built by its people—and every great undertaking begins with someone willing to lay the first block.\n\nRead our rules, meet the community, and request citizenship if you wish to call Colombia home. Diplomats, our Foreign Affairs office awaits you.\n\n¡Bienvenido a Colombia! 🌴\n— Nariño",
            "welcome_footer": "Citizenship: /role-request · Support: /ticket · Diplomacy: /diplomacy",
            
            # Vote Party
            "vote_party_title": "🇨🇴 Colombia Vote Party",
            "vote_party_desc": "The community is working together to reach {goal} votes!",
            "vote_party_complete": "🎉 🇨🇴 VOTE PARTY COMPLETE! 🇨🇴 🎉",
            "vote_party_complete_desc": "The community reached **{goal} votes**! Time for the party!",
            "votes_remaining": "**{remaining}** votes remaining",
            "votes_collected": "{progress} / {VOTE_GOAL} votes collected",
            
            # Status messages
            "status_complete": "🎉 **Vote Party Complete!**",
            "status_imminent": "🔥 **Almost there! Party imminent!**",
            "status_close": "⚡ **Getting close! Notify the server!**",
            "status_progress": "💪 **Good progress! Keep it up!**",
            "status_started": "🗳️ **Vote party in progress**",
            
            # Buttons
            "btn_i_voted": "✅ I Voted!",
            "btn_notify": "🔔 Get Notified",
            "btn_stop_notify": "🔕 Stop Notifications",
            "btn_how_to_vote": "📖 How to Vote",
            "btn_remind_me": "⏰ Remind Me Later",
            "btn_leaderboard": "🏆 Leaderboard",
            
            # Role requests
            "role_request_title": "🇨🇴 Colombia Role Requests",
            "role_request_desc": "Choose a role below. Citizenship and Ally requests go to leadership review. Vote Party Pings can be toggled instantly.\n\n**Request format:**\nMinecraft username · Nation · Town · Nation role",
            "btn_citizen": "🏠 Request Citizenship",
            "btn_ally": "🤝 Request Ally Status",
            "btn_diplomat": "🌐 Foreign Diplomat",
            
            # Tickets
            "ticket_title": "🎫 Support Ticket",
            "ticket_created": "✅ Ticket created! A staff member will be with you shortly.",
            "ticket_closed": "✅ Ticket closed by {user}",
            "ticket_already_open": "❌ You already have an open ticket!",
            
            # Economy
            "balance_title": "💰 Your Balance",
            "balance_desc": "You have **{balance}** {currency}",
            "daily_reward": "✅ You claimed your daily reward of **{amount}** {currency}!",
            "daily_already": "❌ You've already claimed your daily reward! Come back in **{time}**.",
            "work_success": "💼 You worked hard and earned **{amount}** {currency}!",
            "work_cooldown": "⏰ You need to rest! Try again in **{time}**.",
            
            # Moderation
            "warn_success": "✅ {user} has been warned. They now have **{count}/{max}** warnings.",
            "warn_max": "🚨 {user} has reached the maximum warnings and has been banned!",
            "mute_success": "✅ {user} has been muted for **{duration}**.",
            "ban_success": "✅ {user} has been banned.",
            
            # Activity
            "level_up": "🎉 {user} has reached **Level {level}**!",
            "leaderboard_title": "🏆 Leaderboard",
            
            # Events
            "giveaway_title": "🎁 Giveaway",
            "giveaway_ended": "🎁 Giveaway ended!",
            "giveaway_winner": "🎉 Congratulations {winner}! You won **{prize}**!",
            
            # Diplomacy
            "diplomacy_title": "🌐 Foreign Affairs",
            "alliance_formed": "🤝 Alliance formed between {nation1} and {nation2}!",
            "war_declared": "⚔️ {nation1} has declared war on {nation2}!",
            
            # Towns
            "town_created": "✅ Town **{town}** has been created!",
            "town_joined": "✅ {user} has joined **{town}**!",
            
            # Fun
            "fun_fact_title": "🇨🇴 Did You Know?",
            "trivia_title": "🧠 Colombia Trivia",
            "trivia_correct": "✅ Correct! The answer is **{answer}**!",
            "trivia_wrong": "❌ Wrong! The correct answer is **{answer}**.",
            
            # Errors
            "error_generic": "❌ An error occurred: {error}",
            "error_no_permission": "❌ You don't have permission to use this command!",
            "error_invalid_input": "❌ Invalid input. Please try again.",
            "error_cooldown": "⏰ Please wait **{time}** before using this again.",
            
            # General
            "success": "✅ Success!",
            "cancelled": "❌ Cancelled.",
            "timeout": "⏰ Timed out. Please try again.",
        }
    
    def _spanish(self) -> dict:
        """Spanish translations"""
        return {
            # Welcome
            "welcome_title": "🇨🇴 ¡Bienvenido a Colombia, {user}!",
            "welcome_desc": "Camarada, has llegado a nuestras costas. Ya vengas a construir un hogar, estar junto a nuestra gente, o hablar en nombre de otra nación, hay un lugar para ti aquí.\n\nUna nación se construye por su gente—y cada gran empresa comienza con alguien dispuesto a poner el primer bloque.\n\nLee nuestras reglas, conoce a la comunidad, y solicita ciudadanía si deseas llamar a Colombia tu hogar. Diplomáticos, nuestra oficina de Asuntos Exteriores te espera.\n\n¡Bienvenido a Colombia! 🌴\n— Nariño",
            "welcome_footer": "Ciudadanía: /role-request · Soporte: /ticket · Diplomacia: /diplomacy",
            
            # Vote Party
            "vote_party_title": "🇨🇴 Fiesta de Votos de Colombia",
            "vote_party_desc": "¡La comunidad está trabajando junta para alcanzar {goal} votos!",
            "vote_party_complete": "🎉 🇨🇴 ¡FIESTA DE VOTOS COMPLETA! 🇨🇴 🎉",
            "vote_party_complete_desc": "¡La comunidad alcanzó **{goal} votos**! ¡Hora de la fiesta!",
            "votes_remaining": "**{remaining}** votos restantes",
            "votes_collected": "{progress} / {VOTE_GOAL} votos recogidos",
            
            # Status messages
            "status_complete": "🎉 **¡Fiesta de Votos Completa!**",
            "status_imminent": "🔥 **¡Ya casi! ¡Fiesta inminente!**",
            "status_close": "⚡ **¡Cerca! ¡Avisa al servidor!**",
            "status_progress": "💪 **¡Buen progreso! ¡Sigue así!**",
            "status_started": "🗳️ **Fiesta de votos en progreso**",
            
            # Buttons
            "btn_i_voted": "✅ ¡Voté!",
            "btn_notify": "🔔 Notificarme",
            "btn_stop_notify": "🔕 Parar Notificaciones",
            "btn_how_to_vote": "📖 Cómo Votar",
            "btn_remind_me": "⏰ Recordar Después",
            "btn_leaderboard": "🏆 Clasificación",
            
            # Role requests
            "role_request_title": "🇨🇴 Solicitudes de Roles de Colombia",
            "role_request_desc": "Elige un rol abajo. Las solicitudes de Ciudadanía y Aliado van a revisión de liderazgo. Los Pings de Fiesta de Votos se pueden alternar instantáneamente.\n\n**Formato de solicitud:**\nUsuario de Minecraft · Nación · Pueblo · Rol de nación",
            "btn_citizen": "🏠 Solicitar Ciudadanía",
            "btn_ally": "🤝 Solicitar Estado de Aliado",
            "btn_diplomat": "🌐 Diplomático Extranjero",
            
            # Tickets
            "ticket_title": "🎫 Ticket de Soporte",
            "ticket_created": "✅ ¡Ticket creado! Un miembro del staff estará contigo pronto.",
            "ticket_closed": "✅ Ticket cerrado por {user}",
            "ticket_already_open": "❌ ¡Ya tienes un ticket abierto!",
            
            # Economy
            "balance_title": "💰 Tu Balance",
            "balance_desc": "Tienes **{balance}** {currency}",
            "daily_reward": "✅ ¡Reclamaste tu recompensa diaria de **{amount}** {currency}!",
            "daily_already": "❌ ¡Ya reclamaste tu recompensa diaria! Vuelve en **{time}**.",
            "work_success": "💼 ¡Trabajaste duro y ganaste **{amount}** {currency}!",
            "work_cooldown": "⏰ ¡Necesitas descansar! Intenta de nuevo en **{time}**.",
            
            # Moderation
            "warn_success": "✅ {user} ha sido advertido. Ahora tiene **{count}/{max}** advertencias.",
            "warn_max": "🚨 ¡{user} ha alcanzado el máximo de advertencias y ha sido baneado!",
            "mute_success": "✅ {user} ha sido silenciado por **{duration}**.",
            "ban_success": "✅ {user} ha sido baneado.",
            
            # Activity
            "level_up": "🎉 ¡{user} ha alcanzado el **Nivel {level}**!",
            "leaderboard_title": "🏆 Clasificación",
            
            # Events
            "giveaway_title": "🎁 Sorteo",
            "giveaway_ended": "🎁 ¡Sorteo terminado!",
            "giveaway_winner": "🎉 ¡Felicidades {winner}! ¡Ganaste **{prize}**!",
            
            # Diplomacy
            "diplomacy_title": "🌐 Asuntos Exteriores",
            "alliance_formed": "🤝 ¡Alianza formada entre {nation1} y {nation2}!",
            "war_declared": "⚔️ ¡{nation1} ha declarado guerra a {nation2}!",
            
            # Towns
            "town_created": "✅ ¡El pueblo **{town}** ha sido creado!",
            "town_joined": "✅ ¡{user} se ha unido a **{town}**!",
            
            # Fun
            "fun_fact_title": "🇨🇴 ¿Sabías Que?",
            "trivia_title": "🧠 Trivia de Colombia",
            "trivia_correct": "✅ ¡Correcto! La respuesta es **{answer}**!",
            "trivia_wrong": "❌ ¡Incorrecto! La respuesta correcta es **{answer}**.",
            
            # Errors
            "error_generic": "❌ Ocurrió un error: {error}",
            "error_no_permission": "❌ ¡No tienes permiso para usar este comando!",
            "error_invalid_input": "❌ Entrada inválida. Por favor intenta de nuevo.",
            "error_cooldown": "⏰ Por favor espera **{time}** antes de usar esto de nuevo.",
            
            # General
            "success": "✅ ¡Éxito!",
            "cancelled": "❌ Cancelado.",
            "timeout": "⏰ Tiempo agotado. Por favor intenta de nuevo.",
        }
    
    def get(self, key: str, lang: str = "en", **kwargs) -> str:
        """Get translation with optional formatting"""
        if lang not in self.translations:
            lang = "en"
        
        text = self.translations[lang].get(key, self.translations["en"].get(key, key))
        
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError):
                return text
        
        return text
    
    def detect_language(self, text: str) -> str:
        """Auto-detect language from text"""
        text_lower = text.lower()
        
        for lang, patterns in self.auto_detect_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return lang
        
        return "en"
    
    def set_user_lang(self, user_id: int, lang: str):
        """Set user's preferred language"""
        self.user_langs[user_id] = lang
    
    def get_user_lang(self, user_id: int) -> str:
        """Get user's preferred language"""
        return self.user_langs.get(user_id, "en")

# Global instance
i18n = I18n()
