/*
 -----------------------------------------------------------------------------------
 Laboratoire : 02
 Fichier     : main.cpp
 Auteur(s)   : Robel Teklehaimanot, Erwan Moreira, Marion Dutu Launay
 Date        : 27.03.2018

 But         : Mettre en oeuvre le jeu du cube magique de manière récursive

 Compilateur : MinGW-g++ 5.3.0
 -----------------------------------------------------------------------------------
 */

#include <iostream>
#include <vector>
#include <fstream>

using namespace std;

const unsigned X = 0;
const unsigned Y = 1;
const unsigned Z = 2;
const size_t LONGUEUR_CUBE = 3; // x
const size_t HAUTEUR_CUBE = 3; // y
const size_t LARGEUR_CUBE = 3; // z
const size_t TAILLE_CUBE = (LONGUEUR_CUBE * HAUTEUR_CUBE * LARGEUR_CUBE);

//Toutes les pièces du cube
//enum class idPieces {L1 = 1, L2, L3, L4, Z, COIN, T}; //ordre labo ASD1
enum class idPieces {COIN = 1, T, Z, L1, L2, L3, L4}; //ordre Rémi

//On a défini plusieurs using sur les mêmes types, car même si niveau implémentation
//il s'agit du même type, conceptuellement il s'agit d'autre chose,
//et ça aide donc à la compréhension du code
using Ligne = vector<unsigned>; //Ligne de 3 valeurs binaires
using Fragment = vector<unsigned>; //Une coordonnée (x,y,z)
using Face = vector<Ligne>; //Une face du cube
using Orientation = vector<Fragment>; //L'orientation d'une pièce
using Piece = vector<Orientation>; //Toutes les orientations d'une pièce
using ListePieces = vector<Piece>; //Liste des pièces servant à former le cube
using Cube = vector<Face>;
using Positions = vector<Cube>; //Toutes les positions d'une pièce
using Solutions = vector<Cube>; //Toutes les solutions du cube
using Alphabet = vector<Positions>; //Toute les positions de toutes les pièces


//Liste des orientations de toutes les pièces.
//L'origine est située dans le coin supérieur gauche de la face avant du cube.
//La pièce est toujours positionnée en bas à gauche de la face avant du cube.
Piece ortCoin = {
        {{0,2,0},{1,1,0},{0,1,0}},
        {{0,2,0},{1,2,0},{0,1,0}},
        {{0,2,0},{1,2,0},{1,1,0}},
        {{0,1,0},{1,1,0},{1,2,0}},
        {{0,2,0},{1,2,0},{0,2,1}},
        {{0,2,0},{0,2,1},{1,2,1}},
        {{0,2,1},{1,2,1},{1,2,0}},
        {{0,2,0},{1,2,0},{1,2,1}},
        {{0,2,1},{0,1,1},{0,1,0}},
        {{0,2,0},{0,1,0},{0,1,1}},
        {{0,2,0},{0,2,1},{0,1,1}},
        {{0,2,1},{0,2,0},{0,1,0}}

};

Piece ortL = {
        {{0,0,0},{0,1,0},{0,2,0},{1,2,0}},
        {{0,0,0},{0,1,0},{0,2,0},{0,2,1}},
        {{1,0,0},{1,1,0},{1,2,0},{0,2,0}},
        {{0,0,1},{0,1,1},{0,2,1},{0,2,0}},
        {{0,2,0},{1,2,0},{2,2,0},{2,1,0}},
        {{0,2,0},{0,2,1},{0,2,2},{0,1,2}},
        {{0,1,0},{0,2,0},{1,2,0},{2,2,0}},
        {{0,1,0},{0,2,0},{0,2,1},{0,2,2}},
        {{0,0,0},{1,0,0},{1,2,0},{1,2,0}},
        {{0,0,0},{0,0,1},{0,1,1},{0,2,1}},
        {{0,0,0},{1,0,0},{0,1,0},{0,2,0}},
        {{0,0,0},{0,0,1},{0,1,0},{0,2,0}},
        {{0,1,0},{1,1,0},{2,1,0},{0,2,0}},
        {{0,1,0},{0,1,1},{0,1,2},{0,2,0}},
        {{0,1,0},{1,1,0},{2,1,0},{2,2,0}},
        {{0,1,0},{0,1,1},{0,1,2},{0,2,2}},
        {{0,2,0},{0,2,1},{0,2,2},{1,2,0}},
        {{0,2,0},{1,2,0},{2,2,0},{2,2,1}},
        {{1,2,0},{1,2,1},{1,2,2},{0,2,2}},
        {{0,2,0},{0,2,1},{1,2,1},{2,2,1}},
        {{0,2,0},{1,2,0},{1,2,1},{1,2,2}},
        {{0,2,1},{1,2,1},{2,2,1},{2,2,0}},
        {{0,2,0},{0,2,1},{0,2,2},{1,2,2}},
        {{0,2,1},{0,2,0},{1,2,0},{2,2,0}}
};

Piece ortZ = {
        {{0,1,0},{1,1,0},{1,2,0},{2,2,0}},
        {{0,1,0},{0,1,1},{0,2,1},{0,2,2}},
        {{0,2,0},{1,2,0},{1,1,0},{2,1,0}},
        {{0,2,0},{0,2,1},{0,1,1},{0,1,2}},
        {{0,2,0},{0,1,0},{1,1,0},{1,0,0}},
        {{0,2,0},{0,1,0},{0,1,1},{0,0,1}},
        {{0,0,0},{0,1,0},{1,1,0},{1,2,0}},
        {{0,0,0},{0,1,0},{0,1,1},{0,2,1}},
        {{0,2,1},{1,2,1},{1,2,0},{2,2,0}},
        {{0,2,0},{0,2,1},{1,2,1},{1,2,2}},
        {{0,2,0},{1,2,0},{1,2,1},{2,2,1}},
        {{0,2,2},{0,2,1},{1,2,1},{1,2,0}}
};

Piece ortT = {
        {{0,2,0},{1,2,0},{1,1,0},{2,2,0}},
        {{0,1,0},{1,1,0},{1,0,0},{1,2,0}},
        {{0,1,0},{1,1,0},{1,2,0},{2,1,0}},
        {{0,2,0},{0,1,0},{0,0,0},{1,1,0}},
        {{0,2,1},{1,2,1},{2,2,1},{1,2,0}},
        {{0,2,1},{1,2,1},{1,2,2},{1,2,0}},
        {{0,2,0},{1,2,0},{1,2,1},{2,2,0}},
        {{0,2,0},{0,2,1},{0,2,2},{1,2,1}},
        {{0,2,0},{0,1,0},{0,0,0},{0,1,1}},
        {{0,2,1},{0,1,1},{0,1,0},{0,0,1}},
        {{0,1,0},{0,1,1},{0,2,1},{0,1,2}},
        {{0,2,0},{0,1,1},{0,2,1},{0,2,2}},
};

//Construit un cube dont tous les fragments sont à zéro
Cube initCube() {
    Ligne ligneVide = {0, 0, 0};
    Face face = {ligneVide, ligneVide, ligneVide};
    Cube cube = {face, face, face};

    return cube;
}

//Convertit une pièce, à l'origine en coordonnées, dans une représentation binaire.
//La pièce est placée dans un cube où elle est le seul élément présent.
Cube coordToBinary(const Orientation& piece, idPieces id) {
    Cube pieceBinaire = initCube();
    unsigned x, y, z;

    //On récupère les coordonnées du fragment
    for (size_t fragment = 0; fragment < piece.size(); ++fragment) {
        x = piece.at(fragment).at(X);
        y = piece.at(fragment).at(Y);
        z = piece.at(fragment).at(Z);
        //Dans notre système de coordonnées, z correspond à la face.
        //Dans notre manière de coder le cube, on accède en pRémier à la face, puis
        //la ligne, puis la case. C'est pourquoi on inverse x et z.
        pieceBinaire.at(z).at(y).at(x) = (unsigned) id;
    }

    return pieceBinaire;
}

//Détermine le fragment directeur pour un axe donnée, et renvoie sa coordonnée
//x, y, ou z en fonction de l'axe.
//Un fragment directeur pour un axe est le fragment le plus loin sur cet axe
//pour une pièce dans une position donnée
int coordFragmentDirecteur(const Orientation& piece, unsigned axe) {
    unsigned coordMax = piece.at(0).at(axe), coordTemp;
    //On compare tout simplement la coordonnée x, y ou z de tous les fragments.
    //Il peut y avoir plusieurs fragments pouvant être directeurs, on choisit
    //de garder le pRémier trouvé
    for (size_t fragNbr = 1; fragNbr < piece.size(); ++fragNbr) {
        coordTemp = piece.at(fragNbr).at(axe);
        //Si l'axe est Y, la coordonnée la plus haute est 0, et la plus basse 2
        //car l'origine est en haut à gauche du cube et l'axe y descend
        if((axe == Y && coordTemp < coordMax) || (axe != Y && coordTemp > coordMax)) {
            coordMax = coordTemp;
        }
    }

    return coordMax;
}

//Déplace une pièce de deltaCoord sur un axe
void deplacerPiece(Orientation& piece, const unsigned axe, int deltaCoord) {
    if(deltaCoord) {
        for (size_t fragNbr = 0; fragNbr < piece.size(); ++fragNbr) {
            piece.at(fragNbr).at(axe) += deltaCoord;
        }
    }
}

//Calcule toutes les positions de chaque orientation d'une pièce donnée.
//Piece n'est pas const car on va déplacer ses orientations, même si on les
//remet dans leur état initial à la fin
Positions positions(Piece& piece, idPieces id) {
    Cube position;
    Positions posPiece;

    for(size_t ortNbr = 0; ortNbr < piece.size(); ++ortNbr) {
        //Pour déplacer une pièce on se base sur les faits suivants :
        //1. Pour un axe donné, le déplacement de la pièce est limité par son
        //   fragment le plus loin sur cet axe, puisque ce sera le pRémier à
        //   sortir du cube. On travaille donc sur ce fragment.
        //2. Tous les fragments doivent se déplacer en même temps. Ils suivent
        //   donc les mouvements du fragement décrit en 1.
        //3. La pièce est passée par référence, il faut donc annuler le déplacement
        //   une fois que tout un axe a été testé pour pouvoir revenir à la position
        //   originale et continuer les tests.
        Orientation& orientation = piece.at(ortNbr);

        //On ajoute l'orientation de base, avant le pRémier déplacement
        position = coordToBinary(orientation, id);
        posPiece.push_back(position);

        //On récupère les coordonnées des fragments directeurs pour chacun des axes
        int fragDirXinit = coordFragmentDirecteur(orientation, X),
            fragDirYinit = coordFragmentDirecteur(orientation, Y),
            fragDirZinit = coordFragmentDirecteur(orientation, Z);

        //On parcours les axes dans cet ordre : tous les z, puis tous les y,
        //puis tous les x
        for (int x = fragDirXinit; x < LONGUEUR_CUBE; ++x) {
            //Y se décrémente car son axe descend depuis en haut à gauche du
            //du cube, monter sur y veut donc dire décrémenter y
            for (int y = fragDirYinit; y >= 0; --y) {
                for (int z = fragDirZinit; z < LARGEUR_CUBE - 1; ++z) {
                    //Les pièces se déplacent toujours d'une case à la fois
                    deplacerPiece(orientation, Z, 1);
                    position = coordToBinary(orientation, id);
                    posPiece.push_back(position);
                }

                //On replace la pièce dans sa profondeur z de base avant
                //de la monter d'un cran sur y
                deplacerPiece(orientation, Z, -(int)((LARGEUR_CUBE - 1) - fragDirZinit));

                if(y != 0) {
                    deplacerPiece(orientation, Y, -1);
                    position = coordToBinary(orientation, id);
                    posPiece.push_back(position);
                }
            }

            //On replace la pièce à sa hauteur y de base avant de continuer à
            //l'avancer d'un cran sur x
            deplacerPiece(orientation, Y, fragDirYinit);

            //On se déplace enfin d'un cran sur x
            if(x != LONGUEUR_CUBE - 1) {
                deplacerPiece(orientation, X, 1);
                position = coordToBinary(orientation, id);
                posPiece.push_back(position);
            }
        }

        //On replace la pièce dans sa position d'origine
        deplacerPiece(orientation, X, -(int)((LONGUEUR_CUBE - 1) - fragDirXinit));
    }

    return posPiece;
}

//Affiche une face du cube
void afficherFace(const Face& face) {
    for (size_t ligne = 0; ligne < HAUTEUR_CUBE; ++ligne) {
        for (size_t colonne = 0; colonne < LONGUEUR_CUBE; ++colonne) {
            cout << face.at(ligne).at(colonne);
        }
        cout << endl;
    }
    cout << endl;
}

//Affiche toutes les faces d'un cube
void afficherCube(const Cube& cube) {
    for (size_t face = 0; face < LARGEUR_CUBE; ++face) {
        afficherFace(cube.at(face));
    }
}

//Affiche toutes les orientations d'une pièce
void afficherPiece(const Piece& piece, idPieces id) {
    unsigned ortNbr = 1;
    Cube ortCube;

    for (const Orientation& orientation : piece) {
        //On place cette orientation dans un cube en binaire
        ortCube = coordToBinary(orientation, id);

        //On affiche l'orientation
        cout << "Orientation " << ortNbr++ << " : " <<  endl;
        afficherCube(ortCube);
        cout << endl;
    }
}

//Affiche toutes les positions possibles d'une pièce dans un cube
void afficherPositions(const Positions& positions, idPieces id) {
    unsigned posNbr = 1;

    for (const Cube& position : positions) {
        cout << "Position " << posNbr++ << " : " << endl;
        afficherCube(position);
        cout << endl;
    }

    cout << endl;
}

//Insère, si possible, une pièce dans un cube en cours de construction.
//Une pièce s'insère dans un cube si, pour chacun de ses fragments portant
//son id, le fragment correspondant dans le cube de destination est vide
bool insererPiece(Cube& bebeCube, const Cube& piece) {
    //Il faut d'abord vérifier qu'on peut insérer la pièce
    for (size_t z = 0; z < LARGEUR_CUBE; ++z) {
        for (size_t y = 0; y < HAUTEUR_CUBE; ++y) {
            for(size_t x = 0; x < LONGUEUR_CUBE; ++x) {
                //On cherche dans le cube de la pièce où se trouvent ses
                //fragments, et on les compare à ceux du cube
                if(piece.at(z).at(y).at(x) && bebeCube.at(z).at(y).at(x)) {
                    return false;
                }
            }
        }
    }

    //On peut insérer la pièce dans le cube
    for (size_t z = 0; z < LARGEUR_CUBE; ++z) {
        for (size_t y = 0; y < HAUTEUR_CUBE; ++y) {
            for(size_t x = 0; x < LONGUEUR_CUBE; ++x) {
                if (piece.at(z).at(y).at(x)) {
                    bebeCube.at(z).at(y).at(x) = piece.at(z).at(y).at(x);
                }
            }
        }
    }

    return true;
}

//Enlève ue pièce du cube en cours de construction.
//Pour se faire, pour chacun des fragments du cube de la pièce portant son id,
//on place un 0 dans le fragment correspondant du cube en construction
void enleverPiece(Cube& bebeCube, const Cube& piece) {
    for (size_t z = 0; z < LARGEUR_CUBE; ++z) {
        for (size_t y = 0; y < HAUTEUR_CUBE; ++y) {
            for(size_t x = 0; x < LONGUEUR_CUBE; ++x) {
                if (piece.at(z).at(y).at(x)) {
                    bebeCube.at(z).at(y).at(x) = 0;
                }
            }
        }
    }
}

//Teste si le cube en construction est rempli, c'est-à-dire qu'aucun de ses
//fragment n'est à 0
bool estRempli(const Cube& cube) {
    for (size_t z = 0; z < LARGEUR_CUBE; ++z) {
        for (size_t y = 0; y < HAUTEUR_CUBE; ++y) {
            for(size_t x = 0; x < LONGUEUR_CUBE; ++x) {
                if (!cube.at(z).at(y).at(x)) {
                    return false;
                }
            }
        }
    }

    return true;
}

//Fonction récursive calculant toutes les permutations des pièces, et
//construisant les différentes solutions du cube.
//Insère toujours les pièces dans le même ordre.
//Pour chaque pièce, tente d'insérer une positions de la pièce, si elle y arrive,
//et que le cube n'est pas rempli, elle passe à la pièce suivante, tant qu'il y
//en a.
//Il est conseillé de lancer le programme en release mode (3 - 4 minutes d'exécution)
//et non en mode debug (~1h d'exécution)
void permutations(const Alphabet& alphabet, size_t debutAlphabet, size_t finAlphabet, Cube& bebeCube, Solutions& solutions) {
    //Tant qu'on a encore une pièce à traiter
    if(debutAlphabet <= finAlphabet) {
        size_t nbrPosPiece = alphabet.at(debutAlphabet).size();
        //On parcours les positions de la pièce
        for (size_t posPiece = 0; posPiece < nbrPosPiece; ++posPiece) {
            const Cube& piece = alphabet.at(debutAlphabet).at(posPiece);

            //On tente d'insérer la pièce
            if (insererPiece(bebeCube, piece)) {
                if (estRempli(bebeCube)) {
                    //On a une solution quand le cube est rempli
                    solutions.push_back(bebeCube);

                    //On enlève la pièce fraîchement ajoutée pour ne pas perturber
                    //le reste de la récursion
                    enleverPiece(bebeCube, piece);

                    //On a plus besoin de tester les autres positions de la
                    //dernière pièce
                    break;
                }
                else {
                    //Le cube n'est pas rempli, on peut donc tenter d'ajouter
                    //la pièce suivante
                    permutations(alphabet, debutAlphabet + 1, finAlphabet, bebeCube, solutions);
                    enleverPiece(bebeCube, piece);
                }
            }
        }
    }
}

//Crée l'alphabet, qui contient toutes les positions de toutes les pièces.
//listePieces sera temporairement modifiée pour calculer les positions de toutes
//les pièces.
Alphabet creerAlphabet(ListePieces& listePieces) {
    Alphabet alphabet;

    //piece + 1 donne le bon id à la bonne pièce (selon l'enum), seulement
    //si les pièces sont placées dans le même ordre dans l'enum et dans la liste.
    for (size_t piece = 0; piece < listePieces.size(); ++piece) {
        alphabet.push_back(positions(listePieces.at(piece), (idPieces) (piece + 1)));
    }

    return alphabet;
}

//Permet d'écrire les solutions dans un fichier dont le nom est passé en paramètre
void writeToFile(const Solutions& solutions, const char* filename) {
    ofstream file;
    file.open(filename);

    if (file.is_open()) {
        for (const Cube& cubes : solutions) { // On explore toutes les solutions
            // Pour chaque solution, on l'écrit de la façon suivante:
            //Cet exemple comporte 5 L et pas de T
            /*
                      3 2 2
                      2 2 5 | face 1
                      5 5 5

                      3 0 4
                      3 0 4 | face 2
                      3 0 1

                      6 0 4
                      6 6 6 | face 3
                      1 1 1
            */

            for (const Face& face : cubes){
                for (const Ligne& ligne : face) {
                    for (const unsigned& valeur : ligne) {
                        file << valeur << " ";
                    }
                    file << endl;
                }
                file << endl; // Chaque face est séparée par 1 ligne vide
            }
            file << endl; // Chaque solution est séparée par deux lignes vides (ligne vide face + ligne vide solution)
        }

        // On libère le fichier
        file.close();
    }
}

//Diminue tous les indices des solutions de 1 pour correspondre aux indices de Remi
//On ne pouvait pas le faire avant, car dans nos tests l'indice 0 a le sens de
//"pas d'indice"
void diminuerIndice(Solutions& solutions) {
    for(Cube& solution : solutions) {
        for(Face& face : solution) {
            for(Ligne& ligne : face) {
                for(unsigned& valeur : ligne) {
                    --valeur;
                }
            }
        }
    }
}

//L'ordre des pièces a été adapté pour la version de Rémi, les modifications ont
//été apportées aux endroits suivants :
//1. l'enum de pièces tout en haut du fichier
//2. la liste de pièces dans le main
//3. ajout des fonctions writeToFile et diminuerIndice
//
//Indices pour le labo ASD1 : 1 2 3 4 5 6    7
//                            L L L L Z COIN T
//Indices pour Rémi :         3 4 5 6 2 0    1
int main() {
    //Ordre labo ASD1
    //ListePieces listePieces = {ortL, ortL, ortL, ortL, ortZ, ortCoin, ortT};

    //Ordre pour Rémi
    ListePieces listePieces = {ortCoin, ortT, ortZ, ortL, ortL, ortL, ortL};
    Alphabet alphabet = creerAlphabet(listePieces);
    Cube bebeCube = initCube();
    Solutions solutions;

    cout << "Calcul en cours... (env. 5 min)" << endl;
    permutations(alphabet, 0, alphabet.size() - 1, bebeCube, solutions);
    cout << solutions.size() << " solutions au total." << endl;

    //Ecriture des solutions dans le fichier. Pas besoin de le créer à l'avance
    diminuerIndice(solutions);
    cout << "Ecriture dans le fichier (< 1 min)" << endl;
    writeToFile(solutions, "solutions.txt");


    return 0;
}