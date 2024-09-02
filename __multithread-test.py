import threading
from flask import Flask, request
import time

def sanity(function):
    def wrapper(*args):
        try:
            print(f'\033[46m[+] {function}:{__name__}@{function.__name__}({args}) \033[0m')
            return function(*args)
        except Exception as ex:
            print(f'\033[41m[-] {function}:{__name__}@{function.__name__}({args}): FAILED -> {ex} \033[0m')
            return ex
    return wrapper

def threader(function):
    def wrapper(*args):
        try:
            print(f'\033[46m[+] {function}:{__name__}@{function.__name__}({args}) started as thread\033[0m')
            threading.Thread(target=lambda: function(args)).start()
        except Exception as ex:
            print(f'\033[41m[-] {function}:{__name__}@{function.__name__}({args}): FAILED THREAD-> {ex} \033[0m')
            return ex
    return wrapper


### FLASK ###
app = Flask(__name__)
app.config["DEBUG"] = True

# Webserver
@sanity 
def web():
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

# homepage
@app.route("/", methods=['GET', 'POST'])
def hello_world():
        ### ERROR ###
        # [-] <function web at 0x7fe48843db40>:__main__@web(()): FAILED -> signal only works in main thread of the main interpreter
        threading.Thread(target=lambda: web_task('WEBCALL')).start()
        # same error when:
        web_task('WEBCALL')
        ### Solution in name == main
        return 'WEB THREAD'


### BACKGROUND TASKS ###
# called from main
@sanity 
def task(arg1):
    print(f"\033[92m[!!!]Start Task with arg1={arg1}\033[0m")
    threading.Thread(target=lambda: called_task('called')).start()
    for t in range(6):
        print("waiting for task1")
        time.sleep(2)

# called from thread
@sanity 
def called_task(arg1):
    print(f"\033[92m[!!!]Start Task with arg1={arg1}\033[0m")
    for t in range(3):
        print("waiting for task2")
        time.sleep(5)

# called from web
@threader 
def web_task(arg1):
    print(f"\033[92m[!!!] Started WebTask with arg1={arg1}\033[0m")

@sanity
def web_task_caller(arg1):
    threading.Thread(target=lambda: web_task(arg1)).start()


## EXECUTE ###
if __name__ == '__main__':
    ### FIX ###
    # start backgroud threads
    threading.Thread(target=lambda: task('main')).start()
    # The Flask app now runs directly in the main thread when the script is executed.
    # The threading logic in the Flask route now avoids operations that require main-thread execution.
    # The code defines a Flask application with various threading operations. 
    # The main issue stems from attempting to start a new thread from within a Flask route, 
    # which then calls a function that potentially interacts with signals or operations that require being in the main thread.
    web()
