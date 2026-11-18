# Bibliothèque de dessins animés · Cadeaux Chrétiens (charte Crème éditorial)

Tout le matériel du Reel « Ne dérange pas papa », rangé pour être réutilisé dans d'autres histoires.
Style : dessin animé kawaii plat, trait brun épais, même style que la brebis.

## Personnages (`personnages/`, image-mère de face, fond crème #FAF3E6)
- `marc.png` : Marc, le père (35 ans, barbe, chemise bleu clair).
- `claire.png` : Claire, la mère (cheveux châtains, pull vert sauge, jupe crème).
- `leo.png` : Léo, le fils de 7 ans (t-shirt moutarde, tient un dessin).
Servent de référence pour générer de nouvelles poses (Nano Banana Pro, « Same exact character… »).

## Décors vides (`decors/`, 1536×2752, sans personnage)
- `D1_bureau.png` bureau le soir · `D2_couloir.png` couloir avec porte fermée · `D3_chambre_nuit.png` chambre des parents la nuit
- `D4_chambre_leo.png` chambre d'enfant le matin · `D5_bible.png` Bible ouverte (pages vierges : le verset s'écrit en code)

## Poses (`poses/`, fond crème) : images de départ des animations, aussi utilisables fixes
P1b Marc tape au bureau (casque) · P2 Léo frappe à une porte · P3 Claire parle à un enfant · P4 Marc prie à genoux · P5 Marc, ordinateur fermé · P6 Marc à genoux devant Léo qui montre son dessin

## Animations
- `clips/` : les 6 vidéos sources Seedance 2.5 (5 s, 480p, fond crème).
- `sprites/<nom>/` : les mêmes, détourées image par image (WebP transparent, 25 i/s, 126 images), `sprite.json` = nombre d'images, taille, ancrage bas-centre.
  - A1_marc_tape (boucle) · A2_leo_frappe (boucle) · A3_claire_parle (boucle) · A4_marc_prie (boucle)
  - A5_marc_ferme (une fois : enlève le casque, ferme l'ordinateur) · A6_marc_leo_calin (une fois : montre le dessin puis câlin)
  - `pose_*` : les poses détourées (1 image).
- Les boucles commencent et finissent sur la même image : elles se répètent sans saut.

## Outils (`outils/`)
- `clip2sprite.py <video|image> <dossier> [--fps 25] [--scale 1]` : détoure une vidéo ou une image sur fond uni en sprites.
- `asr_words.py` + `snap_words.py` : horodatent chaque mot de la voix (sous-titres et textes calés sur la voix).
- `render_story.py` : montage du Reel (plans = décor + sprites + zoom lent, textes par partie, sous-titres 3 mots).

## Histoires
- `histoires/marc-ne-derange-pas-papa/` : voix Sulafat (`talk.wav`), texte, mots horodatés.
