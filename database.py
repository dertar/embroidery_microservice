import sqlite3
import re
import webcolors

def convert_from_html_to_sqlite3(html_file_path, database_file_path):
    html_file = open(html_file_path, 'r')
    html_text = html_file.read()
    html_file.close()

    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()

    cursor.execute('''CREATE TABLE dmc (dmc text, gamma text, anchor text, madeira text, hex_color int, red int, green int, blue int)''')

    html_trs = html_text.split('</tr>')
    for tr in html_trs[:-1]:
        foundall = re.findall('r\">.*', tr)
        color = re.findall('#.{6}', tr)

        item = [x[3:].replace(' ', '').replace('&nbsp;', '').replace('</p>', '') for x in foundall]

        item[4] = color[0]
        rgb = webcolors.hex_to_rgb(item[4])
        cursor.execute('''INSERT INTO dmc VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')'''.format(item[0], item[1], item[2], item[3], item[4], rgb[0], rgb[1], rgb[2]))

    connect.commit()
    connect.close()

def load_data_from_db(database_file_path):
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()
    
    ret = ([(row[:-3], (row[5],row[6],row[7])) for row in  cursor.execute('SELECT * FROM dmc')], [ch for ch in cursor.execute('SELECT * FROM symbols2')])
    connect.close()
    return ret
