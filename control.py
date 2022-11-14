#!C:\Users\HappyUser\AppData\Local\Programs\Python\Python38\python.exe
#-*- coding: utf-8 -*-

# 這是 shopping project 的 控制（control）部分
# 專門控制前端傳過來的要求 →→ 我這裡收到 →→ 向 DB 要求資料
#                                         ↓
#       前端打開弄成網也呈現的樣子 ←← 打包好後傳回去前端 ←← 索取 DB 傳回來的資料

#print headers first
print("Content-Type: text/html; charset=utf-8\n")
#print("Content-type: application/json; charset: utf-8\n")

import json
from datetime import date, datetime
import cgi
import shopping_mall

#main starts here
form = cgi.FieldStorage()
try:
    act=form.getvalue('o')
except:
    # print("o missing")
    exit()

para=()
#we can start accessing DB now

if act=='updateProductList':  # 查看商品清單（顧客看, 不含商品數0）
    msgList = shopping_mall.getProductList() #get an array from model
    newdata = []
    for i in range(len(msgList)-1):   # 只要給顧客看商品數>0的就好
        if(msgList[i]["count"] != 0):
            newdata.append(dict([("id",msgList[i]["id"]), ("name",msgList[i]["name"]), ("count",msgList[i]["count"]), ("description",msgList[i]["description"])])
    )
    result = {
        "list": newdata
    }
    print(json.dumps(result,ensure_ascii=True)) #dump json string to client
elif act=="addProductInList":
    pname_to_add = form.getvalue('name')
    pcount_to_add = int(form.getvalue('count'))
    pdes_to_add = form.getvalue('describtion')
    if(shopping_mall.addProduct(pname_to_add, pcount_to_add, pdes_to_add) == "ok!") :
        print("add new porduct success")
    else:
        print("add new porduct failure")
elif act=='addInCart':  # 將要購買的商品加入購物車
    pid = int(form.getvalue('id'))
    pcount = int(form.getvalue('count'))
    if(shopping_mall.addInCart(pid, pcount) == "ok") :
        print("purchasing success")
    elif (shopping_mall.addInCart(pid, pcount) == "no") :
        print("purchasing failure")
elif act=='updateCartList':  # 查看購物車內所有物品資訊
    msgList = shopping_mall.getCartList() #get an array from model
    msgList = msgList[0:len(msgList)-1]
    result = {
        "list":msgList
    }
    print(json.dumps(result,ensure_ascii=True)) #dump json string to client
elif act=="changeCart":  # 更改購物車內商品資訊
    pid_change = int(form.getvalue('id'))
    pcount_change = int(form.getvalue('count'))
    if(shopping_mall.changeCart(pid_change, pcount_change) == "ok") :
        print("change success")
    elif (shopping_mall.changeCart(pid_change, pcount_change) == "no") :
        print("change failure")
elif act=="checkoutCart":  # 將購物車內所有商品結帳
    if(shopping_mall.checkoutCart() == "ok!") :
        print("checkout success")
    elif (shopping_mall.checkoutCart() == "okk!"):
        print("checkout successsssss")
    else:
        print("no")
elif act=="getAllProductList":   # 查詢所有商品（主管看, 含商品數0）
    msgList = shopping_mall.getProductList() #get an array from model
    result = {
        "list": msgList[0:len(msgList)-1]
    }
    print(json.dumps(result,ensure_ascii=True)) #dump json string to client
elif act=="delPInpList":   # "只能主管" 從某個商品id刪除該商品
    pid_to_del = int(form.getvalue('id'))
    if(shopping_mall.delProduct(pid_to_del) == "ok!") :
        print("delete success")
    else:
        print("delete failure")
elif act=="updateProductInList":
    pid_to_c = int(form.getvalue('id'))
    newName = form.getvalue('name')
    newCount = int(form.getvalue('count'))
    newDes = form.getvalue('describtion')
    if(shopping_mall.updateProduct(pid_to_c, newName, newCount, newDes) == "ok!") :
        print("update porduct success")
    else:
        print("update porduct failure")
elif act=="checkoutItemOff":
    if(shopping_mall.checkoutItemOff() == "ok!") :
        print("checkout Item Off storage success")
    elif (shopping_mall.checkoutItemOff() == "okk!"):
        print("checkout Item Off storage success")
    else:
        print("no")