from datetime import datetime
import mysql.connector
from mysql.connector import Error
import logging

# Nama file yang akan dibaca
file_path = '../uploads/weigherLog31_20241219_153145.txt'

# Fungsi untuk menyisipkan data ke MySQL

def insert_data(cursor, data):
    try:
        # Cetak data sebelum insert
        print("Data sebelum insert:", data)

        sql_insert_query = """INSERT INTO data_weigher (device_id, device_name, product, weight, date, ip_address, wifi) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        
        # Cetak query dan data
        print("SQL Query:", sql_insert_query)
        print("Data untuk diinsert:", data)
        
        cursor.execute(sql_insert_query, data)
    except Error as e:
        print(f"Kesalahan saat menyisipkan data: {e}")
        # Cetak detail error
        import traceback
        traceback.print_exc()

def insert_data_fail(cursor, data):
    try:
        # Cetak data sebelum insert
        print("Data 'fail' sebelum insert:", data)

        sql_insert_query = """INSERT INTO log_fail (data_log, date) 
                              VALUES (%s, %s)"""
        
        # Cetak query dan data
        print("SQL Query 'fail':", sql_insert_query)
        print("Data 'fail' untuk diinsert:", data)
        
        cursor.execute(sql_insert_query, data)
    except Error as e:
        print(f"Kesalahan saat menyisipkan data 'fail': {e}")
        # Cetak detail error
        import traceback
        traceback.print_exc()

def log_process(file_path):
    try:
        connection = mysql.connector.connect(
            host='192.168.15.223',
            user='admin',
            password='itbekasioke',
            database='weigher',
            port='3306'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            logging.info("Koneksi database berhasil")

            with open(file_path, 'r') as file:
                lines = file.readlines()
                logging.info(f"Jumlah baris: {len(lines)}")

                for line in lines:
                    line = line.strip()
                    data = line.split(',')
                    # print(len(data))
                    if len(data) != 6:
                        fail_data = [line, getTime()]
                        print(fail_data)
                        insert_data_fail(cursor, fail_data)
                        connection.commit()
                        continue
                    # logging.debug(f"Baris mentah: {line}")
                    # logging.debug(f"Data setelah split: {data}")

                    try:
                        # Validasi dan transformasi data
                        processed_data = [
                            data[0].strip(),    # device_id
                            data[1].strip(),    # device_name
                            data[2].strip(),    # product
                            float(data[3].strip()),  # weight
                            getTime(),          # date
                            data[4].strip(),    # ip_address
                            data[5].strip()     # wifi
                        ]

                        insert_data(cursor, processed_data)
                        connection.commit()
                        logging.info(f"Berhasil insert: {processed_data}")

                    except Exception as e:
                        logging.error(f"Gagal memproses baris: {line}")
                        logging.error(f"Error: {e}")

    except Exception as e:
        logging.error(f"Kesalahan umum: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("Koneksi database ditutup")

def getTime():
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_time

# if __name__ == "__main__":
#     log_process(file_path)