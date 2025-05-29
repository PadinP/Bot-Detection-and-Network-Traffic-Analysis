import pandas as pd
import os

def start():
    escenarios = ['3', '9']
    for e in range(len(escenarios)):
        num = int(escenarios[e])
        if 1 <= num <= 13:
            df = pd.read_csv(f'modulo/database/{num}.binetflow', sep=',')
        else:
            print("Opción inválida")

        bot = 5000000#int(input("Number of bots you want to use: "))
        notBot = 50000#int(input("Number of Not bots you want to use: "))

        # HTTP : sera usado para CF , US y HTTP para estos tipos de ataque revisar tabla pagina oficial de ctu-13
        # PortScan(PS) : TCP
        Escenarios = {1: ["IRC", "SPAM", "HTTP"],
                      2: ["IRC", "SPAM", "HTTP"],
                      3: ["IRC", "TCP", "HTTP"],
                      4: ["IRC", "DNS", "HTTP"],
                      5: ["SPAM", "TCP", "HTTP"],
                      6: ["TCP"],
                      7: ["HTTP"],
                      8: ["TCP"],
                      9: ["IRC", "SPAM", "HTTP", "TCP"],
                      10: ["IRC", "DNS", "HTTP"],
                      11: ["IRC", "DNS", "HTTP"],
                      12: ["P2P"],
                      13: ["SPAM", "TCP", "HTTP"]}

        df1_list = []  # Lista para almacenar los dataframes df1

        # Verifica si la clave es igual al número ingresado por el usuario
        if num in Escenarios:
            bot = bot = int(bot / len(Escenarios[num]))
            print(f"La clave {num} tiene {len(Escenarios[num])} elementos.")
            for value in Escenarios[num]:  # Itera sobre los valores de la clave
                condicion1 = df['Label'].str.contains('Botnet', case=False) & df['Label'].str.contains(value,case=False)
                df1 = df[condicion1]  # Filtra el dataframe original con la condición1.
                if len(df1.index) <= bot:
                    print('entro al if')
                    df1 = df1.iloc[:bot]  # Selecciona las primeras filas del dataframe df1 segun el numero que tenga la variable 'bot'.
                else:
                    print('no entro al if')
                    print(f'bot: {bot}')
                    print('Do sys sampling')
                    df1 = systematic_sample(pop_df=df1, s_size=bot)  # Selecciona las filas del dataframe df1 haciendo sampling sistematico segun el numero que tenga la variable 'bot'.
                    print(len(df1))
                df1_list.append(df1)  # Añade el dataframe df1 a la lista df1_list
        else:
            print("La clave no existe en el diccionario.")

        condicion2 = df['Label'].str.contains('Normal', case=False) | df['Label'].str.contains('Background', case=False)
        df2 = df[condicion2]
        df2 = df2.iloc[:notBot]

        df = pd.concat(df1_list + [df2])
        print(f'len del df final: {len(df)}')

        if not os.path.isfile('0.binetflow'):
            df.to_csv('0.binetflow', index=False)
        else:
            df.to_csv('0.binetflow', mode='a', header=False, index=False)


def systematic_sample(pop_df, percentage=None, s_size=None):
    if s_size is None:
        size = len(pop_df) * percentage
        interval = len(pop_df) / size
    else:
        interval = len(pop_df) / s_size

    sampled_indices = []
    index = 0.0
    while int(index) < len(pop_df):
        sampled_indices.append(int(index))
        index += interval
        index = round(index, 1) if index % 1 != 0 else index

    s_sample = pop_df.iloc[sampled_indices]
    return s_sample


if __name__ == "__main__":
    start()




