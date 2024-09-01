from flask import Flask, render_template, redirect, request, session, jsonify
from datetime import date
from datetime import datetime, time
import pyodbc, random
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# 設定日誌紀錄器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 設定日誌處理程序
handler = logging.FileHandler('LogFile/history.log')
handler.setLevel(logging.INFO)

# 設定日誌訊息格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 將處理程序添加到日誌紀錄器
logger.addHandler(handler)

# 資料庫連線設定
def create_connection():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-7GLRS7Q;"
        "Database=airlineWeb;"
        "Trusted_Connection=yes;"
    )
    return conn


def generate_bank_account():
    banks = {
        '001': 'Bank A',
        '002': 'Bank B',
        '003': 'Bank C',
    }
    bank_code, bank_name = random.choice(list(banks.items()))
    bank_account_number = ''.join(random.choices('0123456789', k=10))
    bank_account = f"{bank_code}-{bank_account_number} ({bank_name})"
    return bank_account


@app.route('/get_log_content', methods=['GET'])
def get_log_content():
    log_path = 'C:/Users/user/Desktop/CodeProjects/AirlineWeb/LogFile/history.log'  # 請替換為您的日誌檔案路徑

    with open(log_path, 'r') as file:
        log_content = file.read()
        # log_content = ''.join(log_lines[-10:])
    return jsonify(log_content=log_content)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 從表單獲取輸入的帳號和密碼
        account = request.form['account']
        password = request.form['password']

        conn = create_connection()
        cursor = conn.cursor()

        # 執行 SQL 查詢，比對帳號和密碼是否存在於資料庫中
        cursor.execute("SELECT * FROM Members WHERE account = ? AND password = ?", (account, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:            
            # 將使用者資訊轉換成可序列化的字典形式
            user_dict = {
                'mId': user.mId,
                'mName': user.mName,
                'Email': user.Email,
                'Sex': user.Sex,
                'mNumber': user.mNumber,
                'referrerId': user.referrerId,
                'registrationDate': user.registrationDate,
                'account': user.account,
                'password': user.password,
                'role': user.role
            }

            # 如果驗證成功，將使用者資訊存儲在 session 中
            session['user'] = user_dict
            if session['user']['role'] == "Admin":
                logger.info(f'Admin {user.mName} 登入成功')
                return redirect('/admin_page')  # Redirect to the admin page
            else:
                logger.info(f'使用者 {user.mName} 登入成功')
                return redirect('/flights')  # Redirect to the flights page for members
        else:
            # 驗證失敗，重新顯示登入頁面
            return render_template('login.html', error='Invalid account or password')

    return render_template('login.html', error=None)


@app.route('/SignUp')
def sign_up():
    return render_template('sign_up.html', error=None)


@app.route('/register', methods=['POST'])
def register():
    conn = create_connection()
    cursor = conn.cursor()
    # 获取表单数据
    cursor.execute("SELECT MAX(mId) FROM Members")
    max_mId = cursor.fetchone()
    # print(max_oNo)
    # print(type(max_oNo))
    if max_mId:
        new_mId = 'M' + str(int(max_mId[0][1:]) + 1).zfill(3)
    else:
        new_mId = 'M001'

    mName = request.form.get('mName')
    Email = request.form.get('Email')
    Sex = request.form.get('Sex')
    mNumber = request.form.get('mNumber')
    referrerId = request.form.get('referrerId')
    Date = date.today()
    registration_date = Date.strftime('%Y-%m-%d')
    account = request.form.get('account')
    password = request.form.get('password')
    role = 'Member'

    # 在这里执行注册逻辑

    cursor.execute(
        "INSERT INTO Members (mId, mName, Email, Sex, mNumber, referrerId, registrationDate, account, password, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (new_mId, mName, Email, Sex, mNumber, referrerId, registration_date, account, password, role)
        )
    conn.commit()
    conn.close()
    logger.info(f'{mName} 註冊成功')
    return render_template('signup_successful.html')


@app.route('/admin_page')
def admin():
    # 檢查使用者是否已經登入
    if 'user' not in session:
        return redirect('/')
    
    log_path = 'C:/Users/user/Desktop/CodeProjects/AirlineWeb/LogFile/history.log'  # 請替換為您的日誌檔案路徑

    with open(log_path, 'r') as file:
        log_content = file.read()
        # log_content = ''.join(log_lines[-10:])

    # 從 session 中獲取使用者資訊
    user = session['user']
    username = user['mName']  # 使用者名稱

    conn = create_connection()
    cursor = conn.cursor()

    # 取得航班資訊
    cursor.execute("SELECT * FROM Flight")
    flights = []
    for row in cursor.fetchall():
        flight = {
            'fId': row.fId,
            'fName': row.fName,
            'dAirport': row.dAirport,
            'aAirport': row.aAirport,
            'dTime': row.dTime,
            'aTime': row.aTime,
            'amount':row.amount
        }
        flights.append(flight)

    conn.close()

    return render_template('admin.html', username=username, flights=flights, log_content=log_content)


@app.route('/statistics')
def statistics():
    return render_template('statistics.html')


@app.route('/usermanagement')
def usermanagement():
    users = []
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Members")
    users = cursor.fetchall()
    conn.close()
    print(users)
    return render_template('usermanagement.html', users=users)


@app.route('/admin/<string:mId>/edituser')
def edituser(mId):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Members WHERE mId=?",(mId,))
    user = cursor.fetchone()
    conn.close()
    return render_template('edituser.html', user=user)


@app.route('/admin/edituser/save' ,methods=['POST'])
def saveuser():
    if request.method=='POST':
        mId = request.form['ID']
        mName = request.form['name']
        Email = request.form['email']
        Sex = request.form['sex']
        mNumber = request.form['phone']
        reffer = request.form['referrer']
        registrationDate = request.form['join-date']
        account = request.form['account']
        password = request.form['password']
        role = request.form['role']
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Members SET mName=?, Email=?, Sex=?, mNumber=?, referrerId=?, registrationDate=?, account=?, password=?, role=? WHERE mId=?",
               (mName, Email, Sex, mNumber, reffer, registrationDate, account, password, role, mId))
        conn.commit()
        conn.close()
        logger.info(f'User editted complete')

    return render_template('updateuserss.html')


@app.route('/admin/<string:mId>/deleteuser')
def deleteuser(mId):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Members WHERE mId=?",(mId,))
    conn.commit()
    conn.close()
    logger.info(f'User deleted complete')
    return render_template('updateuserss.html')


@app.route('/flights')
def flights():
    # 檢查使用者是否已經登入
    if 'user' not in session:
        return redirect('/')

    # 從 session 中獲取使用者資訊
    user = session['user']
    username = user['mName']  # 使用者名稱

    conn = create_connection()
    cursor = conn.cursor()

    # 取得航班資訊
    cursor.execute("SELECT * FROM Flight")
    flights = []
    for row in cursor.fetchall():
        flight = {
            'fId': row.fId,
            'fName': row.fName,
            'dAirport': row.dAirport,
            'aAirport': row.aAirport,
            'dTime': row.dTime,
            'aTime': row.aTime,
            'amount':row.amount
        }
        flights.append(flight)

    conn.close()

    return render_template('flights.html', username=username, flights=flights)


@app.route('/flight/<string:fId>', methods=['GET', 'POST'])
def flight_detail(fId):
    # 检查用户是否已登录
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        # 获取表单中的数据
        seat = request.form['seat']
        cabin_class = request.form['cabin-class']
        paymethod = request.form['paymethod']
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT amount FROM Flight WHERE fId = ?", (fId,))
        flight_price = cursor.fetchone()[0]
        amount = flight_price  # 订单金额与选择的機票金額一致
        status = 'Pending'  # 假设订单状态为Pending  
        # 获取当前日期
        oDate = date.today()
        oDate_str = oDate.strftime('%Y-%m-%d')

        mId = session['user']['mId']  # 获取当前登录会员的会员编号
        # 执行查询操作以获取最大的订单编号和票号
        cursor.execute("SELECT MAX(oNo) FROM Orders")
        max_oNo= cursor.fetchone()
        cursor.execute("SELECT MAX(tNo) FROM Ticket")
        max_tNo= cursor.fetchone()
        # print(max_oNo)
        # print(type(max_oNo))
        if max_oNo:
            new_oNo = 'O' + str(int(max_oNo[0][1:]) + 1).zfill(3)
        else:
            new_oNo = 'O001'
        if max_tNo:
            new_tNo = 'T' + str(int(max_tNo[0][1:]) + 1).zfill(3)
        else:
            new_tNo = 'T001'
        # print(oDate_str)
        # print(oDate_str == '2023-06-03')
        #执行插入数据的操作到Orders表
        cursor.execute("INSERT INTO Orders (oNo,paymethod,amount,status,oDate,mId,fId) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (new_oNo, paymethod, amount, status, oDate_str, mId, fId))
        # 执行插入数据的操作到Ticket表
        cursor.execute("INSERT INTO Ticket (tNo, seat, cabinClass, fId, oNo) VALUES (?, ?, ?, ?, ?)",
                       (new_tNo, seat, cabin_class, fId, new_oNo))
        conn.commit()
        # 查询車票資料
        cursor.execute("SELECT * FROM Ticket WHERE tNo = ?", (new_tNo,))
        ticket = cursor.fetchone()
        cursor.execute("SELECT * FROM Orders WHERE oNo = ?", (new_oNo,))
        orders = cursor.fetchone()

        conn.close()

        # 将車票資料传递给ticket.html模板
        return render_template('ticket_detail.html', ticket=ticket, orders=orders)
    else:
        # click進去航班資訊的
        conn = create_connection()
        cursor = conn.cursor()
        sDate = datetime.today()
        # s_time = datetime.strptime(sDate, '%Y-%m-%dT%H:%M')
        user = session['user']
        userId = user['mId']  # 使用者名稱
        cursor.execute("INSERT INTO Search (mId, fId,  sDate) VALUES (?, ?, ?)", (userId, fId, sDate))
        conn.commit()
        # 查询特定航班的详细信息
        cursor.execute("SELECT * FROM Flight WHERE fId = ?", (fId,))
        flight = cursor.fetchone()

        conn.close()

        return render_template('confirm_order.html', flight=flight)


@app.route('/flight/search_flights', methods=['POST'])
def flight_search():
    # 获取表单中提交的数据
    departureTime = request.form['departureTime']
    departure = request.form['departure']
    arrivalTime = request.form['arrivalTime']
    destination = request.form['destination']
    # 验证日期字段是否为空
    # if not departureTime or not arrivalTime:
    #     return "Please provide valid departure and arrival dates."
    
    conn = create_connection()
    cursor = conn.cursor()
    # 從 session 中獲取使用者資訊
    user = session['user']
    username = user['mName']  # 使用者名稱
    
    try:
        # 将表单提交的时间转换为datetime对象
        departureTime = datetime.strptime(departureTime, '%Y-%m-%dT%H:%M')
        arrivalTime = datetime.strptime(arrivalTime, '%Y-%m-%dT%H:%M')
        
        # 使用输入的条件进行查询，筛选符合条件的航班数据
        cursor.execute("SELECT * FROM Flight WHERE dAirport = ? AND aAirport = ? AND dTime >= ? AND aTime <= ?",
                       (departure, destination, departureTime, arrivalTime))
        flights = cursor.fetchall()

        # 返回匹配的航班数据
        return render_template('flight_search_results.html', username=username, flights=flights)
    
    except ValueError as e:
        cursor.execute("SELECT * FROM Flight")
        flights = cursor.fetchall()
        return render_template('flights.html', flights=flights, username=username, error='Please provide full keywords')
    
    finally:
        conn.close()


@app.route('/flight/<string:fId>/edit')
def edit(fId):
    # 從 session 中獲取使用者資訊
    user = session['user']
    username = user['mName']  # 使用者名稱
    logger.info(f'Admin {username} is editting')
    # 根据 fId 从数据库中获取航班信息
    # 连接数据库、执行查询语句等
    # 执行查询语句获取航班信息
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Flight WHERE fId = ?", (fId,))
    flight = cursor.fetchone()
    conn.close()
    return render_template('edit.html', flight=flight)


@app.route('/flight/<string:fId>/update', methods=['POST'])
def update_flight(fId):
    # 获取表单中提交的数据
    fName = request.form['fName']
    dAirport = request.form['dAirport']
    aAirport = request.form['aAirport']
    d_time_str = request.form['dTime']
    a_time_str = request.form['aTime']
    amount = request.form['amount']
    conn = create_connection()
    cursor = conn.cursor()

    # 将日期时间字符串转换为 datetime 对象
    d_time = datetime.strptime(d_time_str, '%Y-%m-%dT%H:%M')
    a_time = datetime.strptime(a_time_str, '%Y-%m-%dT%H:%M')

    # 更新航班信息
    cursor.execute("UPDATE Flight SET fName = ?, dAirport = ?, aAirport = ?, dTime = ?, aTime = ?, amount = ? WHERE fId = ?", 
                   (fName, dAirport, aAirport, d_time, a_time, amount, fId))
    conn.commit()

    conn.close()

    return redirect('/flight/success')


@app.route('/flight/<string:fId>/delete')
def delete(fId):
    conn = create_connection()
    cursor = conn.cursor()
    # cursor.execute("DELETE FROM Ticket WHERE fId=?", (fId,))
    # cursor.execute("DELETE FROM Search WHERE fId=?", (fId,))
    user = session['user']
    username = user['mName']  # 使用者名稱
    logger.info(f'Admin {username} Deleted {fId}')
    cursor.execute("DELETE FROM Flight WHERE fId=?", (fId,))
    conn.commit()
    # cursor.execute("SELECT COUNT(fId) FROM Flight")  # 按照編號順序查詢航班資料
    # nums = cursor.fetchall()
    # cursor.execute("SELECT * FROM Flight")
    # flight = cursor.fetchall()
    # for i in range(nums[0][0]):
    #     if flight[i][0] > fId:
    #         a = flight[i][0]
    #         flight[i][0] -= 1
    #         cursor.execute("UPDATE Flight SET fId=? WHERE fId=?", 
    #                (flight[i][0], a))
    #         cursor.execute("UPDATE Ticket SET fId=? WHERE fId=?", 
    #                (flight[i][0], a))
    #         conn.commit()
    
    conn.close()
    return render_template('update_successful.html')


@app.route('/flight/add')
def add_flight():
    user = session['user']
    username = user['mName']  # 使用者名稱
    logger.info(f'Admin {username} is adding')
    return render_template('add_flight.html')


@app.route('/flight/save', methods=['POST'])
def save_flight():
    # 获取表单数据
    f_name = request.form['fName']
    d_airport = request.form['dAirport']
    a_airport = request.form['aAirport']
    d_time_str = request.form['dTime']
    a_time_str = request.form['aTime']
    amount = request.form['amount']

    # 将日期时间字符串转换为 datetime 对象
    d_time = datetime.strptime(d_time_str, '%Y-%m-%dT%H:%M')
    a_time = datetime.strptime(a_time_str, '%Y-%m-%dT%H:%M')

    # 在此处执行数据库插入操作，将机票信息保存到数据库中
    # 连接数据库、执行插入语句等
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(fId) FROM Flight")
    max_fId= cursor.fetchone()
    # 假設 max_fId 為目前最大的 fId 值，例如 'F001'

    # 假設 max_fId 是一個元組，例如 ('F001',)

    if max_fId:
        new_fId = 'F' + str(int(max_fId[0][1:]) + 1).zfill(3)
    else:
        new_fId = 'F001'
    # 使用 new_fId 來新增機票
    cursor.execute("INSERT INTO Flight (fId, fName, dAirport, aAirport, dTime, aTime, amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (new_fId, f_name, d_airport, a_airport, d_time, a_time, amount))
    conn.commit()
    logger.info(f'FLight ID {new_fId} {f_name} added')
    # 返回成功提示或重定向到其他页面
    return redirect('/flight/success')


@app.route('/flight/success')
def flight_success():
    user = session['user']
    username = user['mName']  # 使用者名稱
    logger.info(f"Admin {username}'s update complete")
    return render_template('update_successful.html')


# cancel返回上一頁 並取消原本要購買的機票(已插入資料庫的)
@app.route('/delete_data', methods=['POST'])
def delete_data():
    # 从请求中获取要删除的数据的标识符（例如订单号）
    data = request.get_json()
    oNo = data['oNo']  # 替换为实际的订单号
    conn = create_connection()
    cursor = conn.cursor()
    # 执行删除数据的操作
    cursor.execute("DELETE FROM Ticket WHERE oNo = ?", (oNo,))
    cursor.execute("DELETE FROM Orders WHERE oNo = ?", (oNo,))
    conn.commit()
    conn.close()

    return jsonify(message='Data deleted successfully')


@app.route('/payment/<string:oNo>')
def payment(oNo):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders WHERE oNo = ?", (oNo,))
    payment = cursor.fetchone()
    cursor.execute("SELECT mName FROM Members WHERE mId = ?", (payment.mId,))
    name = cursor.fetchone()
    print(payment)
    logger.info(f'使用者 {name[0]} is Paying')
    # Render the payment page with payment details and barcode
    return render_template('payment.html', payment=payment, bank_account=generate_bank_account())


@app.route('/payment/<string:mId>/thanks')
def thanks(mId):
    print(mId)
    logger.info(f'使用者 {mId} 付款成功')

    return render_template('thanks.html')


@app.route('/show_statistics' , methods=['POST'])
def show_statistics():
    statistics = request.form['statisticType']
    conn = create_connection()
    cursor = conn.cursor()
    if statistics == 'search':        
        cursor.execute("SELECT Search.fId, fName, COUNT(Search.fId) FROM Search JOIN Flight ON Search.fId=Flight.fId GROUP BY Search.fId, fName ORDER BY COUNT(Search.fId) DESC")
        a = cursor.fetchall()

        return render_template('s.html', a=a)
    elif statistics == 'today':
        today = date.today()
        print(today)
        start_of_day = datetime.combine(today, time.min)
        end_of_day = datetime.combine(today, time.max)

        cursor.execute("SELECT fId, COUNT(fId) FROM Search WHERE sDate BETWEEN ? AND ? GROUP BY fId ORDER BY COUNT(fId) DESC", (start_of_day, end_of_day))

        a = cursor.fetchall()
        print(a)
        return render_template('s.html', a=a)
    else:
        return statistics


@app.route('/allorders')
def allorders():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Orders JOIN Flight ON Orders.fId=Flight.fId JOIN Members ON Orders.mId=Members.mId')
    orders = cursor.fetchall()
    print(orders)
    return render_template('allorder.html', orders=orders)


@app.route('/admin/<string:oNo>/editorder')
def editorders(oNo):
    return render_template('editorder.html')


@app.route('/admin/editorder/save', methods=['POST'])
def saveeditorders():
    conn = create_connection()
    cursor = conn.cursor()

    oNo = request.form['order-id']
    paymethod = request.form['payment-method']
    amount = request.form['amount']
    status = request.form['status']
    orderdate = request.form['order-date']
    mId = request.form['member-id']
    fId = request.form['flight-id']
    fName = request.form['airline']
    mName = request.form['passenger-name']
    dTime = request.form['departure-date']
    aTime = request.form['arrival-date']
    dAirport = request.form['origin']
    aAirport = request.form['destination']
    seat = request.form['seat-number']

    cursor.execute("UPDATE Orders SET oNo=?, paymethod=?, amount=?, status=?, oDate=?, mId=?, fId=? WHERE oNo=?"
                   , (oNo, paymethod, amount, status, orderdate, mId, fId, oNo))
    cursor.execute("UPDATE Flight SET fId=?, fName=?, dAirport=?, aAirport=?, dTime=?, aTime=?, amount=? WHERE fId=?"
                   , (fId, fName, dAirport, aAirport, dTime, aTime, amount, fId))
    cursor.execute("UPDATE Members SET mId=?, mName=? WHERE mId=?"
                   , (mId, mName, mId))
    cursor.execute("UPDATE Ticket SET seat=? WHERE oNo=?", (seat, oNo))

    conn.commit()
    conn.close()
    logger.info(f"Oreder已更新")
    return render_template('updateorderss.html')


@app.route('/admin/<string:oNo>/deleteorder')
def deleteorders(oNo):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Orders WHERE oNo=?', (oNo,))
    conn.commit()
    conn.close()
    logger.info(f"Oreder已刪除")
    return render_template('updateorderss.html')


@app.route('/logout')
def logout():
    # 從 session 中獲取使用者資訊
    user = session['user']
    username = user['mName']  # 使用者名稱
    logger.info(f'User {username} Log Out')
    # 登出，清除 session 中的使用者資訊
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run()