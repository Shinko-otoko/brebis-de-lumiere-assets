# brebis-de-lumiere-assets

Assets pour monter les Reels « brebis parlante » de cadeaux_chretiens_fr.

- `sprites/` : 9 images 768x1376 de la brebis (fond crème uni, même position et même taille) :
  closed, mid, wide, o, ee (formes de bouche), blink (yeux fermés), wave (patte levée), head_tilt, neutral_end.
- `fonts/` : Lora et Nunito Sans (woff2), utilisées pour le hook et les sous-titres.
- `render_talking_reel.py` : script de rendu (bouche calée sur l'audio, hook, sous-titres, appel à l'action).

Liens directs : https://raw.githubusercontent.com/Shinko-otoko/brebis-de-lumiere-assets/main/sprites/closed.png

## Bibliothèque de dessins animés (ajout)
- `bibliotheque/` : personnages (Marc, Claire, Léo), décors vides D1 à D5, 6 poses, 6 animations (clips Seedance + sprites détourés), outils (clip2sprite, asr_words, snap_words, render_story). Voir `bibliotheque/README.md`.
- `histoire-pourquoi-tu-restes/` : feuilles d'animation de Claire et Sarah (12 cases découpées en clips `sprites/`, grilles Wan complètes `grilles/`), 2 scènes à deux personnages (`scenes/`), script de montage `render_reel.py`.
- Personnages : `characters/claire`, `characters/sarah`, `characters/jesus` (image-mère + grille). Décor D6 salle à manger : `decors_d6_salle_a_manger.jpg`. Scène de départ : `scenes/repas_claire_sarah.jpg`.
- Aucun Reel fini ici (dépôt public).
