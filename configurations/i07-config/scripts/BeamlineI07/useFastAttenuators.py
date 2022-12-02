from gdaserver import fatt

add_default(fatt)

def att(attenuation=None):
    if attenuation != None:
        pos(fatt, attenuation)
    else :
        pos(fatt)


alias(att)