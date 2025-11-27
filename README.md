# Keylogger

Créer deux VMs une vm attaquante et une vm victime. 
Mettez les deux VMs en mode hostonly et nat. 

Sur la vm attaquante :

créer un dosser Keylogger.
Dans ce dossier créer deux fichier server.py et panel.py.
Implémenter le code correspondant
Puis créer un dossier victime c'est là que seront stocké les fichiers des logs

Sur la vm victime : 

créer un dossier victime
créer un fichier keylogger.py
implémenter le code

Pour lancer le server streamlit, rentrer la commande suivante : 
streamlit run panel.py

Pour lancer le serveur, rentrer la commande suivante :
python3 serveur.py

Pour lancer le code malveillant sur keylogger, rentrer la commande suivante : 
python3 keylogger.py

Rentrer ensuite sur une page web hhtp://ip_attaquant
