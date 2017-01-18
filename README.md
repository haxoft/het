# het
Haxoft Extraction Tool - Atlassian plugin

Running instructions:

1. manage.py runserver 8000 [in PyCharm you run manage.py with ctrl+alt+r]
2. ngrok.exe http 8000
3. Copy https ngrok url to:
    a) hetaddon/static/addon/atlassian-connect.json
    b) HET/settings.py -> ALLOWED_HOSTS = ['ngrok_URL']
4. install addon @Atlassian [https://haxoft.atlassian.net/plugins/servlet/upm]
5. refresh the atlassian page and click on "HET" on the main menu
