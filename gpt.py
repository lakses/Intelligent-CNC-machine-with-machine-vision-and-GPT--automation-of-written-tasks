from gigachat import GigaChat
import os
# Используйте токен, полученный в личном кабинете из поля Авторизационные данные
with GigaChat(credentials="ZjliZjhlZjctOWU0Yy00ZjljLWFkYjktZjNmMTllOTgzYTA3OjU0OWJiMDBmLTQ5ZWQtNDE4ZC1hN2Y5LWMxOWRhN2Y3NGNiNA==", verify_ssl_certs=False) as giga:
    promt=""
    question = input()
    response = giga.chat(question)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "input.txt")
    input = open(input_file, 'w', encoding='utf-8')
    input.write(response.choices[0].message.content)