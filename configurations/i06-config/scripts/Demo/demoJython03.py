#start with a comment

if __name__ == "__main__":
    print "Hello Pydev World";
else:
    print "Invoked as module: " + __name__;


print"-------------------------------\n";

from java.util import Random;
r = Random();
print r.nextInt();

import javax.swing as swing
import java.lang as lang
import java.awt as awt
import java.applet.Applet 

names = ["Groucho", "Chico", "Harpo"];
quotes = {"Groucho": "Say the secret word", "Chico": "Viaduct?", "Harpo": "HONK!"};


def buttonPressed(event):
    field.text = quotes[event.source.text];

def exit(event):
    lang.System.exit(0);

def createButton(name):
    return swing.JButton(name, preferredSize=(100, 20), actionPerformed=buttonPressed);


win=swing.JFrame("Welcome to Jython", size=(200, 200), windowClosing=exit);
print win

win.contentPane.layout = awt.FlowLayout();

field = swing.JTextField(preferredSize=(200,20));
win.contentPane.add(field);

buttons = [createButton(each) for each in names]
for eachButton in buttons:
    win.contentPane.add(eachButton);
 
win.pack();
#win.show();
win.setVisible(java.lang.Boolean.TRUE)
    