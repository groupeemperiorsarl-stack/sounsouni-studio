"""
Sounsouni Studio – Règle de publication automatique (v2), fournie par la discussion « scénariste » le 21/10/2026.
La voix off (assets/publication/voix_youtube.wav) est faite avec la voix VOIX_OFF de la série (Chatterbox, 4,2 s).

À partir de l'épisode complet, fabrique automatiquement 4 vidéos :
  - YouTube (complet)  : l'épisode entier, sans bandeau
  - TikTok             : coupée à 3:00, bandeau de 2:50 à 3:00
  - YouTube Shorts     : coupée à 2:58, bandeau de 2:50 à 2:58
  - Facebook Reels     : coupée à 1:00, bandeau de 0:50 à 1:00

Pendant le bandeau :
  - logo YouTube + « Suivez tout l'épisode sur notre chaîne YouTube : Sounsouni »
  - « sounsouni.pro » écrit en petit (visuel seulement)
  - voix off : « Si vous voulez suivre tout l'épisode, rendez-vous sur notre
    chaîne YouTube Sounsouni. » (fichier voix_youtube.wav, voir plus bas)
  - le son de l'épisode baisse pendant que la voix off parle

LA VOIX OFF : générer UNE SEULE FOIS la phrase avec la voix VOIX_OFF de la série
et l'enregistrer sous le nom « voix_youtube.wav » (ou .mp3) à côté de ce fichier.
Elle sera réutilisée pour tous les épisodes. Sans ce fichier, les vidéos sont
quand même fabriquées, mais sans voix off (un avertissement s'affiche).

Utilisation seule :
    python publication.py sortie_mon_episode/mon_episode.mp4
Utilisation dans l'application (à la fin du rendu) :
    from publication import fabriquer_versions
    fabriquer_versions("sortie_mon_episode/mon_episode.mp4")
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------
# RÈGLES (modifier ici seulement)
# ------------------------------------------------------------------
REGLES = [
    # nom,          coupure (s), bandeau à partir de (s)
    ("tiktok",      180.0,       170.0),
    ("shorts",      178.0,       170.0),
    ("facebook",     60.0,        50.0),
]
TEXTE_BANDEAU = "Suivez tout l'épisode sur notre chaîne YouTube : Sounsouni"
TEXTE_SITE = "sounsouni.pro"
DOSSIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "publication")
VOIX_OFF = [os.path.join(DOSSIER, "voix_youtube.wav"),
            os.path.join(DOSSIER, "voix_youtube.mp3")]
DELAI_VOIX = 0.6            # la voix commence 0,6 s après l'apparition du bandeau
VOLUME_EPISODE = 0.25       # volume de l'épisode pendant la voix off (25 %)
COULEUR_FOND = (18, 18, 18, 225)        # noir légèrement transparent
COULEUR_TEXTE = (255, 255, 255, 255)
ROUGE_YOUTUBE = (255, 0, 0, 255)
POSITION_VERTICALE = 0.70              # 0 = haut, 1 = bas (centre du bandeau)
_UI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ui")
POLICE = os.path.join(_UI, "Poppins-Bold.ttf")          # police de la série (repli : DejaVu)
POLICE_SITE = os.path.join(_UI, "Poppins-Medium.ttf")
# ------------------------------------------------------------------


def _infos(fichier):
    sortie = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,width,height",
         "-of", "json", fichier],
        capture_output=True, text=True, check=True).stdout
    data = json.loads(sortie)
    duree = float(data["format"]["duration"])
    image = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    son = any(s["codec_type"] == "audio" for s in data["streams"])
    if image is None:
        return duree, 0, 0, son
    return duree, int(image["width"]), int(image["height"]), son


def _police(chemin, taille):
    for c in (chemin, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(c, taille)
        except OSError:
            pass
    return ImageFont.load_default()


def _lignes(texte, police, largeur_max, dessin):
    mots, lignes, ligne = texte.split(), [], ""
    for mot in mots:
        essai = (ligne + " " + mot).strip()
        if dessin.textlength(essai, font=police) <= largeur_max:
            ligne = essai
        else:
            if ligne:
                lignes.append(ligne)
            ligne = mot
    if ligne:
        lignes.append(ligne)
    return lignes


def _logo_youtube(dessin, x, y, largeur):
    """Bouton lecture rouge avec triangle blanc (icône YouTube)."""
    hauteur = int(largeur * 0.70)
    dessin.rounded_rectangle([x, y, x + largeur, y + hauteur],
                             radius=int(hauteur * 0.28), fill=ROUGE_YOUTUBE)
    cx, cy, t = x + largeur / 2, y + hauteur / 2, hauteur * 0.24
    dessin.polygon([(cx - t * 0.8, cy - t), (cx - t * 0.8, cy + t),
                    (cx + t * 1.05, cy)], fill=(255, 255, 255, 255))
    return hauteur


def _bandeau(largeur, hauteur, chemin_png):
    base = min(largeur, hauteur)
    taille = max(18, int(base * 0.042))
    taille_site = max(14, int(base * 0.030))
    marge = int(base * 0.03)
    police = _police(POLICE, taille)
    police_site = _police(POLICE_SITE, taille_site)

    calque = Image.new("RGBA", (largeur, hauteur), (0, 0, 0, 0))
    dessin = ImageDraw.Draw(calque)
    largeur_bandeau = int(largeur * 0.92)
    largeur_logo = int(taille * 2.6)
    largeur_texte = largeur_bandeau - largeur_logo - 3 * marge
    lignes = _lignes(TEXTE_BANDEAU, police, largeur_texte, dessin)
    interligne = int(taille * 1.25)
    h_texte = interligne * len(lignes) + int(taille_site * 1.4)
    h_logo = int(largeur_logo * 0.70)
    h_bandeau = 2 * marge + max(h_texte, h_logo)

    x0 = (largeur - largeur_bandeau) // 2
    y_centre = int(hauteur * POSITION_VERTICALE)
    y0 = max(0, min(hauteur - h_bandeau, y_centre - h_bandeau // 2))
    dessin.rounded_rectangle([x0, y0, x0 + largeur_bandeau, y0 + h_bandeau],
                             radius=int(taille * 0.6), fill=COULEUR_FOND)

    # logo à gauche, centré verticalement
    _logo_youtube(dessin, x0 + marge, y0 + (h_bandeau - h_logo) // 2, largeur_logo)

    # texte à droite du logo, centré dans sa zone
    zone_x = x0 + 2 * marge + largeur_logo
    y = y0 + (h_bandeau - h_texte) // 2
    for ligne in lignes:
        l = dessin.textlength(ligne, font=police)
        dessin.text((zone_x + (largeur_texte - l) / 2, y), ligne,
                    font=police, fill=COULEUR_TEXTE)
        y += interligne
    l = dessin.textlength(TEXTE_SITE, font=police_site)
    dessin.text((zone_x + (largeur_texte - l) / 2, y + int(taille_site * 0.1)),
                TEXTE_SITE, font=police_site, fill=(220, 220, 220, 255))
    calque.save(chemin_png)


def _trouver_voix():
    for chemin in VOIX_OFF:
        if os.path.exists(chemin):
            return chemin
    return None


def _version(video, sortie, coupure, debut, png, son, voix):
    t_voix = debut + DELAI_VOIX
    entrees = ["-i", video, "-loop", "1", "-i", png]
    filtre = (f"[1:v]format=rgba,fade=in:st={debut}:d=0.4:alpha=1[b];"
              f"[0:v][b]overlay=0:0:enable='gte(t,{debut})':shortest=1[v]")
    fin_son = f"afade=out:st={max(0, coupure - 0.6)}:d=0.6"
    carte_son = None

    if voix:
        entrees += ["-i", voix]
        ms = int(t_voix * 1000)
        voix_f = f"[2:a]adelay={ms}|{ms},apad[vo]"
        if son:
            filtre += (f";[0:a]volume='if(gte(t,{debut}),{VOLUME_EPISODE},1)':eval=frame[ep];"
                       f"{voix_f};[ep][vo]amix=inputs=2:duration=first:normalize=0,{fin_son}[a]")
        else:
            filtre += f";{voix_f};[vo]{fin_son}[a]"
        carte_son = "[a]"
    elif son:
        filtre += f";[0:a]{fin_son}[a]"
        carte_son = "[a]"

    cmd = ["ffmpeg", "-y", "-v", "error"] + entrees + [
        "-filter_complex", filtre, "-map", "[v]"]
    if carte_son:
        cmd += ["-map", carte_son, "-c:a", "aac", "-b:a", "160k"]
    cmd += ["-t", f"{coupure}", "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", sortie]
    subprocess.run(cmd, check=True)


def fabriquer_versions(video, dossier=None):
    """Fabrique les 4 vidéos et renvoie la liste des fichiers créés."""
    dossier = dossier or os.path.dirname(os.path.abspath(video))
    nom = os.path.splitext(os.path.basename(video))[0]
    duree, largeur, hauteur, son = _infos(video)
    voix = _trouver_voix()
    if voix is None:
        print("  ⚠ voix_youtube.wav introuvable : versions fabriquées SANS voix off.")
    else:
        d_voix = _infos(voix)[0]
        for plateforme, coupure, debut in REGLES:
            if DELAI_VOIX + d_voix > coupure - debut:
                print(f"  ⚠ la voix off ({d_voix:.1f} s) dépasse le bandeau {plateforme} "
                      f"({coupure - debut:.0f} s) : elle sera coupée à la fin.")
    crees = []

    complet = os.path.join(dossier, f"{nom}_youtube.mp4")
    if os.path.abspath(complet) != os.path.abspath(video):
        shutil.copyfile(video, complet)
    crees.append(complet)

    with tempfile.TemporaryDirectory() as tmp:
        png = os.path.join(tmp, "bandeau.png")
        _bandeau(largeur, hauteur, png)
        for plateforme, coupure, debut in REGLES:
            fin = min(coupure, duree)
            debut_reel = max(0.0, fin - (coupure - debut))
            sortie = os.path.join(dossier, f"{nom}_{plateforme}.mp4")
            _version(video, sortie, fin, debut_reel, png, son, voix)
            crees.append(sortie)
            print(f"  ✔ {plateforme:9s} {fin:6.1f} s · bandeau dès {debut_reel:.1f} s → {sortie}")
    return crees


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Utilisation : python publication.py chemin/episode.mp4")
        sys.exit(1)
    print("Fabrication des versions de publication…")
    fabriquer_versions(sys.argv[1])
    print("Terminé.")
