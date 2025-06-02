import subprocess


WORKING_DIR = "/home/app/Escritorio/proyecto/SniffPyBot/moderate_bot"


commands = [
    "python3 main.py",
    "python3 remote-driver.py 1",
    "python3 remote-driver.py 2",
    "python3 remote-driver.py 3",
    "python3 remote-driver.py 4",
    "python3 remote-driver.py 5",
    "python3 remote-driver.py 6",
    "python3 remote-driver.py 7",
    "python3 remote-driver.py 8",
    "python3 remote-driver.py 9",
    "python3 remote-driver.py 10",
]

for command in commands:
    print(f"Ejecutando: {command}")
    subprocess.Popen(command, shell=True, cwd=WORKING_DIR)


