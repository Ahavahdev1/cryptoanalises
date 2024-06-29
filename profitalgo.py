import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk

# Função para obter dados históricos de criptomoedas usando a CoinGecko API
def get_crypto_data(crypto_id, days):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart'
    params = {
        'vs_currency': 'usd',  # Moeda base
        'days': days
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        prices = data['prices']
        
        # Converter para DataFrame
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('Date', inplace=True)
        df.drop('timestamp', axis=1, inplace=True)
        
        return df
    else:
        print(f"Erro ao buscar dados: {response.status_code}")
        return pd.DataFrame()

# Função para mostrar o gráfico
def show_graph(df):
    try:
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        root = Tk()
        root.title("Crypto Price Chart by Ahavahdev")

        # Criar a figura
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plotar os dados
        ax.plot(df.index, df['price'], label='Price')
        ax.plot(df.index, df['SMA_14'], label='SMA 14', linestyle='--')

        # Personalizar o gráfico
        ax.set_title('Crypto Price and SMA by Ahavahdev')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (USD)')
        ax.legend()

        # Adicionar o gráfico ao Tkinter
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        canvas.draw()

        root.mainloop()

    except ImportError as e:
        print("Para visualizar o gráfico, você precisa ter o 'matplotlib' instalado.")
        print(f"Erro: {e}")

# Configurações do usuário
crypto_id = input("Digite o ID da criptomoeda (por exemplo, 'bitcoin' para Bitcoin): ")
days = input("Digite o número de dias para os dados históricos (ex: '30' para 30 dias): ")

# Obter dados históricos da criptomoeda
data = get_crypto_data(crypto_id, days)

# Verificar se os dados foram obtidos com sucesso
if data.empty:
    print(f"Não foi possível obter dados para a criptomoeda {crypto_id}.")
else:
    # Calcular a média móvel simples (SMA)
    data['SMA_14'] = data['price'].rolling(window=14).mean()

    # Gerar sinais de compra e venda
    data['Buy_Signal'] = np.where(data['price'] > data['SMA_14'], 1, 0)
    data['Sell_Signal'] = np.where(data['price'] < data['SMA_14'], -1, 0)

    # Sinais combinados
    data['Signal'] = data['Buy_Signal'] + data['Sell_Signal']

    # Mostrar o gráfico
    show_graph(data)

