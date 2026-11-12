# ARA — proposition de coque v0.5

**État : étude mécanique paramétrique, pas validation de fabrication.**

Le modèle a été reconstruit en partant du cahier des charges `DESIGN.md` et du modèle d'origine `ara_base_shell.scad` v0.4. Il ne modifie pas les choix de composants électroniques ; il change la manière de les disposer.

## Composition

- `ARA_shell_v05.scad` : source OpenSCAD complète. Paramètre `part` : `assembled`, `exploded`, `print`, `front`, `back`, `retainer`, `button`, `pcb`, `rear_view`. `show_components` affiche les maquettes électroniques sans les incorporer aux STL.
- `ara_v05_front.stl` : demi-coque avant (écran et microphone, tête de vis).
- `ara_v05_back.stl` : demi-coque arrière (batterie, haut-parleur, supports PCB, USB-C, boutons, points accessoires).
- `ara_v05_retainer.stl` : cadre de maintien de l'écran à visser depuis l'intérieur.
- `ara_v05_button.stl` : **poussoir d'étude** ; 4 exemplaires envisagés, à redimensionner après choix des interrupteurs.
- `ara_v05_pcb.stl` : **volume de contrôle**, pas un circuit électronique ni des fichiers Gerber.
- Images PNG : rendus OpenSCAD illustratifs.

## Géométrie

- Encombrement de la coque **Ø 60 mm × 22 mm**, hors boutons. L'original faisait 21 mm d'épaisseur.
- Demi-coque arrière : 16 mm, demi-coque avant : 6 mm.
- Joint médian plat + trois pions de centrage, quatre vis de fermeture depuis l'avant.
- Écran `ET013TT1` (27,1 × 28,4 × 0,4 mm) inséré par l'intérieur et maintenu par une pièce séparée, sans collage permanent.
- Batterie `LP702030` (enveloppe d'étude 32 × 20,5 × 7,3 mm) au fond : guides courts avec 0,55 mm de jeu nominal sur les côtés, sortie de câble vers le haut.
- PCB de **forme circulaire évidée aux fixations**, Ø 52 mm, fixé à 4 entretoises hors du volume de la batterie. L'ESP32 est représenté en 25,5 × 18 × 3,1 mm sur sa face supérieure.
- USB-C prévu à 6 h et raccordé à la tranche inférieure du PCB de forme libre, **pas** au petit PCB rectangulaire de la v0.4.
- Haut-parleur 20 × 14 × 3,2 mm à l'arrière, grille directement dans le fond, avec emplacement de joint d'étanchéité acoustique.
- Quatre poussoirs radiaux répartis sur deux côtés ; ils restent des volumes **indicatifs**.
- Deux points de fixation arrière espacés de 6 mm pour un accessoire externe optionnel (passant de chaîne, cordon, etc.).

## Ordre d'assemblage envisagé

1. Installer le haut-parleur, joint côté grille, dans le fond arrière.
2. Placer la batterie, faire cheminer les fils vers le JST-PH ; éviter toute pression sur sa poche.
3. Monter les quatre poussoirs par l'intérieur avant le PCB.
4. Fixer le PCB sur les quatre entretoises ; vérifier que l'USB-C atteint la découpe et que les boutons atteignent les contacts.
5. Installer l'écran E-Ink par l'intérieur de la face avant, connecter soigneusement la nappe FPC, positionner le cadre de retenue avec une faible pression sur la **bordure inactive**.
6. Présenter la façade sur les trois pions et visser les quatre points de fermeture.

## À valider avant un prototype électronique fonctionnel

**Bloquants**

- **Implantation réelle du PCB** : les trous, boutons sur tranche, USB-C, composants d'alimentation et le connecteur FPC doivent être dessinés en CAO électronique et transférés au modèle mécanique.
- **Antenne ESP32-S3** : sa zone de dégagement RF et le positionnement des métaux du haut-parleur/batterie sont impératifs ; le disque PCB actuellement affiché ne comprend **pas** le keep-out cuivre et le module n'a pas été replacé pour l'optimiser.
- **Port USB-C** : résolu (2026-11-11) — `SHOU HAN TYPE-C 6P CB1.6(073)` (LCSC C2858274), 6 broches (VBUS×2, GND×2, CC1, CC2), volontairement sans D+/D- puisque l'OTA firmware passe par BLE. Corps réel 8,94×3,16 mm, ~6,8 mm de profondeur — le modèle utilisait déjà une découpe cohérente (9,7×3,8 mm), mais la hauteur `usbc_z` a été corrigée : elle plaçait le connecteur ~2,2 mm trop bas (calée sur la mi-épaisseur du PCB au lieu du dessus du PCB + moitié de la hauteur réelle du connecteur).
- **LiPo** : confirmer la taille réelle et le débattement des câbles/JST-PH ; le jeu des guides doit être confirmé avec les dimensions à tolérance maximale, et sans contrainte ni compression sur la batterie.
- **Écran E-Ink** : plans complets de la nappe FPC, face active, rayon de courbure admissible, jeu/verre de protection optionnel et méthode de retenue non traumatisante. La version proposée n'est pas protégée contre l'eau/la poussière.
- **Vis** : choisir les vis et vérifier alésages pilotes réels suivant le matériau ; les valeurs nominales M2 utilisées sont illustratives.

**Essais recommandés**

- Imprimer d'abord en PLA à faible coût pour contrôler le passage des composants ; choisir PETG ou autre matériau adapté ensuite.
- Tester l'intelligibilité du haut-parleur lorsque le boîtier est posé sur une surface ou porté : une grille arrière peut être partiellement obturée.
- Vérifier le rendu des trous de grille de Ø1,45 mm selon buse / hauteur de couche.
- Vérifier l'actionnement des quatre poussoirs, les efforts sur les interrupteurs et l'absence d'activation accidentelle.
- Vérifier la sortie et la dissipation thermique de la charge batterie et de l'amplificateur.

## État de validation effectué

OpenSCAD a calculé un maillage STL **fermé** pour chaque pièce distincte (`front`, `back`, `retainer`, `button`, `pcb`) ; ceci prouve la cohérence topologique des surfaces exportées, **pas** l'absence d'interférence sur un assemblage physique réel.

**Propriété intellectuelle** : cette proposition de modèle est distribuée sous CC BY-SA 4.0 pour pouvoir être modifiée et partagée dans l'esprit du projet. Ce document n'est pas une vérification des obligations liées aux composants logiciels mentionnés dans `DESIGN.md`.
