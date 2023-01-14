import vl53l5cx
import threading, numpy

class ToFReceiver(threading.Thread) :
    """
    Classe permettant de recevoir les données du capteur vl53l5cx en parallele pour ameliorer la performance.

    Elle n'est pas cense etre utilise par les utilisateurs directement mais par la classe ToFManager.

    NDT : 
        Cette classe herite de threading.Thread; 
        Elle cree donc un nouveau thread pour chaque cpateur associe et s'execute en parallele du programme principal.

    Possibilite d'optimisations pour multi-capteurs mais n'etant pas, pour l'instant, utile pour ce projet.
    """
    def __init__(self, tof,format):
        """
        Fonction initialisant la classe

        Parametres :
            tof : une instance de la classe vl53l5cx.vl53l5cx permettant de récupérer les donnees du capteur
            format : format du nombre sous-capteurs utilise : (8,8) ou (4,4) uniquement supporte
        """
        threading.Thread.__init__(self) # On initialise la classe herite, en l'occurence pour permettre la parallelesition  
        self.format = format[0] ** 2 # Nombre de sous-capteurs utilise, 64 ou 16 uniquement
        self.tof = tof # instance de la classe vl53l5cx.vl53l5cx
        self.data = None # variable qui va contenir les donnees du capteur

        self.tof.set_resolution(format) # initialisation du capteur en fonction du nombre de sous capteur utilise
        self.tof.start_ranging() # on demarre le capteur

        # isChanged vaut True si de nouvelles donnees sont arrivees
        #   Sinon elle vaut False
        self.isChanged = True 

    def run(self) :
        """
        Fonction appele pour recuperer les donnees 

        NDT : 
            Tout ce qui est dans cette fonction s'execute en parallele
        """
        while True :# Boucle infinie, peut etre stoppee si la fonction stop() est appelee
            if self.tof.data_ready() :# Si le capteur a envoye de nouvelles donnees
                self.data = self.tof.get_data() # On stocke les donnees qui sont arrivees
                self.isChanged = True # On indique que les donnees sont arrivees

    def stop(self):#Permet de stopper la fonction run()
        pass


class ToFManager :
    """
    Classe gerant le capteur vl53l5cx et ses differentes fonctionnalites pour un Raspberry Pi.
    Elle permet de faciliter la tache de l'utilisateur.

    NDT :
        Encore beaucoup de parametres a implementer
        Et possibles bugs
        Version beta
    """
    def __init__(self, resolution = (8,8), frequence = 15, sharpener = 5):
        """
        Fonction d'initialisation de la classe.

        Parametres : 
            resolution : format du nombre sous-capteurs utilise : (8,8) ou (4,4) uniquement supporte
            frequence : nombre de fois par secondes que le capteur va envoyer des donnees
            sharpener : effectue un "zoom" pour eviter les parasites liees aux donnees du bord, en pourcentage (entre 0 et 100)

        NDT :
            Pour une resolution de (4,4) la frequence maximale est de 60
            Pour une resolution de (8,8) la frequence maximale est de 15
        """
        DataTof.SetFormatData(resolution, self) # Initialisation de la classe permettant de gerer les donnees

        # voir description des parametres de la classe
        self.resolution = resolution 
        self.frequence = frequence
        self.sharpener = sharpener

        self.tof = vl53l5cx.vl53l5cx()# initialisation de la classe permettant de gerer le capteur (plus bas niveau)
        self.receiver = ToFReceiver(self.tof, resolution)# initialisation de la classe permettant de recevoir les donnees du capteur

        self.currentData = None # donnees actuelles recues

    def start(self):
        """
        Fonction pour initialiser la capteur et le demarer

        NDT : Peut etre utilise plusieurs fois pour utiliser des parametres differents
            Exemple :
            <<Initialisation de la classe>>
            start()
            ...
            stop(all = False)
            <<On change les parametres>>
            start()
            ...
            stop(all = True)
            <<Fin du programme>>

            Seule la resolution ne peut pas etre change avec cette methode
        """
        self.tof.set_ranging_frequency_hz(self.frequence) # On initialise la frequence du capteur
        self.tof.set_sharpener_percent(self.sharpener) # On initialise le "zoom" virtuel du capteur
        self.receiver.run() # On demarre le receveur, voir la classeToFReceiver pour plus de details

    def stop(self, all=True):
        """
        Fonction pour stopper le capteur.

        Si all = True :
            Le capteur s'arrete totalement 
        Sinon si all = False :
            Le receveur se met en pause et peut etre redemarer par start()

        NDT :
            A la fin de votre programme utilisez all = True, sinon all = False             
        """
        self.receiver.stop() # Le capteur se met en pause
        if all : # Si on veut totalement arreter le capteur
            self.tof.stop_ranging() 

    def UpdateData(self):
        if self.receiver.isChanged : # Si on a de nouvelles donnees disponibles
            self.currentData = DataTof(self.receiver.data) # on les recupere
            self.receiver.isChanged = False # et on indique que l'on a lu ces donnees

class DataTof :
    """
    Classe permettant d'avoir des donnees sous le format desire
    """
    format = 4 # Nombre de sous capteurs par ligne
    formatTuple = (4, 4) # Nombre de sous capteurs par ligne et par colonnes
    formatSquared = 16 # Nombre total de sous capteurs

    @classmethod
    def SetFormatData(cls, format):
        """
        Fonction initialisant le format des donnees
        """
        cls.formatBase = format
        cls.formatTuple = (format,format)
        cls.formatSquared = format ** 2

    def __init__(self,dataBrute):
        """
        Fonction initialisant un nouvel objet de donnees
        """
        #Toutes ces donnes sont des tbleaux numpy de forme formatTuple
        self.distance = self.transformFormatTofToNumpy(dataBrute.distance_mm) # indique la distance en mm
        self.reflectance = self.transformFormatTofToNumpy(dataBrute.reflectance) # indique la quantite de lumiere renvoyee
        self.status = self.transformFormatTofToNumpy(dataBrute.target_status) # indique des informations sur les donnes, voir documentations
        self.noise = self.transformFormatTofToNumpy(dataBrute.range_sigma_mm) # indique le bruit estime des mesures en chaque point

    def transformFormatTofToNumpy(data):
        """
        Fonction permettant de transformer les donnees en tableaux numpy.
        """
        dataRes = numpy.array(data)
        dataRes = numpy.flipud(dataRes[0:DataTof.formatSquared].reshape(DataTof.formatTuple).astype('float64'))
        return dataRes
"""
class showData :
    def __init__(self,x_range,y_range):
        x_vals = numpy.linspace(0, x_range, x_range)
        y_vals = numpy.linspace(0, y_range, y_range)
        self.xAxis, self.yAxis = numpy.meshgrid(x_vals, y_vals)

        plt.ion()

        self.figure  = plt.figure(figsize=(x_range,y_range))
        left, bottom, width, height = 0.1, 0.1, 0.8, 0.8
        self.ax = self.figure.add_axes([left, bottom, width, height])

    def Update(self, data):


        cp = plt.contour(self.xAxis, self.yAxis, data, levels=40)
        plt.colorbar(cp)

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

"""
if __name__ == '__main__':
    mainTof = ToFManager((8, 8))
    mainTof.start()

    while True :
        print(mainTof.currentData)
        if input("Print new data? y/n") == "y" :
            mainTof.UpdateData()
        else:break
    mainTof.stop()