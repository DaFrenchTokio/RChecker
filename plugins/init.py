import os
import requests

class func:
    class proxies:
        temp = os.path.join(os.getenv("TEMP"), "RCheckerProxies")
        filedirect = os.path.join(temp, "proxies.txt")

        if not os.path.exists(temp):
            os.makedirs(temp)
        if not os.path.exists(filedirect):
           with open(filedirect, "w") as f:
              f.write('')
              f.close()	


        def scrape():
            response = requests.get('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt')

            if response.status_code == 200:
                if os.path.exists(func.proxies.filedirect):
                    with open(func.proxies.filedirect, "w") as f:
                        f.write(response.text)
                        f.close()
            else:
                print("Une erreur s'est produite lors de la requête.")
            


        def get():
            if os.stat(func.proxies.filedirect).st_size == 0:
                func.proxies.scrape()
            proxies = open(func.proxies.filedirect).read().split('\n')
            proxy = proxies[0]
            with open(func.proxies.filedirect, 'r+') as fp:
                lines = fp.readlines()
                fp.seek(0)
                fp.truncate()
                fp.writelines(lines[1:])
            return proxy