# HET
Haxoft Extraction Tool - Atlassian plugin

Running instructions:

1. ngrok.exe http 8000  
2. Copy https ngrok url to:  
    a) hetaddon/static/addon/atlassian-connect.json  
    b) HET/settings.py -> ALLOWED_HOSTS = [ {ngrok_URL} ]  
3. manage.py runserver 8000 [in PyCharm you run manage.py with ctrl+alt+r]  
4. install addon @Atlassian  
	The URL to install addons: https://haxoftaddon.atlassian.net/plugins/servlet/upm
	Important: The backend is serving the atlassian descriptor on: {ngrok_URL}/static/addon/atlassian-connect.json  
5. refresh the atlassian page and click on "HET" on the main menu  