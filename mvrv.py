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

# Função para obter dados do MVRV usando a CoinGecko API
def get_mvrv_data(crypto_id, days):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart'
    params = {
        'vs_currency': 'usd',  # Moeda base
        'days': days
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        mvrv = data['market_caps']
        
        # Converter para DataFrame
        df_mvrv = pd.DataFrame(mvrv, columns=['timestamp', 'market_cap'])
        df_mvrv['Date'] = pd.to_datetime(df_mvrv['timestamp'], unit='ms')
        df_mvrv.set_index('Date', inplace=True)
        df_mvrv.drop('timestamp', axis=1, inplace=True)

        # Supondo que o valor realizado seja o preço médio de compra (simplificação para exemplo)
        df_mvrv['realized_value'] = df_mvrv['market_cap'] / 2  # Isso é uma simplificação
        df_mvrv['MVRV'] = df_mvrv['market_cap'] / df_mvrv['realized_value']
        
        return df_mvrv
    else:
        print(f"Erro ao buscar dados do MVRV: {response.status_code}")
        return pd.DataFrame()

# Função para mostrar o gráfico
def show_graph(df, df_mvrv):
    try:
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        root = Tk()
        root.title("Crypto Price Chart by ahavahdev")

        # Criar a figura
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plotar os preços e a SMA
        ax1.plot(df.index, df['price'], label='Price', color='b')
        ax1.plot(df.index, df['SMA_14'], label='SMA 14', linestyle='--', color='g')

        # Adicionar sinais de compra e venda
        buy_signals = df[df['Buy_Signal'] == 1]
        sell_signals = df[df['Sell_Signal'] == -1]
        ax1.scatter(buy_signals.index, buy_signals['price'], label='Buy Signal', marker='^', color='green', alpha=1)
        ax1.scatter(sell_signals.index, sell_signals['price'], label='Sell Signal', marker='v', color='red', alpha=1)

        # Personalizar o primeiro eixo (preços e SMA)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price (USD)')
        ax1.tick_params(axis='y', labelcolor='b')
        ax1.legend(loc='upper left')

        # Segundo eixo para o MVRV
        ax2 = ax1.twinx()
        ax2.plot(df_mvrv.index, df_mvrv['MVRV'], label='MVRV', linestyle='-', color='r')
        ax2.set_ylabel('MVRV', color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        ax2.legend(loc='upper right')

        # Adicionar título e assinatura
        fig.suptitle('Crypto Price, SMA, and MVRV with Buy/Sell Signals\nby ahavahdev')

        # Adicionar o gráfico ao Tkinter
        fig.tight_layout()
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

# Obter dados do MVRV da criptomoeda
data_mvrv = get_mvrv_data(crypto_id, days)

# Verificar se os dados foram obtidos com sucesso
if data.empty or data_mvrv.empty:
    print(f"Não foi possível obter dados para a criptomoeda {crypto_id}.")
else:
    # Calcular a média móvel simples (SMA)
    data['SMA_14'] = data['price'].rolling(window=14).mean()

    # Gerar sinais de compra e venda
    data['Buy_Signal'] = np.where(data['price'] > data['SMA_14'], 1, 0)
    data['Sell_Signal'] = np.where(data['price'] < data['SMA_14'], -1, 0)

    # Mostrar o gráfico
    show_graph(data, data_mvrv)
