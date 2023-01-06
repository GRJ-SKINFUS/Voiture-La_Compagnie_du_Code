import vl53l5cx
import threading, numpy

class ToFReceiver(threading.Thread) :

    def __init__(self, tof,format):
        threading.Thread.__init__(self)
        self.format = format[0] ** 2
        self.tof = tof
        self.Continue = True
        self.data = None

        self.tof.set_resolution(format)
        self.tof.start_ranging()

        self.isChanged = True

    def run(self) :
        while self.Continue :
            if self.tof.data_ready() :
                self.data = self.tof.get_data()
                self.isChanged = True

    def stop(self):
        pass


class ToFManager :
    #TODO self.tof.set_powerr_mode
    #TODO comment recevoir donnees en parallele


    def __init__(self, resolution = (8,8), frequence = 15, sharpener = 5):
        DataTof.SetFormatData(resolution, self)

        self.resolution = resolution
        self.frequence = frequence
        self.sharpener = sharpener

        self.tof = vl53l5cx.vl53l5cx()
        self.receiver = ToFReceiver(self.tof, resolution)

        self.currentData = None

    def start(self):
        self.tof.set_ranging_frequency_hz(self.frequence)
        self.tof.set_sharpener_percent(self.sharpener)
        self.receiver.run()

    def stop(self, all=True):
        self.receiver.stop()
        if all :
            self.tof.stop_ranging()

    def UpdateData(self):
        if self.receiver.isChanged :
            self.currentData = DataTof(self.receiver.data)
            self.receiver.isChanged = False

class DataTof :
    format = 4
    formatTuple = (4, 4)
    formatSquared = 16

    @classmethod
    def SetFormatData(cls, format):
        cls.formatBase = format
        cls.formatTuple = (format,format)
        cls.formatSquared = format ** 2

    def __init__(self,dataBrute):
        self.distance = self.transformFormatTofToNumpy(dataBrute.distance_mm)
        self.reflectance = self.transformFormatTofToNumpy(dataBrute.reflectance)
        self.status = self.transformFormatTofToNumpy(dataBrute.target_status)
        self.noise = self.transformFormatTofToNumpy(dataBrute.range_sigma_mm)

    def transformFormatTofToNumpy(self, data):
        dataRes = numpy.array(data)
        dataRes = numpy.flipud(dataRes[0:DataTof.formatSquared].reshape(DataTof.formatTuple).astype('float64'))
        return dataRes


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mainTof = ToFManager((8, 8))
    mainTof.start()
    while True :
        print(mainTof.currentData)
        if input("Print new data? y/n") == "y" :
            mainTof.UpdateData()
        else:break
    mainTof.stop()
