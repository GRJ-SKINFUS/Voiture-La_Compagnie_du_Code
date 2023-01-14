#!/usr/bin/env python3
#-- coding: utf-8 --
import RPi.GPIO as GPIO
import time

class Servo :
    """
    Classe permettant de controller un servo-moteur sur un raspberry pi.
        Permet aussi de controller un moteur brushless.

    Utilisation :
    1- Initialiser la classe avec les bons paramètres
        fonction : __init__

    2- Dire au servo de se positionner entre son angle minimum (O% -> 0) et son maximum (100% -> 100)
        fonction : goAngle( angle -> angle desire)
    3- Quand on veut desactiver le servo, le stopper
        fonction : stop()

    NDT : 
    Si cette classe est utilise a la fin de l'execution de votre execution appelez :
        GPIO.cleanup() 

    Si cette classe est utilise pour controller un servo-moteur :
        Les valeurs conseilles sont : minPulse=0.5, maxPulse=2.5
    Si cette classe est utilise pour controller un moteur brushless :
        Les valeurs conseilles sont : minPulse=1, maxPulse=2    

    Remerciement a Raspberry Pi FR pour son tres bon tutoriel dont est inspire cettte classe :
        Voir : https://raspberry-pi.fr/servomoteur-raspberry-pi/
    """

    def __init__(self,pin ,frequence=50,minPulse=0.5, maxPulse=2.5) :
        """
        Fonction pour initialiser le servo-moteur

        Parametres :
            pin : pin du raspberry pi qui commande le servo - un numero
            frequence : frequence à laquelle est actualise le servo - en hertz
            minPulse : duree minimale ou le pwm est a l'etat haut - en milisecondes
            maxPulse : duree maximale ou le pwm est a l'etat haut - en milisecondes
        """
        self.frequence = frequence # frequence à laquelle est actualise le servo - en hertz

        nbMsParFrame = 1000 / frequence # nombre de temps qu'il s'ecoule entre chaque periode -> en milisecondes

         # rapport de :
         #      la duree du signal a l'etat haut pour la valeur minimum et maximum
         # par rapport a :
         #      temps du signal en entier
         #-> retourne entre 0 et 1
        self.minDutyCycle = minPulse/nbMsParFrame
        self.maxDutyCycle = maxPulse/nbMsParFrame

        #On les ramene entre 0 et 100 (en pourcentages)
        self.minDutyCycle *= 100
        self.maxDutyCycle *= 100 

        #etendue entre le pourcentage maximum et minimum (pourcentage -> entre 0 et 100)
        self.ratio = (self.maxDutyCycle - self.minDutyCycle)

        self.ratio /= 100 #on le ramene entre 0 et 1

        self.pinNumber = pin # numero du pin

        # on initiallise le pin utilise
        GPIO.setup(pin, GPIO.OUT) # on le declare en sortie
        self.pin = GPIO.PWM(pin, frequence) # on cree une instance de la classe PWM (de la librairie RPi.GPIO) pour le controller

    def goAngle(self, angle) :
        """
        Fonction permettant de positionner a un angle

        Parametre :
            angle : pourcentage (entre 0 et 100)
                0 -> angle minimum du servo-moteur
                100 -> angle maximum du servo-moteur
        """

        # verifie que l'utilisateur a rentre un chiffre dans le bon interval
        if angle > 100 :
            angle = 100
        elif angle < 0 :
            angle = 0

        # angle devient le pourcentage que la pin doit etre a l'etat haut (entre 0 et 100)
        #   Si angle vaut 0 : le servo-moteur va a son angle minimum
        #   Si angle vaut 100 : le servo-moteur va a son angle maximum
        angle = angle*self.ratio + self.minDutyCycle 

        #On ordonne enfin a la pin d'envoyer au servo le bon pourcentage
        self.pin.ChangeDutyCycle(angle)

    def stop(self) :
        """
        Fonction pour stopper le servo proprement
        """

        self.pin.stop() # ordonne au pin de n'etre plus une sortie PWM, il devient libre a etre utilise pour autre chose