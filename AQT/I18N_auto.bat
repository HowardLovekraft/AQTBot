pybabel extract C:\GitHub\AQTBot\AQT\ -o locales/messages.pot
pybabel update -d locales -D messages -i locales/messages.pot
pause
pybabel compile -d locales -D messages