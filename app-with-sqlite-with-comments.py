from flask import Flask, render_template, request # Flask web uygulama çerçevesini kullanabilmek için gerekli olan Flask modüllerini içe aktarır.
from flask_sqlalchemy import SQLAlchemy # SQLAlchemy kütüphanesini kullanarak veritabanı işlemleri yapabilmek için gerekli olan SQLAlchemy modülünü içe aktarır.
from sqlalchemy import text #  SQLAlchemy ile SQL sorgularını çalıştırmak için gerekli olan text işlevini içe aktarır.
app = Flask(__name__) #Bu satır, Flask uygulamasını oluşturur. __name__ değişkeni, uygulamanın ana modülünü temsil eder.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./email.db' # SQLAlchemy ile kullanılacak olan veritabanının URI'sini belirtir. SQLite veritabanını kullanır ve email.db adında bir veritabanı dosyasını işaret eder.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # SQLAlchemy'nin otomatik olarak veritabanı değişikliklerini takip etmesini devre dışı bırakır. Bu, bazı durumlarda performansı artırabilir.
db = SQLAlchemy(app) # Bu satır, SQLAlchemy ile veritabanı işlemleri yapmak için bir SQLAlchemy veritabanı bağlantısını oluşturur. db nesnesi, veritabanı işlemlerini gerçekleştirmek için kullanılır.


with app.app_context(): # with ifadesi bir bağlam yöneticisi başlatır. Bu, belirli bir bağlam içinde kodun çalıştırılmasını sağlar. Flask uygulamaları, request-response döngüsü içinde çalışır ve bu nedenle bazı işlemler doğru bağlam içinde gerçekleştirilmelidir.
    drop_table = text('DROP TABLE IF EXISTS users;') # "users" adlı tabloyu varsa silen bir SQL sorgusunu oluşturur. Eğer "users" tablosu zaten varsa, bu satır tabloyu silecektir.
    users_table = text(""" 
    CREATE TABLE users(
    username VARCHAR NOT NULL PRIMARY KEY,
    email VARCHAR);
    """) # "users" adlı yeni bir SQL tablosu oluşturan bir SQL sorgusunu oluşturur. Tablo iki sütundan oluşur: "username" (kullanıcı adı) ve "email" (e-posta adresi). "username" sütunu, PRIMARY KEY olarak işaretlenmiş, yani benzersiz ve boş bırakılamaz.
    data = text("""
    INSERT INTO users
    VALUES
        ("dora", "dora@amazon.com"),
        ("cansın", "cansın@google.com"),
        ("sencer", "sencer@bmw.com"),
        ("uras", "uras@mercedes.com"),
	    ("ares", "ares@porche.com");
        """) #Bu satır, "users" tablosuna eklemek için kullanılacak örnek verileri içeren bir SQL sorgusunu oluşturur. İçeriği kısaca şu şekildedir: Tabloya beş kullanıcı ekleniyor, her biri bir kullanıcı adı ve e-posta adresi içeriyor.
    db.session.execute(drop_table) # Bu satır, drop_table değişkenindeki SQL sorgusunu veritabanına uygular. Bu sorgu, "users" tablosunu varsa siler.
    db.session.execute(users_table) # Bu satır, users_table değişkenindeki SQL sorgusunu veritabanına uygular. Bu sorgu, "users" tablosunu oluşturur.
    db.session.execute(data) # Bu satır, data değişkenindeki SQL sorgusunu veritabanına uygular. Bu sorgu, örnek kullanıcı verilerini "users" tablosuna ekler.
    db.session.commit() # Bu satır, yaptığınız tüm değişiklikleri veritabanına kaydeder (commit işlemi). Yani, tabloya yeni veriler ekler, değişiklikleri kalıcı hale getirir.

def find_emails(keyword): # find_emails fonksiyonu, keyword adında bir parametre alır, bu parametre ile aranan anahtar kelimeyi temsil eder.
    with app.app_context(): # bir Flask uygulama bağlamı oluşturulur. Bu bağlam, veritabanı işlemleri için gerekli olan bağlamı sağlar.
        query = text(f"""   
        SELECT * FROM users WHERE username like '%{keyword}%'; 
        """) # query adında bir SQL sorgusu oluşturulur. Bu sorgu, users adlı tablodan username sütununda belirtilen anahtar kelimeyi içeren kullanıcıları seçer. %{keyword}% ifadesi, LIKE operatörünü kullanarak username sütununda belirtilen anahtar kelimeyi içeren kullanıcıları bulur. % işaretleri, anahtar kelimenin başka karakterlerle çevrili olabileceğini belirtir.
        result = db.session.execute(query) # sorgu çalıştırılır ve sonuç (result) elde edilir.
        user_emails = [(row[0], row[1]) for row in result] # sorgunun sonucunda bulunan kullanıcıların kullanıcı adları ve e-posta adreslerini içeren bir liste oluşturur. Her bir kullanıcı adı ve e-posta adresi, bir tuple olarak user_emails listesine eklenir.
        if not any(user_emails):
            user_emails = [("Not Found", "Not Found")] # eğer user_emails listesi boşsa (yani hiçbir kullanıcı bulunamadıysa), "Not Found" kullanıcı adı ve e-posta adresini içeren bir tuple oluşturulur ve bu tuple, user_emails listesine eklenir.
        return user_emails # user_emails listesi sonuç olarak döndürülür. Bu liste, eşleşen kullanıcıların bilgilerini veya "Not Found" mesajını içerebilir.

def insert_email(name,email): # Bu kod bir kullanıcının adını ve e-posta adresini alır ve bu bilgileri bir SQLite veritabanında saklar.
    with app.app_context(): # Bu kod bloğu, Flask uygulama bağlamı içinde çalıştırılmak üzere tasarlanmıştır. Bu bağlam içinde veritabanı işlemleri gerçekleştirilir.
        query = text(f"""
        SELECT * FROM users WHERE username like '{name}'
        """) # Girilen name (kullanıcı adı) değerine göre veritabanında bir SQL sorgusu oluşturur. Bu sorgu, veritabanında aynı kullanıcı adıyla kayıtlı başka bir kullanıcının olup olmadığını kontrol eder.
        result = db.session.execute(query) # Oluşturulan SQL sorgusunu veritabanında çalıştırır ve sonucu result değişkenine atar
        response = '' # İşlem başarılı veya hataliysa, response değişkeni uygun bir mesajla doldurulur ve sonucun kullanıcıya iletilmesine yardımcı olur.
        if len(name) == 0 or len(email) == 0: # Girilen kullanıcı adı veya e-posta adresi boşsa, hata mesajı ('Username or email can not be empty!!') döner.
            response = 'Username or email can not be empty!!' 
        elif not any(result):  # SQL sorgusu sonucu herhangi bir kullanıcı dönmezse (yani kullanıcı veritabanında bulunmuyorsa), yeni bir kullanıcı eklemek için bir SQL sorgusu oluşturur ve çalıştırır.
            insert = text(f"""
            INSERT INTO users
            VALUES ('{name}', '{email}');
            """)
            result = db.session.execute(insert)
            db.session.commit()
            response = text(f"User {name} and {email} have been added successfully")
        else: # Yukarıdaki koşullar sağlanmazsa (yani kullanıcı veritabanında zaten varsa), kullanıcıya "User {name} already exists" şeklinde bir hata mesajı döner.
            response = text(f"User {name} already exist")
        return response # İşlem sonucuna bağlı olarak bir yanıt döner. Yanıt, işlemin başarılı olup olmadığını veya hata durumlarını içerir.


@app.route('/', methods=['GET', 'POST']) # Bu route (yol) ana sayfayı temsil eder. Ana sayfa URL'si (/) ile ilişkilendirilmiştir. HTTP GET ve POST istekleri kabul edilir.
def emails(): # emails() işlevi, bu yolu işler.
    with app.app_context(): # , Flask uygulama bağlamı içinde çalıştırılır.
        if request.method == 'POST': # şartı, sayfa bir POST isteği ile yüklendiğinde çalışır. Bu, kullanıcının bir arama sorgusu gönderdiğini ve e-postaları aradığını gösterir.
            user_app_name = request.form['user_keyword']
            user_emails = find_emails(user_app_name) # Kullanıcının arama sorgusu (user_app_name) alınır ve bu sorgu ile eşleşen e-postaları find_emails() işlevi kullanılarak bulunur.
            return render_template('emails.html', name_emails=user_emails, keyword=user_app_name,   show_result=True) # Sonuçlar bir HTML şablonu olan 'emails.html' ile birlikte render_template() kullanılarak gösterilir. name_emails ve keyword gibi değişkenler, şablon içinde kullanılır 
        else: # eğer sayfa bir POST isteği ile yüklenmemişse (yani sadece URL'ye gitmişse), sonuçları göstermek için show_result değeri False olarak ayarlanır.
            return render_template('emails.html', show_result=False)


@app.route('/add', methods=['GET', 'POST']) # Bu route, e-posta eklemek için kullanılır ve /add URL'si ile ilişkilendirilir,  HTTP GET ve POST istekleri kabul edilir.
def add_email(): # add_email() işlevi, bu yolu işler.
    with app.app_context(): # bloğu, Flask uygulama bağlamı içinde çalıştırılır.
        if request.method == 'POST': # şartı, kullanıcının bir e-posta eklemek için bir form gönderdiğini kontrol eder.
            user_app_name = request.form['username'] # Kullanıcının girdiği kullanıcı adı (user_app_name) alınır.
            user_app_email = request.form['useremail'] # Kullanıcının girdiği e-posta (user_app_email) alınır.
            result_app = insert_email(user_app_name, user_app_email) #  bu bilgiler veritabanına eklenir ve sonuç (result_app) elde edilir.
            return render_template('add-email.html', result_html=result_app, show_result=True) # Sonuçlar bir HTML şablonu olan 'add-email.html' ile birlikte render_template() kullanılarak gösterilir.
        else:
            return render_template('add-email.html', show_result=False) # Eğer sayfa bir POST isteği ile yüklenmemişse (yani sadece URL'ye gitmişse), sonuçları göstermek için show_result değeri False olarak ayarlanır.


# - Add a statement to run the Flask application which can be reached from any host on port 80.
if __name__=='__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=8080)

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/