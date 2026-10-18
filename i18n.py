"""
Internationalization (i18n) module for Spanish + English support.
"""

from typing import Optional

# ─── Translation Strings ──────────────────────────────────────────────────────

STRINGS = {
    "en": {
        # Embed
        "embed_title": "🇨🇴 Colombia Vote Party",
        "votes_remaining": "**{remaining}** votes remaining",
        "votes_collected": "{progress} / {VOTE_GOAL} votes collected",
        "vote_counts": "🗳️ **Vote Counts**",
        "vote_now": "🔗 **Vote Now!**",
        "vote_on": "Vote on {name}",
        "unavailable": "⚠️ Unavailable",
        "updates_every": "Updates every {seconds}s",
        "last_vp": "Last VP: {time}",
        "waiting_first": "Waiting for first update...",

        # Status messages
        "status_complete": "🎉 **Vote Party Complete!**",
        "status_imminent": "🔥 **Almost there! Party imminent!**",
        "status_close": "⚡ **Getting close! Notify the server!**",
        "status_progress": "💪 **Good progress! Keep it up!**",
        "status_started": "🗳️ **Vote party in progress**",

        # Celebration
        "celebration_title": "🎉 🇨🇴 VOTE PARTY COMPLETE! 🇨🇴 🎉",
        "celebration_desc": "The community reached **{goal} votes**! Time for the party!",
        "celebration_stats": "⏱️ Completed in **{time}**\n📊 Voting speed: **{speed} votes/hour**",
        "celebration_new_cycle": "New cycle starting...",
        "celebration_contributions": "🏆 **Top Contributors This Cycle**",

        # Buttons
        "btn_i_voted": "✅ I Voted!",
        "btn_notify": "🔔 Get Notified",
        "btn_stop_notify": "🔕 Stop Notifications",
        "btn_how_to_vote": "📖 How to Vote",
        "btn_remind_me": "⏰ Remind Me Later",
        "btn_leaderboard": "🏆 Leaderboard",

        # Vote claim
        "vote_claimed": "✅ Vote claimed! You now have **{total}/3** votes this cycle.",
        "vote_claimed_streak": "✅ Vote claimed! 🔥 **{streak} day streak!**",
        "vote_cooldown": "⚠️ You've already claimed all **3** votes for this cycle!\n*Wait for the next vote party to claim more.*",
        "vote_first_link": "🔗 Please link your Minecraft username first using `/link`.",

        # Notifications
        "notify_on": "✅ You will now be **notified** when the vote party is close!",
        "notify_off": "✅ You will **no longer** be notified for vote party updates.",
        "role_not_found": "❌ The 'VP' role was not found. Please ask an admin to create it.",
        "permission_error": "❌ I don't have permission to manage roles. Please ensure my role is **above** the VP role.",

        # Reminder
        "reminder_set": "⏰ I'll remind you in **30 minutes** to vote!",
        "reminder_message": "🔔 **Reminder!** The Colombia Vote Party is still going!\n{remaining} votes remaining. Come vote now!",
        "reminder_cooldown": "⏳ You already have a reminder set. Try again in **{time}**.",

        # How to vote
        "how_to_title": "📖 How to Vote for Colombia",
        "how_to_desc": "Follow these steps to help us reach the vote party goal!",
        "how_to_step1": "**1.** Click the vote links in the tracker embed above.",
        "how_to_step2": "**2.** Complete the captcha on the voting site.",
        "how_to_step3": "**3.** After voting, click the **✅ I Voted!** button below to claim your vote.",
        "how_to_step4": "**4.** You can vote once per hour on each site.",
        "how_to_tip": "💡 **Tip:** Vote on all 3 sites for maximum impact!",

        # Leaderboard
        "lb_title": "🏆 Vote Leaderboard",
        "lb_cycle": "This Cycle",
        "lb_alltime": "All Time",
        "lb_no_data": "No votes claimed yet. Be the first!",
        "lb_entry": "**#{rank}** {mention} — **{votes}** votes",
        "lb_your_rank": "📍 Your rank: **#{rank}** ({votes} votes)",

        # Stats
        "stats_title": "📊 Colombia Vote Party Stats",
        "stats_parties": "🎉 Parties Completed",
        "stats_avg_time": "⏱️ Average Completion",
        "stats_fastest": "⚡ Fastest Party",
        "stats_total_votes": "🗳️ Total Votes Cast",
        "stats_current_rate": "📈 Current Rate",
        "stats_votes_per_hour": "{rate} votes/hour",
        "stats_est_completion": "🕐 Est. Completion",

        # My votes
        "myvotes_title": "🗳️ Your Vote Stats",
        "myvotes_this_cycle": "This Cycle",
        "myvotes_alltime": "All Time",
        "myvotes_streak": "🔥 Current Streak",
        "myvotes_best_streak": "⭐ Best Streak",
        "myvotes_days": "{days} days",
        "myvotes_not_linked": "🔗 You haven't linked your Minecraft username yet!\nUse `/link` to get started.",

        # Link modal
        "link_title": "Link Your Minecraft Username",
        "link_label": "Minecraft Username (IGN)",
        "link_placeholder": "e.g. Notch",
        "link_success": "✅ Linked your Minecraft username to **{ign}**!",
        "link_invalid": "❌ Invalid username. Minecraft usernames are 3-16 characters (letters, numbers, underscores).",

        # Admin commands
        "admin_setup": "✅ Vote Party tracker posted in {channel}!",
        "admin_setremaining": "✅ Remaining votes set to **{value}**.\nProgress: {progress}/{VOTE_GOAL} ({pct}%)\nBaseline adjusted to **{baseline}**.",
        "admin_setbaseline": "✅ New baseline set to **{total}**.\nVote party reset! {VOTE_GOAL} votes to go.",
        "admin_forceupdate": "✅ Update complete!\nRemaining: {remaining} votes",
        "admin_reset": "✅ Vote party reset! All progress cleared.",
        "admin_only": "❌ You need **Administrator** permission to use this command.",
        "text_channel_only": "❌ This command can only be used in a text channel.",

        # Errors
        "error_generic": "❌ An error occurred: {error}",
        "error_server_only": "❌ This button only works in a server.",

        # Ping
        "ping_message": "🚨 {role} Only **{remaining}** votes left until the Vote Party! Vote now!",
    },

    "es": {
        # Embed
        "embed_title": "🇨🇴 Fiesta de Votos Colombia",
        "votes_remaining": "**{remaining}** votos restantes",
        "votes_collected": "{progress} / {VOTE_GOAL} votos recogidos",
        "vote_counts": "🗳️ **Conteo de Votos**",
        "vote_now": "🔗 **¡Vota Ahora!**",
        "vote_on": "Votar en {name}",
        "unavailable": "⚠️ No disponible",
        "updates_every": "Actualiza cada {seconds}s",
        "last_vp": "Última FP: {time}",
        "waiting_first": "Esperando primera actualización...",

        # Status messages
        "status_complete": "🎉 **¡Fiesta de Votos Completa!**",
        "status_imminent": "🔥 **¡Ya casi! ¡Fiesta inminente!**",
        "status_close": "⚡ **¡Cerca! ¡Avisa al servidor!**",
        "status_progress": "💪 **¡Buen progreso! ¡Sigue así!**",
        "status_started": "🗳️ **Fiesta de votos en progreso**",

        # Celebration
        "celebration_title": "🎉 🇨🇴 ¡FIESTA DE VOTOS COMPLETA! 🇨🇴 🎉",
        "celebration_desc": "¡La comunidad alcanzó **{goal} votos**! ¡Hora de la fiesta!",
        "celebration_stats": "⏱️ Completado en **{time}**\n📊 Velocidad: **{speed} votos/hora**",
        "celebration_new_cycle": "Nuevo ciclo iniciando...",
        "celebration_contributions": "🏆 **Mayores Contribuidores Este Ciclo**",

        # Buttons
        "btn_i_voted": "✅ ¡Voté!",
        "btn_notify": "🔔 Notificarme",
        "btn_stop_notify": "🔕 Parar Notificaciones",
        "btn_how_to_vote": "📖 Cómo Votar",
        "btn_remind_me": "⏰ Recordar Después",
        "btn_leaderboard": "🏆 Clasificación",

        # Vote claim
        "vote_claimed": "✅ ¡Voto registrado! Ahora tienes **{total}/3** votos este ciclo.",
        "vote_claimed_streak": "✅ ¡Voto registrado! 🔥 **¡Racha de {streak} días!**",
        "vote_cooldown": "⚠️ ¡Ya has reclamado los **3** votos de este ciclo!\n*Espera al próximo vote party para reclamar más.*",
        "vote_first_link": "🔗 Primero vincula tu usuario de Minecraft con `/link`.",

        # Notifications
        "notify_on": "✅ ¡Ahora serás **notificado** cuando la fiesta de votos esté cerca!",
        "notify_off": "✅ **No** serás notificado para actualizaciones de la fiesta de votos.",
        "role_not_found": "❌ El rol 'VP' no fue encontrado. Pide a un admin que lo cree.",
        "permission_error": "❌ No tengo permiso para gestionar roles. Asegúrate de que mi rol esté **sobre** el rol VP.",

        # Reminder
        "reminder_set": "⏰ ¡Te recordaré en **30 minutos** para votar!",
        "reminder_message": "🔔 **¡Recordatorio!** ¡La Fiesta de Votos de Colombia sigue!\n{remaining} votos restantes. ¡Ven a votar!",
        "reminder_cooldown": "⏳ Ya tienes un recordatorio activo. Intenta en **{time}**.",

        # How to vote
        "how_to_title": "📖 Cómo Votar por Colombia",
        "how_to_desc": "¡Sigue estos pasos para ayudarnos a alcanzar la meta!",
        "how_to_step1": "**1.** Haz clic en los enlaces de voto en el embed de arriba.",
        "how_to_step2": "**2.** Completa el captcha en el sitio de votación.",
        "how_to_step3": "**3.** Después de votar, haz clic en **✅ ¡Voté!** abajo.",
        "how_to_step4": "**4.** Puedes votar una vez por hora en cada sitio.",
        "how_to_tip": "💡 **Tip:** ¡Vota en los 3 sitios para máximo impacto!",

        # Leaderboard
        "lb_title": "🏆 Clasificación de Votos",
        "lb_cycle": "Este Ciclo",
        "lb_alltime": "Todo el Tiempo",
        "lb_no_data": "Aún no hay votos registrados. ¡Sé el primero!",
        "lb_entry": "**#{rank}** {mention} — **{votes}** votos",
        "lb_your_rank": "📍 Tu posición: **#{rank}** ({votes} votos)",

        # Stats
        "stats_title": "📊 Estadísticas de Fiesta de Votos",
        "stats_parties": "🎉 Fiestas Completadas",
        "stats_avg_time": "⏱️ Tiempo Promedio",
        "stats_fastest": "⚡ Fiesta Más Rápida",
        "stats_total_votes": "🗳️ Total de Votos",
        "stats_current_rate": "📈 Velocidad Actual",
        "stats_votes_per_hour": "{rate} votos/hora",
        "stats_est_completion": "🕐 Completado Estimado",

        # My votes
        "myvotes_title": "🗳️ Tus Estadísticas de Votos",
        "myvotes_this_cycle": "Este Ciclo",
        "myvotes_alltime": "Todo el Tiempo",
        "myvotes_streak": "🔥 Racha Actual",
        "myvotes_best_streak": "⭐ Mejor Racha",
        "myvotes_days": "{days} días",
        "myvotes_not_linked": "🔗 ¡Aún no has vinculado tu usuario de Minecraft!\nUsa `/link` para empezar.",

        # Link modal
        "link_title": "Vincular Usuario de Minecraft",
        "link_label": "Usuario de Minecraft (IGN)",
        "link_placeholder": "ej. Notch",
        "link_success": "✅ ¡Vinculaste tu usuario a **{ign}**!",
        "link_invalid": "❌ Usuario inválido. Los nombres son de 3-16 caracteres (letras, números, guiones bajos).",

        # Admin commands
        "admin_setup": "✅ ¡Tracker de Fiesta de Votos publicado en {channel}!",
        "admin_setremaining": "✅ Votos restantes: **{value}**.\nProgreso: {progress}/{VOTE_GOAL} ({pct}%)\nBase ajustada a **{baseline}**.",
        "admin_setbaseline": "✅ Nueva base: **{total}**.\n¡Fiesta reiniciada! {VOTE_GOAL} votos por delante.",
        "admin_forceupdate": "✅ ¡Actualización completa!\nRestantes: {remaining} votos",
        "admin_reset": "✅ ¡Fiesta de votos reiniciada! Todo el progreso borrado.",
        "admin_only": "❌ Necesitas permiso de **Administrador** para usar este comando.",
        "text_channel_only": "❌ Este comando solo se puede usar en un canal de texto.",

        # Errors
        "error_generic": "❌ Ocurrió un error: {error}",
        "error_server_only": "❌ Este botón solo funciona en un servidor.",

        # Ping
        "ping_message": "🚨 {role} ¡Solo **{remaining}** votos para la Fiesta de Votos! ¡Vota ahora!",
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Get a translated string with optional format arguments."""
    strings = STRINGS.get(lang, STRINGS["en"])
    text = strings.get(key, STRINGS["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def get_user_lang(user_id: int, user_langs: dict) -> str:
    """Get the preferred language for a user."""
    return user_langs.get(str(user_id), "en")
