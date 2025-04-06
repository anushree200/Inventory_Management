import Inventory_Management.db_utils as db_utils
print ("Welcome to Inventory management")
uname = input("Enter username:")
pwd = input("Enter password:")
result = db_utils.login(uname, pwd)
if(result == "Success"):
    db_utils.displayData ()
    choice = int(input("Choose one of the following\nl. Add new data\n2. Remove data\n3. Update data\n4. Display data\n5. Exit\n"))
    while (choice >0 and choice <5):
      if choice==1:
        product_name = input("enter product name: ")
        qty = int(input("enter quantity:"))
        price = int(input("enter price:") )
        db_utils.insertData(product_name,price,qty)
      elif choice == 2:
        product_name= input("enter product name:")
        db_utils.deletedata(product_name)
      elif choice==3:
        name = input("Enter product name you would like to update:")
        option=int(input("do you want to change 1. quantity\n2.price\n"))
        if option==1:
          qty=int(input("enter the new quantity:")) 
          db_utils.updateData(name, qty, 0)
        elif option==2:
          price=int(input("enter the new price:"))
          db_utils.updateData(name, 0, price)
        else:
          print("Invalid choice")
      elif choice==4:
        db_utils.displayData()
      choice = int(input("Choose one of the following\nl. Add new data\n2. Remove data\n3. Update data\n4. Display data\n5. Exit\n"))
else:
  print("please check the details")
