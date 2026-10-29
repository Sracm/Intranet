import sqlite3

URL = ('https://app.powerbi.com/reportEmbed?reportId=5a2a1ded-b800-406f-83ab-23a791544279'
       '&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53&actionBarEnabled=true')

conn = sqlite3.connect('intranet.db')
n = conn.execute(
    "UPDATE reports SET embed_url=? WHERE title='Demandas de Reabastecimento do Estoque'", (URL,)
).rowcount
conn.commit()
print('linhas atualizadas:', n)
print(conn.execute("SELECT id, title, embed_url FROM reports WHERE title LIKE 'Demandas%'").fetchall())
conn.close()
