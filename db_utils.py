import sqlite3
def login(uname, pwd):
  value = ""
  try:
    con = sqlite3.connect ("database.db")
    cursor = con.cursor()
    cursor.execute(f"select * from users where username = '(uname)'")
    records = cursor.fetchall()
    if len (records)==1:
      if pwd == records [0] [1]:
        value = "Success"
      else:
        value = "Incorrect password"
    else:
      value = "Please check the username"
    cursor.close()
    con.close()
    return value
  except:
    print ("Database error")
def displayData():
  try:
    con = sqlite3.connect("database.db")
    cursor = con.cursor()
    cursor.execute(f"select * from products")
    records = cursor.fetchall()
    for i in records:
      print(f'{i[0]}\t{i[1]}\t{i[2]}\t{i[3]}')
    cursor.close()
    con.close()
  except:
    print("Database error")
def insertData(name, price, qty):
  try:
    con = sqlite3.connect("database.db")
    cursor = con.cursor()
    cursor.execute("select MAX(pid) from products")
    records = cursor.fetchall()
    id_new = records[0][0]+1
    query = f"insert into products(pid, pname, qty,price) values({id_new},'{name}','{qty}','{price}')"
    i = cursor.execute(query)
    print (f"{cursor.rowcount} row added successfully")
    con.commit()
    cursor.close()
    con.close()
  except:
    print("Database error")

def deletedata(product_name) :
  try:
    con = sqlite3.connect("database.db" )
    cursor = con.cursor()
    query = f"delete from products where pname='{product_name}'"
    i = cursor.execute(query)
    print (f"{cursor.rowcount} row deleted successfully")
    con.commit()
    cursor.close()
    con.close()
  except:
    print("Database error")

def updateData(name, qty, price):
  try:
    con = sqlite3.connect("database.db")
    cursor = con.cursor()
    if (qty>0) :
      query = f"update products set qty = {qty} where pname='{name}'"
    else:
      query = f"update products set price = {price} where pname='{name}'"
    i = cursor.execute(query)
    print (f"{cursor.rowcount} row updated successfully")
    con.commit()
    cursor.close()
    con.close()
  except:
    print ("Database error")
