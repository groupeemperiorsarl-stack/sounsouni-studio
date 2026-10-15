# Guide du scénariste — « Les Plans de Bakary »

_Version 2 · 15 octobre 2026_

Ce guide explique **comment écrire un script que l'application Sounsouni Studio peut animer toute seule** :
voix, visages, gestes, réactions, décors, bruitages. Tout ce qui est écrit selon ces règles est exécuté
**au mot près**. Ce qui n'est pas écrit n'est pas animé (à part la respiration et les petits mouvements naturels).

---

## 1. Règles générales

- **Durée visée : 3 à 4 minutes** (jamais moins de 3). Repère : 1 minute ≈ 110 à 130 mots de dialogue.
- **Une réplique = une seule personne qui parle.** Si un autre personnage réagit, on l'écrit avec `[RÉACTION …]`.
- **Les indications sont accrochées au mot qui suit** : `{sourire} Bonjour` → le sourire commence sur « Bonjour ».
- **Écrire les mots comme ils doivent être prononcés** (« V.D.B. », « cinq cents », « sounsouni point pro »).
- **Pas d'action impossible** : un personnage ne dit à voix haute que ce que les autres peuvent entendre.
  Ce qu'il pense se met en **PENSÉE** (voir § 4).
- **Plans d'ensemble obligatoires** dès que plusieurs personnages sont concernés (dispute, appel, révélation).
- **Gros plan obligatoire** sur les objets importants (téléphone, argent, brochettes, colis…).

---

## 2. Structure d'un épisode

```
TITRE: Les Plans de Bakary – Épisode 12 : <titre>

DÉCOR: <lieu> · <moment> · ambiance: <sons de fond>
PLAN: <type> [<personnages et postures>]

<répliques, réactions, bruitages…>

DÉCOR: …            ← nouvelle scène
…

FIN: voix off + écran de fin
```

### 2.1 Décors disponibles
| Code | Lieu |
|---|---|
| `KIOSQUE` | Kiosque « Chez Bakary » (thé, café, brochettes) |
| `MARCHÉ` | Grand marché du quartier |
| `ATELIER` | Atelier « Awa Couture » (intérieur) |
| `CABINE` | Cabine de crédit de Fatim (rue, lampadaire) |
| `RUE` | Rue animée du quartier (motos, boutiques) |
| `BUREAU` | Bureau moderne (Karim) |
| `VILLA` | Villa / cour d'une grande maison |
| `SHOWROOM` | Magasin moderne (vitrines) |

Moments : `matin` · `midi` · `après-midi` · `soir` · `nuit` (la lumière s'adapte).
Ambiances : `marché`, `rue calme`, `grillons`, `vent`, `pluie`, `circulation`, `musique lointaine`.
Un nouveau lieu = nouvelle image de décor à fournir (le dire en tête de script : `NOUVEAU DÉCOR: …`).

### 2.2 Personnages (noms à écrire exactement ainsi)
`BAKARY` · `AWA` · `MODIBO` · `DIASABI` · `SALI` · `FATIM` · `MIMI` · `SEYDOU` (livreur) · `KADI` (Tantie Kadi) · `MOUSSA` · `KARIM` · `VENDEUSE` (de tomates) · `VOIX_OFF`
Nouveau personnage = l'annoncer en tête : `NOUVEAU PERSONNAGE: NOM — description physique et tenue`.

### 2.3 Types de plans
| Écriture | Ce que l'on voit |
|---|---|
| `PLAN: large [A, B, C]` | Plan d'ensemble : tous les personnages cités sont visibles |
| `PLAN: deux [A, B]` | Deux personnages face à face |
| `PLAN: gros A` | Visage et buste de A (par défaut pour celui qui parle) |
| `PLAN: très gros A` | Visage seul (réaction forte, choc) |
| `PLAN: objet <objet>` | Gros plan sur un objet. Objets connus : téléphone, grill, robe trouée, robe réparée, voiture de Karim, boîte (pleine / vide), gâteau(x) / un seul gâteau, billets, carte de recharge, colis / cadeau, lettre / message. Autre objet → son nom s'affiche en gros. |
| `PLAN: écran <texte>` | Écran de téléphone / application Sounsouni (texte affiché) |
| `PLAN: 3 s · …` | Plan sans parole d'une durée donnée |

Sans indication, l'application filme **celui qui parle en gros plan**.
Postures (entre crochets) : `assis`, `debout`, `au grill`, `sur le banc`, `marche`, `court`, `de dos`.

---

## 3. Écrire une réplique

```
NOM (émotion · regarde: <cible> · voix: <manière>)
Texte de la réplique, avec {indications} accrochées aux mots.
```

- **émotion** (de base pour toute la réplique) : voir § 5.1.
- **regarde** : `Bakary`, `Awa`… (un personnage), `bas`, `haut`, `loin`, `caméra`, `téléphone`.
- **voix** (manière de parler) : `normal`, `chuchote`, `crie`, `vite`, `lentement`, `rit en parlant`,
  `au téléphone` (son de haut-parleur), `essoufflé`, `en pleurant`.

Exemple :
```
MODIBO (taquin · regarde: Bakary · voix: normal)
Bakarin ! {sourcils_haut} Alors, cette nuit, tu as bien dormi ? {penche_tete} Ou bien {sourire_malin} tu as rêvé de Fatim ?
```

---

## 4. Pensées, appels, voix off

```
PENSÉE AWA (hésitante · regarde: loin)
Hmm… {moue} J'ai encore envie de goûter ces brochettes…
```
→ bulle de pensée, la bouche ne bouge pas, voix intérieure.

```
FATIM (tendre · voix: au téléphone)
Bakary… c'est Fatim. Je voulais juste entendre ta voix.
```
→ voix déformée « haut-parleur ». Si on doit voir le téléphone : `PLAN: objet téléphone` juste avant.

```
VOIX_OFF (chaleureuse)
Sur Sounsouni, chaque petit commerce a sa boutique…
```

---

## 5. Les indications `{…}` (visage, tête, corps)

Elles se placent **juste avant le mot** où l'action commence. Elles durent jusqu'à la fin de la phrase,
ou jusqu'à `{neutre}`. On peut en combiner deux : `{choc}{recule}`.

### 5.1 Émotions (visage)
| Indication | Effet |
|---|---|
| `{neutre}` | Retour au visage normal |
| `{sourire}` | Sourire bouche fermée |
| `{grand_sourire}` | Sourire avec les dents |
| `{sourire_malin}` | Sourire en coin, malicieux |
| `{rire}` | Rire (dents, tête en arrière, épaules qui sautent) |
| `{rire_retenu}` | Pouffe, se retient de rire |
| `{colere}` | Sourcils froncés, mâchoire serrée |
| `{furieux}` | Colère forte, tremblement |
| `{choc}` | Yeux écarquillés, bouche ouverte |
| `{surpris}` | Sourcils hauts, petit recul |
| `{peur}` / `{panique}` | Yeux grands ouverts, sueur |
| `{triste}` | Sourcils relevés au centre, regard bas |
| `{gene}` | Petit sourire forcé, regard qui fuit |
| `{mepris}` | Lèvre relevée d'un côté, yeux plissés |
| `{mefiant}` / `{yeux_plisses}` | Yeux plissés |
| `{amoureux}` | Regard rêveur, cœurs |
| `{fier}` | Menton levé, poitrine bombée |
| `{moue}` | Lèvres pincées, hésitation |
| `{degout}` | Nez froncé |
| `{innocent}` | Grand sourire naïf |

### 5.2 Tête et regard
`{hoche_tete}` (oui) · `{secoue_tete}` (non) · `{penche_tete}` · `{tourne_vers:Nom}` · `{detourne_regard}` ·
`{leve_yeux_ciel}` · `{regarde_bas}` · `{clin_oeil}` · `{cligne}` · `{ferme_yeux}`

### 5.3 Corps
`{recule}` · `{avance}` · `{sursaut}` · `{hausse_epaules}` · `{soupir}` · `{tremble}` · `{bombe_torse}` ·
`{se_penche}` (confidence) · `{s_affale}` (découragé) · `{sueur}` · `{rougit}`

> Gestes des bras et des mains (pointer du doigt, mains sur la tête, croiser les bras) :
> ils demandent **une image de cette posture**. Les écrire ainsi : `{POSE: mains sur la tête}`.
> La liste des postures à générer sera envoyée à Issa avec les prompts d'images.

### 5.4 Effets graphiques
`{coeurs}` · `{etoiles}` · `{eclair}` · `{fumee_tete}` (colère) · `{goutte}` (gêne) · `{point_exclamation}` ·
`{point_interrogation}` · `{autocollant:"TEXTE"}` (ex. `{autocollant:"LOSER !"}`)

---

## 6. Réactions, bruitages, écrans `[…]`

Une ligne à part, juste **après la réplique concernée**. `sur "<mot>"` = l'instant exact où le mot est dit.

```
[RÉACTION BAKARY sur "Fatim": choc, recule]
[RÉACTION MODIBO: rire_retenu]                 ← à la fin de la réplique
[BRUITAGE sur "Fatim": tonnerre]
[BRUITAGE: sonnerie de téléphone]
[ÉCRAN 3 s: Appel entrant : Fatim]
[MUSIQUE: suspense]                             ← change l'ambiance musicale
[SILENCE 3 s: grillon]                          ← pause comique
```

Bruitages connus : `sonnerie`, `bip`, `clic`, `notification`, `pièces`, `porte qui claque`, `pas`, `talons`,
`tonnerre`, `grillon`, `whoosh`, `pop`, `fracas`, `grésillement`, `rires de foule`, `applaudissements`,
`klaxon`, `moto`, `coq`, `chien`. (Un bruit absent de la liste peut être demandé, il sera ajouté.)

Musiques : `joyeuse`, `suspense`, `romantique`, `drôle`, `triste`, `action`.

---

## 7. Fin d'épisode (obligatoire)

```
FIN:
[ÉCRAN: À suivre…]
VOIX_OFF (chaleureuse)
<phrase publicitaire Sounsouni adaptée à l'épisode>
VOIX_OFF (lentement)
Pour télécharger l'application Sounsouni, rendez-vous sur le site sounsouni point pro.
[ÉCRAN FIN: logo · sounsouni.pro · Android · iPhone bientôt]
```

---

## 8. Exemple complet (court)

```
DÉCOR: KIOSQUE · soir · ambiance: grillons
PLAN: large [Bakary assis, Modibo sur le banc, Diasabi au grill]

MODIBO (taquin · regarde: Bakary)
Bakarin ! {sourcils_haut} Alors, cette nuit, tu as bien dormi ? {penche_tete} Ou bien {sourire_malin} tu as rêvé de Fatim ?
[RÉACTION DIASABI: rire_retenu]

BAKARY (gene · regarde: bas)
Arrête, Van. {secoue_tete} Ce n'est pas drôle. {soupir} Awa ne me parle plus.

MODIBO (sérieux · regarde: Bakary)
{se_penche} Envoie-lui un cadeau sur Sounsouni. Ça arrive directement à son atelier.

BAKARY (pensif · regarde: loin)
Un cadeau… {moue} Hmm… {grand_sourire}{point_exclamation} Des fleurs ! Oui, des fleurs !

PLAN: large [Bakary, Modibo, Awa marche]
[BRUITAGE: talons]

AWA (mepris · regarde: Bakary · voix: normal)
{yeux_plisses} Des fleurs ? {recule} Garde-les pour ta {mepris} Fatim.
[RÉACTION BAKARY sur "Fatim": choc, sursaut]
[BRUITAGE sur "Fatim": tonnerre]

PLAN: 2 s · très gros Bakary · {panique}{sueur}
[SILENCE 2 s: grillon]

MODIBO (rire · regarde: Bakary · voix: rit en parlant)
{rire} Ha ha ha ! Mon frère, tu es vraiment dans le pétrin.
```

---

## 9. Liste de vérification avant d'envoyer un script

- [ ] Durée estimée entre 3 et 4 minutes (≈ 350 à 500 mots de dialogue)
- [ ] Chaque scène commence par `DÉCOR:` et un `PLAN:`
- [ ] Un plan d'ensemble à chaque moment où plusieurs personnages sont concernés
- [ ] Chaque réplique a une émotion et un `regarde:`
- [ ] Les mots forts / choquants ont une `[RÉACTION …]` des autres personnages
- [ ] Les pensées sont en `PENSÉE`, les appels en `voix: au téléphone`
- [ ] Les objets importants ont un `PLAN: objet`
- [ ] Nouvelles postures / nouveaux décors / nouveaux personnages annoncés en tête du script
- [ ] Fin d'épisode avec voix off Sounsouni et écran de fin

---

## 10. Lancer l'application

```
python -m studio mon_episode.txt                      # vidéo complète
python -m studio mon_episode.txt --plans-seulement    # seulement l'aperçu des plans (rapide)
```

Résultat dans `sortie_mon_episode/` :
- `apercu_plans.png` — toutes les images-clés, plan par plan : **à regarder avant le rendu complet** ;
- `mon_episode.mp4` (haute qualité) et `mon_episode_leger.mp4` (moins de 28 Mo, pour WhatsApp) ;
- `journal.txt` — ce que l'application a fait, et les avertissements (réplique mal prononcée, pose manquante…).

Si on corrige le script et qu'on relance, les voix déjà bonnes sont réutilisées (beaucoup plus rapide).
Temps sur un ordinateur sans carte graphique : environ 2 minutes par réplique pour les voix, puis 15 à 20 minutes pour l'image.
