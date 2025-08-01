import os
from argparse import ArgumentParser

from dotenv import load_dotenv
from tqdm import tqdm
from web3 import Web3

# --- Цветовые константы для интерфейса монитора ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def connect_to_network():
    """Подключается к сети Ethereum для сбора данных."""
    load_dotenv()
    infura_project_id = os.getenv("INFURA_PROJECT_ID")
    if not infura_project_id or infura_project_id == "YOUR_INFURA_PROJECT_ID_HERE":
        print(f"{Colors.FAIL}Ошибка оборудования: INFURA_PROJECT_ID не настроен.{Colors.ENDC}")
        print(f"Требуется настройка. Создайте файл {Colors.BOLD}.env{Colors.ENDC} с вашим ключом.")
        print("Формат: INFURA_PROJECT_ID=\"abcdef1234567890\"")
        return None
    
    w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{infura_project_id}'))
    
    if not w3.is_connected():
        print(f"{Colors.FAIL}Нет сигнала от сети Ethereum.{Colors.ENDC}")
        return None
        
    print(f"{Colors.GREEN}Соединение с сетью установлено. Монитор готов к работе.{Colors.ENDC}")
    return w3

def monitor_vitals(w3, contract_address, num_blocks):
    """
    Снимает и анализирует витальные показатели (vitals) смарт-контракта.
    Основной показатель - приток новых пользователей.
    """
    try:
        patient_address = w3.to_checksum_address(contract_address)
    except ValueError:
        print(f"{Colors.FAIL}Ошибка идентификации: неверный ID пациента (адрес контракта).{Colors.ENDC}")
        return

    latest_block_number = w3.eth.block_number
    start_block = latest_block_number - num_blocks + 1

    print(f"\n{Colors.HEADER}{Colors.BOLD}🩺 Запуск монитора EtherPulse...{Colors.ENDC}")
    print(f"ПАЦИЕНТ:{Colors.CYAN} {patient_address}{Colors.ENDC}")
    print(f"ГЛУБИНА АНАЛИЗА:{Colors.CYAN} {num_blocks} блоков (период с {start_block} по {latest_block_number}){Colors.ENDC}")
    
    active_users_in_period = set()
    total_transactions = 0

    pbar = tqdm(range(start_block, latest_block_number + 1), 
                desc=f"{Colors.BLUE}Снятие кардиограммы{Colors.ENDC}",
                ncols=100)

    for block_num in pbar:
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                if tx['to'] and w3.to_checksum_address(tx['to']) == patient_address:
                    total_transactions += 1
                    user_address = w3.to_checksum_address(tx['from'])
                    active_users_in_period.add(user_address)
        except Exception as e:
            tqdm.write(f"{Colors.WARNING}Помехи на линии в блоке {block_num}: {e}{Colors.ENDC}")
            continue

    # --- РАСЧЕТ ПОКАЗАТЕЛЕЙ ---
    total_unique_users = len(active_users_in_period)
    
    # Симулируем, что до этого периода мы не знали ни об одном пользователе.
    # Это позволяет нам измерить приток "новых пациентов".
    known_users_before_period = set() 
    new_users = active_users_in_period - known_users_before_period
    
    # Наша ключевая метрика: Витальность!
    vitality_score = (len(new_users) / total_unique_users) * 100 if total_unique_users > 0 else 0
    # Пульс - среднее количество транзакций на блок
    pulse_rate = total_transactions / num_blocks

    # --- ВЫВОД ДИАГНОСТИЧЕСКОГО ОТЧЕТА ---
    print(f"\n{Colors.HEADER}{Colors.BOLD}📋 Диагностический отчет EtherPulse:{Colors.ENDC}")
    print("--------------------------------------------------")
    print(f"Общее число транзакций (сердцебиений): {Colors.BOLD}{Colors.GREEN}{total_transactions}{Colors.ENDC}")
    print(f"Уникальных пользователей (активных клеток): {Colors.BOLD}{Colors.GREEN}{total_unique_users}{Colors.ENDC}")
    print(f"Пульс (транзакций/блок): {Colors.BOLD}{Colors.CYAN}{pulse_rate:.2f}{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{Colors.UNDERLINE}Ключевой показатель здоровья:{Colors.ENDC}")
    print(f"❤️  {Colors.WARNING}Индекс Витальности (Vitality Score):{Colors.ENDC} "
          f"{Colors.BOLD}{vitality_score:.2f}%{Colors.ENDC}")
    print(f"   {Colors.WARNING}(Доля новых пользователей в общей массе активных){Colors.ENDC}")
    print("--------------------------------------------------")
    
    if vitality_score > 80:
         print(f"{Colors.GREEN}ДИАГНОЗ: Отличное здоровье. Пациент демонстрирует быстрый рост и регенерацию.{Colors.ENDC}")
    elif vitality_score > 50:
        print(f"{Colors.CYAN}ДИАГНОЗ: Стабильное состояние. Наблюдается здоровый приток новых пользователей.{Colors.ENDC}")
    else:
        print(f"{Colors.BLUE}ДИАГНОЗ: Требуется наблюдение. Активность поддерживается зрелым организмом, приток новых пользователей ограничен.{Colors.ENDC}")


if __name__ == "__main__":
    parser = ArgumentParser(description="EtherPulse - монитор витальных показателей смарт-контрактов.")
    parser.add_argument("contract", help="Адрес пациента (смарт-контракта) для обследования.")
    parser.add_argument("-b", "--blocks", type=int, default=1000, help="Глубина обследования в блоках (по умолчанию: 1000).")
    
    args = parser.parse_args()
    
    network_connection = connect_to_network()
    if network_connection:
        monitor_vitals(network_connection, args.contract, args.blocks)
