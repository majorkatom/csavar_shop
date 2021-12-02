from app import Bolts, db

db.create_all()

with open('db_elements.txt', 'r', encoding='utf-8') as records_file:
    added_records = []
    for record in records_file:
        if record != '\n' and record not in added_records:
            added_records.append(record)
            record = record.replace("'", '')
            record = record.replace('\n', '')
            record = record.replace('ü', 'u')
            
            data = record.split(',')
            data[0] = data[0].strip()
            data[2] = data[2].strip()

            if data[2] == 'M3':
                price = 3
            elif data[2] =='M4':
                price = 5
            elif data[2] =='M5':
                price = 8
            elif data[2] == 'M6':
                price = 10
            elif data[2] == 'M8':
                price = 12
            elif data[2] == 'M10':
                price = 12
            elif data[2] == 'M12':
                price = 15
            elif data[2] == 'M16':
                price = 18
            elif data[2] == 'M20':
                price = 20

            db.session.add(Bolts(description=data[0].lower(), nomD=data[2], length=int(data[3]), threadL=int(data[4]), price=price, qty=100))

db.session.commit()
