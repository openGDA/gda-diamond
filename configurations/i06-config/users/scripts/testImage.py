from Diamond.Pilatus.ZipImageProducer import ZipImageProducerClass;
a=ZipImageProducerClass('/scratch/Dev/gdaDev/gda-config/i07/scripts/Diamond/Pilatus/images100K.zip', 'tif');


a.printList();
a.setFilePath("/scratch/temp")
a.setFilePrefix("p100k")

for i in range(5):
	print a.getNextImage();
