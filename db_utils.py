import Inventory_Management.app as app
print ("Welcome to Inventory management")
uname = input("Enter username:")
pwd = input("Enter password:")
result = app.login(uname, pwd)
if(result == "Success"):
    app.displayData ()
    choice = int(input("Choose one of the following\nl. Add new data\n2. Remove data\n3. Update data\n4. Display data\n5. Exit\n"))
    while (choice >0 and choice <5):
      if choice==1:
        product_name = input("enter product name: ")
        qty = int(input("enter quantity:"))
        price = int(input("enter price:") )
        app.insertData(product_name,price,qty)
      elif choice == 2:
        product_name= input("enter product name:")
        app.deletedata(product_name)
      elif choice==3:
        name = input("Enter product name you would like to update:")
        option=int(input("do you want to change 1. quantity\n2.price\n"))
        if option==1:
          qty=int(input("enter the new quantity:")) 
          app.updateData(name, qty, 0)
        elif option==2:
          price=int(input("enter the new price:"))
          app.updateData(name, 0, price)
        else:
          print("Invalid choice")
      elif choice==4:
        app.displayData()
      choice = int(input("Choose one of the following\nl. Add new data\n2. Remove data\n3. Update data\n4. Display data\n5. Exit\n"))
else:
  print("please check the details")
