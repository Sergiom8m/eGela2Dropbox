import os
import sys
from tkinter import messagebox as tkMessageBox
import requests
import urllib

import self as self
from bs4 import BeautifulSoup
import time
import helper


class eGela:
    _login = 0
    _cookie = ""
    _subject = ""
    _refs = []
    _root = None
    _loginToken = ""
    _uriRequest = ""

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):
        global LOGIN_EGIAZTAPENA
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. ESKAERA (Login inprimakia lortu 'logintoken' ateratzeko #####")

        method = 'GET'
        self._uriRequest = 'https://egela.ehu.eus/login/index.php'
        headers = {'Host': 'egela.ehu.eus'}
        content = ''

        response = requests.request(method, self._uriRequest, headers=headers, data=content,
                            allow_redirects=False)

        html_file = response.content

        print("##### HTML-aren azterketa... #####")

        main_page = BeautifulSoup(html_file, 'html.parser')
        form = main_page.find_all('form', {'class': 'm-t-1 ehuloginform'})[0]
        self._loginToken = form.find_all('input', {'name': 'logintoken'})[0]['value']

        self._cookie = response.headers['Set-Cookie'].split(';')[0]

        if ('Location' in response.headers) is not False:
            self._uriRequest = response.headers['Location']

        try:
            self._cookie = response.headers['Set-Cookie'].split(";")[0]
        except Exception:
            print("Cookie-a mantentzen da")

        print("1.Eskaeraren metodoa eta URIa :", method, self._uriRequest)
        print("1.Eskaera: " + str(response.status_code) + " " + response.reason)

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 2. ESKAERA (Kautotzea -datu bidalketa-) #####")

        method = 'POST'
        headers = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie,
                   'Content-Type': 'application/x-www-form-urlencoded'}

        content = {'logintoken': self._loginToken,
                   'username': username.get(),
                   'password': password.get()}

        content_encoded = urllib.parse.urlencode(content)
        headers['Content-Length'] = str(len(content_encoded))

        response = requests.request(method, self._uriRequest, headers=headers, data=content,
                                    allow_redirects=False)

        if (response.headers['Location'].__eq__("https://egela.ehu.eus/login/index.php")):
            print('Login incorrect')
            sys.exit(1)
        else:
            print('Login successful')

        print("2.Eskaeraren metodoa eta URIa :", method, self._uriRequest)
        print("2.Eskaera: " + str(response.status_code) + " " + response.reason)

        if ('Location' in response.headers) is not False:
            self._uriRequest = response.headers['Location']

        try:
            self._cookie = response.headers['Set-Cookie'].split(";")[0]
        except Exception:
            print("Cookie-a mantentzen da")

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 3. ESKAERA (berbidalketa) #####")

        method = 'GET'
        headers = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
        content = ''

        response = requests.request(method, self._uriRequest, headers=headers, data=content,
                                    allow_redirects=False)

        print("3.Eskaeraren metodoa eta URIa :", method, self._uriRequest)
        print("3.Eskaera: " + str(response.status_code) + " " + response.reason)

        if ('Location' in response.headers) is not False:
            self._uriRequest = response.headers['Location']

        try:
            self._cookie = response.headers['Set-Cookie'].split(";")[0]
        except Exception:
            print("Cookie-a mantentzen da")


        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 4. ESKAERA (eGelako orrialde nagusia) #####")

        method = 'GET'
        headers = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
        content = ''

        response = requests.request(method, self._uriRequest, headers=headers, data=content,
                                    allow_redirects=False)

        print("4.Eskaeraren metodoa eta URIa :", method, self._uriRequest)
        print("4.Eskaera: " + str(response.status_code) + " " + response.reason)

        if ('Location' in response.headers) is not False:
            self._uriRequest = response.headers['Location']

        try:
            self._cookie = response.headers['Set-Cookie'].split(";")[0]
        except Exception:
            print("Cookie-a mantentzen da")

        if int(response.status_code) == 200:
            LOGIN_EGIAZTAPENA = True



        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)
        popup.destroy()

        print("\n##### LOGIN EGIAZTAPENA #####")
        if LOGIN_EGIAZTAPENA:
            self._login = 1
            print('Login successful')
            self._root.destroy()
        else:
            tkMessageBox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 5. ESKAERA (Ikasgairen eGelako orrialdea) #####")

        method = 'GET'
        headers = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
        content = ''

        response = requests.request(method, self._uriRequest, headers=headers, data=content,
                                    allow_redirects=False)

        html_file = response.content
        main_page = BeautifulSoup(html_file, 'html.parser')
        rows = main_page.find_all('div', {'class': 'info'})

        for idx, row in enumerate(rows):
            subject = row.h3.a.text
            if subject == 'Web Sistemak':
                self._subject = row.a['href']
                print(subject)
                print(self._subject)

        print("\n##### HTML-aren azterketa... #####")

        method = 'GET'
        headers = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
        content = ''

        response = requests.request(method, self._subject, headers=headers, data=content,
                                    allow_redirects=False)

        html_file = response.content
        subject_page = BeautifulSoup(html_file, 'html.parser')
        link_list = subject_page.find_all('img', {'class': 'iconlarge activityicon'})
        length = len(link_list)

        progress_step = float(100.0 / length)

        for link in link_list:
            if (link['src'].find("/pdf") != -1):

                self._uriRequest = link.parent['href']

                method = 'GET'
                headers = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
                content = ''

                response = requests.request(method, self._uriRequest, headers=headers, data=content,
                                            allow_redirects=False)

                html_file = response.content
                subject_page = BeautifulSoup(html_file, 'html.parser')
                pdf_list = subject_page.find_all('div', {'class': 'resourceworkaround'})

                for pdf in pdf_list:
                    pdf_file = pdf.find_all('a')[0]['href']
                    pdf_name = pdf_file.split('/')[-1]
                    self._refs.append({'pdf_link': pdf_file, 'pdf_name': pdf_name})

            progress += progress_step
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(0.1)

        # print(self._refs)
        popup.destroy()

        return self._refs

    def get_pdf(self, selection):
        print("##### PDF-a deskargatzen... #####")

        pdf_file = self._refs[selection]['pdf_link']
        pdf_name = self._refs[selection]['pdf_name']

        method = 'GET'
        headers = {'Host': pdf_file.split('/')[2], 'Cookie': self._cookiea}
        content = ''

        response = requests.request(method, pdf_file, headers=headers, data=content,
                                    allow_redirects=False)

        if not os.path.exists("pdf"):
            os.mkdir("pdf")

        file = open("./pdf/" + pdf_name, "wb")
        file.write(response.content)
        file.close()

        return pdf_name, pdf_file
