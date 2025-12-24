from telethon import TelegramClient
from datetime import datetime
import pandas as pd
import asyncio

api_id = Тут ставим id без кавычек, например 56318784
api_hash = 'Тут ставим свой хэш'
channel = 'Тут имя канала, например datajobskz'

start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()
    print("Авторизация успешна!")
    
    me = await client.get_me()
    print(f"Вы вошли как: {me.username or me.first_name}")
    
    data = []
    message_count = 0
    
    async for message in client.iter_messages(channel):
        message_count += 1
        
        if message.date is None:
            continue
        
        # Убираем информацию о временной зоне для сравнения
        message_date = message.date.replace(tzinfo=None)
        
        if start_date <= message_date <= end_date:
            # Преобразуем дату в строку без временной зоны
            date_without_tz = message.date.replace(tzinfo=None)
            
            data.append({
                'date': date_without_tz,
                'date_original': message.date.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'text': message.text or '',
                'message_id': message.id
            })
        
        # Прогресс каждые 50 сообщений
        if message_count % 50 == 0:
            print(f"Обработано {message_count} сообщений...")
    
    print(f"Всего обработано: {message_count} сообщений")
    print(f"Соответствует фильтру дат: {len(data)} сообщений")
    
    if data:
        df = pd.DataFrame(data)
        
        # Убедимся, что даты без временных зон
        df['date'] = pd.to_datetime(df['date'])
        
        # Сортируем по дате (от новых к старым)
        df = df.sort_values('date', ascending=False).reset_index(drop=True)
        
        # Сохраняем в Excel
        df.to_excel('vacancies_2025.xlsx', index=False)
        print(f"Данные сохранены в vacancies_2025.xlsx")
        print(f"Столбцы: {df.columns.tolist()}")
        print(f"Размер: {len(df)} строк")
        
        # Показываем первые несколько строк
        print("\nПервые 5 строк:")
        for i, row in df.head().iterrows():
            print(f"{row['date'].strftime('%Y-%m-%d %H:%M')}: {row['text'][:100]}...")
    else:
        print("Нет сообщений за указанный период")

if __name__ == '__main__':
    try:
        with client:
            client.loop.run_until_complete(main())
    except Exception as e:
        print(f"Ошибка: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:

        input("\nНажмите Enter для выхода...")
