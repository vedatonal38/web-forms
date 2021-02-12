import sys
import webbrowser
import requests as req
from bs4 import BeautifulSoup as bs
from requests_html import HTMLSession
from urllib.parse import urljoin
from pprint import pprint

# English : How to Extract and Submit Web Forms from a URL using Python
# Türkçe : Python kullanarak bir URL'den Web Formlarını Çıkarma ve Gönderme
# kurulum : pip install requests_html
#           pip install requests
#           pip install bs4

class Form:
    def __init__(self, url):
        self.session = HTMLSession()
        self.url = url

    def get_all_forms(self):
        """
        English:
            Returns all form tags found on a web page's `url`
        Türkçe:
            Bir web sayfasının "url" sinde bulunan tüm form etiketlerini döndürür
        """

        # GET request
        response = self.session.get(self.url)
        # for javascript driven website / javascript tabanlı web siteleri için
        # res.html.render()
        # for html driven website / html tabanlı web siteleri için
        # res.html.html
        soup = bs(response.html.html, "html.parser")
        return soup.find_all("form")
    
    def get_form_details(self, form):
        """
        English:
            Returns the HTML details of a form, including action, 
            method and list of form controls (inputs, etc)
        Türkçe:
            Eylem, yöntem ve form denetimlerinin listesi (girdiler, 
            vb.) Dahil olmak üzere bir formun HTML ayrıntılarını verir
        """
        details = {} # detaylar
        # get the form action (target url) / form eylemini al (hedef url)
        try: 
            action = form.attrs.get("action").lower()
        except:
            action = None
        #  get the form method (POST, GET, etc.) / form yöntemini alın (POST, GET, vb.)
        method = form.attrs.get("method", "get").lower()
        # get all the input details such as type and name / tür ve ad gibi tüm giriş ayrıntılarını alın
        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type","text")
            input_name = input_tag.attrs.get("name")
            input_value = input_tag.attrs.get("value", "")
            inputs.append({"type": input_type, "name": input_name, "value": input_value})
        details["action"] = action
        details["method"] = method
        details["inputs"] = inputs
        return details

    def submit(self, value): 
        """
        English:
            Submitting Web Forms
        Türkçe:
            Web formlarin gönderme
        """
        # get the first form / ilk form getir
        first_form = self.get_all_forms()[0]
        # extract all form details / tüm form ayrıntılarını cikar
        formDetails = self.get_form_details(first_form)
        # the data body we want to submit / göndermek istediğimiz veri gövdesi
        data = {}
        for input_tag in formDetails["inputs"]:
            if input_tag["type"] == "hiddden":
                data[input_tag["name"]] = input_tag["value"]
            elif input_tag["type"] != "submit":
                # value = input(f"Enter the value of the field '{input_tag['name']}' (type: {input_tag['type']}): ")
                data[input_tag["name"]] = value
        new_url = urljoin(self.url, formDetails["action"])
        if formDetails["method"] == "post":
            response = self.session.post(new_url,data=data)
        elif formDetails["method"] == "get":
            response = self.session.get(new_url, params=data)
        # session.put () ve session.delete () yöntemleride var!!!
        self.copy_site(response)

    def copy_site(self, res):    
        soup = bs(res.content, "html.parser")
        for link in soup.find_all("link"):
            try:
                link.attrs["href"] = urljoin(url, link.attrs["href"])
            except:
                pass
        for script in soup.find_all("script"):
            try:
                script.attrs["src"] = urljoin(url, script.attrs["src"])
            except:
                pass
        for img in soup.find_all("img"):
            try:
                img.attrs["src"] = urljoin(url, img.attrs["src"])
            except:
                pass
        for a in soup.find_all("a"):
            try:
                a.attrs["href"] = urljoin(url, a.attrs["href"])
            except:
                pass
        open("page.html","w",encoding="utf-8").write(str(soup))
        webbrowser.open("page.html")

    def printALL(self):
        forms = self.get_all_forms()
        for i, form in enumerate(forms, start=1):
            formDetails = self.get_form_details(form)
            print("="*50, f"form #{i}", "="*50)
            pprint(formDetails)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You did not enter a URL.") # URL girmediniz.
        print("Example: https://example.com") # Örnek: https://example.com
        sys.exit()
    
    control = False
    try:
        response = req.get(sys.argv[1])
        control = True
        url = sys.argv[1]
    except:
        print("Please enter a valid URL") # Lütfen geçerli bir adres girin
    
    if control:
        form = Form(url)
        form.printALL()
        if len(sys.argv) == 3:
            form.submit(sys.argv[2])
