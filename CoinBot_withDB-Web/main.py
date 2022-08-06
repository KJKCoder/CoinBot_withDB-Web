import threading
import os
import CoinBot_with_DB

Base_Dir = os.chdir('CoinBotWeb')
if __name__ == '__main__' :

        print('start')
        threads = []

        t = threading.Thread(target=os.system, args=(f'python manage.py runserver {8000}',), daemon=True)
        t.start()
        threads.append(t)

        t = threading.Thread(target=CoinBot_with_DB.run, daemon=True)
        t.start()
        threads.append(t)

        for t in threads:
                t.join() 

        print('end')
                