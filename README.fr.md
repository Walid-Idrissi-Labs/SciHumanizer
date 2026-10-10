# SciHumanizer

[English](README.md) · Français

SciHumanizer est un skill pour Claude qui écrit et réécrit des textes en français et en anglais de façon qu'ils ne se lisent plus comme des textes de machine, puis vérifie son propre travail à l'aide de scripts. Nous l'avons conçu pour l'écriture scientifique et universitaire (sections d'articles, résumés, mémoires, rapports), mais son étalonnage couvre aussi les tribunes, les articles de vulgarisation et les essais.

Quand un texte « fait IA », le remède habituel est une liste de mots à éviter. Les travaux sur lesquels le projet s'appuie montrent pourquoi une telle liste ne suffit pas : selon l'une des études, un détecteur atteignait encore un score F1 de 99,5 sur des textes produits avec des consignes de style comme « écris à la manière d'un lycéen ». Ce qui trahit la prose des modèles relève surtout de la statistique : la grammaire, la longueur des phrases, la proportion de noms propres et de chiffres, autant de traits que personne ne voit en relisant un brouillon. Le skill les mesure donc. Un analyseur compare chaque brouillon à des textes humains de même langue, de même registre et de même longueur. Un registre des faits vérifie ensuite qu'aucun chiffre, aucune citation, aucune négation ni aucune réserve n'a changé en route, tandis qu'un contrôle de longueur refuse qu'un nombre de mots soit atteint par du remplissage.

Cette page n'est qu'un résumé : les résultats complets, la méthode et les limites figurent dans le [README anglais](README.md), et le catalogue des habitudes propres au français dans [`references/french.md`](references/french.md).

## Une réécriture, avant et après

La phrase de gauche ouvre une introduction qu'un modèle a rédigée à partir d'un résumé (l'étude est inventée et sert de cas d'essai). À droite, la réécriture conserve tous les faits et tous les termes du domaine ; seule la grammaire change, puisqu'une phrase de 62 mots en devient trois et que les verbes *être* et *avoir* reviennent.

| Avant | Après |
|---|---|
| Le réchauffement climatique s'accompagne d'une augmentation bien documentée de la fréquence et de l'intensité des vagues de chaleur, dont les conséquences sanitaires pèsent de manière disproportionnée sur les populations âgées, plus vulnérables aux effets physiologiques de la chaleur extrême en raison du vieillissement des mécanismes de thermorégulation et de la prévalence élevée de comorbidités cardiovasculaires, respiratoires et rénales dans cette tranche d'âge. | Avec le réchauffement climatique, les vagues de chaleur sont devenues plus fréquentes et plus intenses ; ce fait est bien documenté. Ce sont les personnes âgées qui en souffrent le plus. Avec l'âge, la thermorégulation fonctionne moins bien, et les maladies cardiovasculaires, respiratoires et rénales sont fréquentes dans cette tranche d'âge : la chaleur extrême est donc plus dangereuse pour elles que pour le reste de la population. |

Sur l'ensemble de l'introduction, les scripts donnent les mesures suivantes.

| Mesure | Brouillon | Réécriture | Médiane humaine |
|---|---|---|---|
| Mots | 698 | 687 | |
| Score composite (seuil : 0,65) | 1,13 | 0,27 | |
| Longueur moyenne des phrases, en mots | 46,5 | 27,5 | 27 |
| *être, en, avoir, dans* pour 100 tokens | 2,6 | 6,9 | 6,5 |
| Longueur moyenne des mots, en lettres | 5,83 | 5,29 | 5,37 |
| Chiffres et citations modifiés, d'après le registre des faits | | 0 | |

Il a fallu trois brouillons successifs, qui se trouvent tous dans [`examples/D-rewrite-introduction-fr`](examples/D-rewrite-introduction-fr), avec le brouillon de départ et le résumé fourni par l'auteur.

## Ce que les mesures disent du français des modèles

Pour le français, l'étalonnage repose sur 747 textes humains antérieurs à 2020 (articles de recherche, résumés, presse, vulgarisation, articles encyclopédiques) et sur 140 textes de deux modèles (les gammes Sonnet et Haiku de Claude), auxquels nous avions demandé de traiter les mêmes sujets. Le résultat le plus net est que les modèles compriment leur prose. En anglais, ce sont les articles et les prépositions qui disparaissent ; en français, c'est le verbe. Dans les articles scientifiques, les deux modèles emploient à peine plus de la moitié des *être*, *avoir*, *en* et *dans* que l'on trouve chez les auteurs humains, et le passé composé, le passif ou « il y a » disparaissent du même coup. Des verbes lourds (*constituer, demeurer*), des noms qui encadrent sans rien apporter (*enjeu, contexte*) et deux fois plus d'adverbes en *-ment* prennent leur place, comme le montrent les médianes du tableau, calculées sur la prose scientifique française à 450 mots.

| Habitude | Humains | Grand modèle | Petit modèle |
|---|---|---|---|
| *être, en, avoir, dans* pour 100 tokens | 6,39 | 3,66 | 3,52 |
| Auxiliaires, en % des tokens | 3,47 | 1,49 | 1,57 |
| Longueur moyenne des phrases, en mots | 26,6 | 42,5 | 20,6 |
| Noms propres, sigles et chiffres, en % des tokens | 5,26 | 1,55 | 1,48 |
| Adverbes en *-ment*, en % des tokens | 0,84 | 1,70 | 1,70 |
| Parenthèses pour 1 000 mots | 6,68 | 0 | 2,20 |

## Installation

Les scripts demandent Python 3.8 ou une version plus récente et n'utilisent que la bibliothèque standard : aucune installation par pip n'est nécessaire, et aucun appel réseau n'a lieu. Avec Claude Code, la voie la plus courte est d'installer le skill comme plugin, par les deux commandes ci-dessous.

```bash
claude plugin marketplace add Walid-Idrissi-Labs/SciHumanizer
claude plugin install scihumanizer@scihumanizer
```

Il est également possible de cloner le dépôt à l'emplacement des skills. Dans ce cas, le skill est disponible pour tous vos projets, et un `git pull` suffit ensuite pour la mise à jour.

```bash
git clone https://github.com/Walid-Idrissi-Labs/SciHumanizer.git ~/.claude/skills/scihumanizer
```

Pour les applications Claude, chaque [version publiée](https://github.com/Walid-Idrissi-Labs/SciHumanizer/releases/latest) comprend une archive `scihumanizer-skill.zip`, à téléverser depuis les réglages (Customize, puis Skills). Nous n'avons pas encore essayé cette voie.

## Utilisation

Aucune syntaxe particulière n'est requise : le skill se déclenche pour des demandes formulées comme celles-ci.

```text
Humanise l'introduction de brouillon.md. Les faits sont dans resume.md : aucun ne doit changer.
Rédige la discussion à partir de ces résultats, environ 700 mots, pour des relecteurs en écologie routière.
Est-ce que ce texte fait « écrit par une IA » ? Ne le réécris pas, dis-moi seulement ce qui cloche.
Voici trois pages que j'ai écrites l'an dernier. Continue le chapitre 2 dans mon style.
```

En réponse, vous recevez le texte, suivi d'un bloc de vérification comme celui de la réécriture présentée plus haut :

```text
Vérification (registre scientifique, français)
- Grille : composite 1,13 -> 0,27 (seuil 0,65 à cette longueur), PASS ; aucun signal classique
- Principaux écarts corrigés : longueur des phrases 46 -> 27 mots ; être/avoir/en/dans 2,6 -> 6,9
  pour 100 ; participiales après virgule 4 -> 0 ; parenthèses 0 -> 3
- Encore du côté IA : spécificité (le résumé ne nomme ni lieux, ni personnes, ni instruments)
- Longueur : 687 mots pour une cible de 700 (630-770), ON TARGET
- Registre des faits (--facts résumé) : OK ; chiffres ajoutés issus du résumé : 1 km, 1,9 million,
  65 ans, 12 villes, 2008-2018
- Retiré car absent du résumé (à rétablir si c'est exact) : villes « aux climats et aux
  morphologies urbaines contrastés »
- Repris du brouillon, non vérifié (à citer ou à supprimer) : station de référence « en
  périphérie des villes » ; estimations « produites de façon routinière pour de nombreuses
  villes européennes » ; écarts de « plusieurs degrés » à « quelques kilomètres »
- Équivalence des paragraphes : tous >= 4/5
```

Si la demande précise les faits (des notes, un résumé, les données), le lecteur visé, la longueur souhaitée et, quand vous en avez un, un échantillon de votre propre prose, le résultat est nettement meilleur. En revanche, le skill n'invente aucun détail pour améliorer un score ; lorsque les notes ne suffisent pas à remplir la longueur demandée, il rend un texte plus court en indiquant ce qui manque.

Sans modèle, les scripts fonctionnent aussi seuls : la langue est détectée automatiquement, et les rapports sont rédigés en anglais.

```bash
python3 scripts/sci_metrics.py analyze brouillon.md --register scientific --sentences
python3 scripts/sci_metrics.py analyze tribune.md --register general --target-words 600 --source notes.md
python3 scripts/fact_ledger.py source.md brouillon.md --facts faits.md
```

## Limites

- L'étalonnage de la grille repose sur deux modèles d'une seule famille : un autre modèle peut s'écarter des textes humains selon des directions qu'elle ne pèse pas.
- Pour le français, la prose générale courte est le cas le plus faible, puisqu'à 150 mots 22 % des textes d'IA non retouchés passent la grille, et encore 8 % à 300 mots.
- Environ un texte humain sur sept échoue ; un score décrit donc une prose, jamais l'identité de son auteur.
- Le corpus scientifique humain provient de la médecine (PubMed Central, presque entièrement une seule revue) et des sciences humaines et sociales (OpenEdition), sans physique, chimie ni ingénierie.
- Le skill n'a pas été essayé contre les détecteurs commerciaux et ne promet rien à leur sujet.
- Un texte produit avec le skill est toujours un texte écrit avec l'aide d'une IA : lorsqu'une revue, une université ou un employeur demande de le déclarer, l'obligation ne change pas.

## Licence

Le code et la documentation sont publiés sous [licence MIT](LICENSE). Quant au lexique français, dérivé de Lexique 3.83 et de UD_French-GSD, il relève de la licence CC BY-SA 4.0 (voir [`NOTICE.md`](NOTICE.md)).
