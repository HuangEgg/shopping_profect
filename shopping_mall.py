# shopping_mall 是一個物件
# 此物件含許多方法：
#     1. 列出所有商品庫存 => getProductList()
#     2. 查看目前購物車
#     3. 刪除購物車內物品
#     4. 將購物車內商品結帳
#     5. 
# 連線DB 引入兩個變數來用, conn(連線), cur()
from dbConfig import conn, cur
from iteration_utilities import duplicates
from iteration_utilities import unique_everseen

def getCartList():
    sql="select * from `cart` order by `checkout`,`product_id`;" # 查詢所有的商品，包含列出商品的所有狀態
    cur.execute(sql)   # 用 cur 執行
    records = cur.fetchall()   # 全部抓出來
    cartData = []
    idInCart = []
    for (pk, product_id, product_name, product_count, checkout) in records:
        temp={
            "pk": pk,
            "product_id": product_id,
            "product_name": product_name,
            "product_count": product_count,
            "checkout": checkout
        }
        cartData.append(temp)
        idInCart.append(product_id)
    for item in cartData:
        if (item["checkout"] == "0"):
            item["checkout"] = "未結帳"
        elif (item["checkout"] == "1"):
           item["checkout"] = "已結帳，未出貨"
        elif (item["checkout"] == "2"):
            item["checkout"] = "已出貨"
    cartData.append(idInCart)
    return cartData

def getProductList():  # 列出所有商品庫存<顧客 & 商場管理員>
    sql="SELECT * FROM `products` ORDER BY `id`;" # 查詢所有商品 
    cur.execute(sql)   # 用 cur 執行
    records = cur.fetchall()   # 全部抓出來
    productData = []
    idCanBuy = []
    for (id, name, count, description) in records:
        temp={
            "id": id,
            "name": name,
            "count": count,
            "description": description,
        }
        idCanBuy.append(id)
        #print(temp)
        productData.append(temp)
    productData.append(idCanBuy)
    return productData    # 會回傳商品資料，最後一個是 list 形態，內含可購買的 id

# 寫法：
#   如果第一次購買（商品id為...）的商品，則用 insert 新增
#   不過之前購買過同種類商品，則用 update 更新 購買數量（product_count）
# 做兩個防呆：
#   防呆1：輸入錯誤id
#   防呆2：購買數量超過商品庫存    
def addInCart(ProductID,ProductCount):  # 將商品加入購物車<顧客> # 防呆1：其他 id # 防呆2：購買數量超過商品庫存
    productData = getProductList()
    cartData = getCartList()
    productDataOfIwantToBuy = {}
    InCartItemCount = 0
    inCartButNotCheckout = False
    for i in productData[0:len(productData)-1]:
        if(i["id"] == ProductID):   # 若有我想購買的商品(id)   且   此商品架上有貨
            productDataOfIwantToBuy = dict([("id",i["id"]), ("name",i["name"]), ("count",i["count"]), ("description",i["description"])])

    if(len(productDataOfIwantToBuy) == 0) :  # 如果我想買的東西不在架上（id）
        return "no"
    # 注意!
    ## 在所有購物車內含有：已結賬&未結帳
    ## 所以是要檢查完車內的符合此id的商品數量

    for j in cartData[0:len(cartData)-1]:
        if(j["product_id"] == ProductID):   # 若有我想購買的商品(id)   且   此商品我之前購買過
            InCartItemCount += j["product_count"]
            print("checkout:",j["checkout"]) # 若有此商品，那此商品是否在車內有 “未結帳” 的商品
            if(j["checkout"] == "未結帳"):
                inCartButNotCheckout = True
    print("cOrNotC:",InCartItemCount)
    # 邏輯上 => 你買進的商品數量，不論你之前買不買過，大於商品目前庫存就不行
    ## 沒有大於：小於等於商品庫存，你再 => 檢查你之前有沒有買
    ##    1. 你沒買：可以直接買（因為你一開始檢查過你要買的數量已經可以買了）
    ##    2. 你買過：不論你買過的商品是否結帳，都要小於你曾經<已結&未結>所購買的商品數
    ##        2.1 你買過但結帳了：新增一筆還沒結帳的新的賬目
    ##        2.2 你買過但還沒結賬：update
    if(ProductCount > productDataOfIwantToBuy["count"]):   # 你買太多：你想買的商品數量大於目前商品庫存
        return "no"
    elif(ProductID not in cartData[-1]):  # 如果你之前沒買過：你想要買的商品(ID)不在你的購物車裡 => 直接買
        sql="insert into cart (product_id, product_name, product_count) values (%s, %s, %s);"
        cur.execute(sql,(ProductID, productDataOfIwantToBuy["name"], ProductCount))
        conn.commit()
        return "ok"
    elif(productDataOfIwantToBuy["count"] >= InCartItemCount+ProductCount):  # 你之前買過：檢查庫存要大於你曾經<已結&未結>所購買的商品數
        if(inCartButNotCheckout == True):  # 如果你之前買過的這項商品在車內有 “未結帳” 的情況，就更新這一筆
            sql="update `cart` set `product_count`=`product_count`+%s where `product_id`=%s and `checkout`=0;"
            cur.execute(sql,(ProductCount,ProductID))
            conn.commit()
            return "ok"
        else:  # 車內只剩結過帳的同品項商品了，那當然不能更新結過帳的了，所以安插一筆新的
            sql="insert into cart (product_id, product_name, product_count) values (%s, %s, %s);"
            cur.execute(sql,(ProductID, productDataOfIwantToBuy["name"], ProductCount))
            conn.commit()
            return "ok"
    else:
        return "no"

# 更改購物車內商品資訊<刪除or增加減少>：寫法
#   如果修改後的數目為 0, 則直接刪除(delete)
#   不然的話<視情況, 可以的話>, 就更新成 user 想要的數量
# 視情況：
#   情況1：id 要是在購物車當中的 物品 id
#   情況2：要更新成這樣的數量是要 => 貨架上還有這樣的數量阿
def changeCart(id_to_change,count_to_change):  # 將購物車內商品更改 # 防呆1：其他 id # 防呆2：購買數量超過商品庫存
    productData = getProductList()
    cartData = getCartList()
    InCartButNotCheck = False   # 唯有之前購買過且未結帳的商品才可更改數目  （沒有買過不行, 買了結帳了不行）
    canBuyLimit = 0  # 我想買的(ID)商品的目前庫存多少：我最多可以賣多少
    IalreadyBuy = 0  # 我以前總共買過多少（含結帳與未結帳）
    for i in productData[0:len(productData)-1]:
        if(i["id"] == id_to_change):   # 若有我想購買的商品(id)   且   此商品架上有貨
            canBuyLimit = i["count"]   # 我最多可以買多少
    for j in cartData[0:len(cartData)-1]:
        if(j["product_id"] == id_to_change):   # 此商品我之前購買過
            IalreadyBuy = IalreadyBuy + j["product_count"]
            if(j["checkout"] == "未結帳"):
                InCartButNotCheck = True   # 確認我還有未結帳的賬目
    if(InCartButNotCheck == False): # 沒有就提早拜拜↑
        return "no"
    if (count_to_change == 0): # 我要刪除這一個商品的未結帳的賬目
        sql="delete from `cart` where `product_id` = %s and `checkout`=0;"
        cur.execute(sql,(id_to_change,))
        conn.commit()
        return "ok"
    elif(canBuyLimit >= IalreadyBuy + count_to_change):
        sql="update `cart` set `product_count`=%s where `product_id` = %s and `checkout`=0;"
        cur.execute(sql,(count_to_change, id_to_change))
        conn.commit()
        return "ok"
    else:
        return "no"





# 在所有購物車<含已結帳與未結帳>的商品中，找出“要結帳的商品中”有與“已結帳商品”相同商品id的就合併成total個數的 1 row
# 
def checkoutCart():
    cartData = getCartList()  # 在 最後一欄[-1] 有購物車內<已結未結>的商品id
    duplicateItemID = (list(unique_everseen(duplicates(cartData[-1]))))  # 找尋重複的商品id  # 重複：已結與未結 
    if len(duplicateItemID) == 0: # 如果沒有重複的 # 代表所有商品都是第一次購買 # 直接全設結帳不用合併
        sql="update `cart` set `checkout`=1 where 1;"
        cur.execute(sql)
        conn.commit()
        return "ok!"
    else: # 有重複的 # 做法：把未結帳的“商品ID”讀出來
        for i in range(len(duplicateItemID)):   # 在所有重複的 購物車物品id (種類） 中
            current_count = 0
            for item in cartData[0:len(cartData)-1]:  # 在所有 購物車內 物品 中
                if(item["product_id"] == duplicateItemID[i]):  # 如果 該物品ID 等於 重複ID （應該只會最多兩筆<已結&未結>）
                    current_count = current_count + item["product_count"]
            sql = "update `cart` set `product_count`=%s where `product_id`=%s;"  # 將以前購買的此 id 的商品數量 更新成 現在新的數量（以前已結+現在未結）
            cur.execute(sql,(current_count, duplicateItemID[i]))
            conn.commit()
            sql = "delete from `cart` where `checkout` = 0 and `product_id`=%s;"  # 刪除未結的那筆 （同此商品id）
            cur.execute(sql,(duplicateItemID[i],))
            conn.commit()
        return "okk!"



def delProduct(id_to_del):
    productData = getProductList()
    if(id_to_del not in productData[-1]):   # 如果主管要刪除的商品ID不在商品列裡的話
        return "no"
    else:
        sql = "delete from `products` where `id` = %s;"  # 將以前購買的此 id 的商品數量 更新成 現在新的數量（以前已結+現在未結）
        cur.execute(sql,(id_to_del,))
        conn.commit()
        return "ok!"

def addProduct(p_name, p_count, p_des):
    productData = getProductList()
    for p in productData[0:len(productData)-1]:   # 簡單檢查：同名不能新增
        if (p_name == p["name"]):    # 如果名字有重複就不能新增同名商品了
            return "no"
    sql = "insert into `products`(`name`, `count`, `description`) values (%s, %s, %s);"  # 將以前購買的此 id 的商品數量 更新成 現在新的數量（以前已結+現在未結）
    cur.execute(sql,(p_name, p_count, p_des))
    conn.commit()
    return "ok!"

def updateProduct(pid, newN, newC, newD):
    productData = getProductList()
    if(pid not in productData[-1]):   # 如果主管要更新的商品ID不在商品列裡的話
        return "no"
    else:
        sql = "update `products` set `name`=%s,`count`=%s,`description`=%s WHERE `id`= %s;"  # 將以前購買的此 id 的商品數量 更新成 現在新的數量（以前已結+現在未結）
        cur.execute(sql,(newN, newC, newD, pid))
        conn.commit()
        return "ok!"

def checkoutItemOff():
    productData = getProductList()
    cartData = getCartList()
    checkoutItemInCart = []
    checkoutItemInCartID = []
    for item in cartData[0:len(cartData)-1]:
        if(item["checkout"] == "已結帳，未出貨"):
            temp = dict([("product_id",item["product_id"]), ("product_count",item["product_count"])])
            checkoutItemInCartID.append(item["product_id"])
            checkoutItemInCart.append(temp)
    checkoutItemInCart.append(checkoutItemInCartID)
    for product in productData[0:len(productData)-1]:   # 檢查所有商品欄位
        for item in checkoutItemInCart[0:len(checkoutItemInCart)-1]:   # 檢查所有已結帳欄位
            if (product["id"] == item["product_id"]):   # 如果商品列中的 id 等於 車內已結帳的 id
                sql = "update `products` set `count`=(`count`- %s) WHERE `id`= %s;"  # 將以前購買的此 id 的商品數量 更新成 現在新的數量（以前已結+現在未結）
                cur.execute(sql,(item["product_count"], product["id"]))
                conn.commit()
                sql = "delete from `cart` where `product_id` = %s;"  # 將以前購買的此 id 的商品數量 更新成 現在新的數量（以前已結+現在未結）
                cur.execute(sql,(item["product_id"],))
                conn.commit()
    return "ok!"