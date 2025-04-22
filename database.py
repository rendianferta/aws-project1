import mysql.connector

class SQL: 
    def __init__(self):
        self.connect_SQL()

    def connect_SQL(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Yeet_mydatabase2"
            )

            if not self.conn.is_connected():
                print("Failed to connect")
                return None, None
            
            self.cursor = self.conn.cursor()
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS cars_db")
            self.conn.database = 'cars_db'

            if self.is_created():
                return 
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Account (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nama VARCHAR(100) NOT NULL,
                    email VARCHAR(200) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(10) NOT NULL
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Car (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    type VARCHAR(200) NOT NULL,
                    capacity INT NOT NULL,
                    steering VARCHAR(10) NOT NULL,
                    gasoline INT NOT NULL,
                    price INT NOT NULL,
                    status VARCHAR(10) NOT NULL,
                    description TEXT NOT NULL,
                    image VARCHAR(100) NOT NULL
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Booking (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    car_id INT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    total_cost DECIMAL(10,2) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES Account(id) ON DELETE CASCADE,
                    FOREIGN KEY (car_id) REFERENCES Car(id) ON DELETE CASCADE
                )
            """)

            self.cursor.execute(r"""
            INSERT INTO Account (nama, email, password, role) VALUES
                    ('Albern', 'member1@gmail.com', 'aaaa', 'member'),
                    ('Naftali', 'admin1@gmail.com', 'aaaa', 'admin'),
                    ('Filbert', 'admin2@gmail.com', 'aaaa', 'admin');
            """)

            self.cursor.execute(r"""
                INSERT INTO Car (name, type, capacity, steering, gasoline, price, status, description, image) VALUES
                    ("Toyota Camry", "Sedan", 5, "Auto", 50, 100, "Available", "A comfortable midsize sedan with a smooth ride.", "car1"),
                    ("Honda CR-V", "SUV", 7, "Auto", 60, 120, "Available", "A reliable SUV with spacious seating and fuel efficiency.", "car2"),
                    ("Tesla Model 3", "Sedan", 5, "Auto", 0, 150, "Available", "An electric car with cutting-edge autopilot features.", "car3"),
                    ("Ford Mustang", "Sports", 4, "Manual", 45, 200, "Available", "A high-performance sports car with powerful acceleration.", "car4"),
                    ("Chevrolet Tahoe", "SUV", 8, "Auto", 70, 180, "Available", "A full-size SUV with a rugged build and off-road capability.", "car5"),
                    ("BMW X5", "Luxury SUV", 5, "Auto", 65, 250, "Available", "A premium SUV with high-tech features and luxury comfort.", "car6"),
                    ("Mercedes-Benz C-Class", "Luxury Sedan", 5, "Auto", 55, 220, "Available", "A luxury sedan offering style, comfort, and performance.", "car7"),
                    ("Hyundai Tucson", "SUV", 5, "Auto", 50, 110, "Available", "A practical SUV with good fuel economy and safety features.", "car8"),
                    ("Nissan Altima", "Sedan", 5, "Auto", 48, 95, "Available", "A dependable midsize sedan with excellent fuel efficiency.", "car9"),
                    ("Jeep Wrangler", "Off-Road", 5, "Manual", 75, 170, "Available", "A rugged off-road vehicle built for adventure and durability.", "car10");
            """)  

            self.conn.commit()
        
        except mysql.connector.Error as e:
            print(f"Error: {e}")
        finally:
            pass

    def search_all(self, table):
        self.cursor.execute(f"SELECT * FROM {table}")
        return self.cursor.fetchall()
    
    def search(self, query, column, table):
        self.cursor.execute(f"SELECT * FROM {table} WHERE {column} = %s", (query,))
        return self.cursor.fetchall()
    
    def search_like(self, query, column, table):
        self.cursor.execute(f"SELECT * FROM {table} WHERE {column} LIKE %s", (f"%{query}%",))
        return self.cursor.fetchall()

    def select_id(self, id, table):
        self.cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (id,))
        return self.cursor.fetchall()

    def register(self, nama, email, password, role):
        self.cursor.execute("""
        INSERT INTO Account(nama, email, password, role) VALUES (%s, %s, %s, %s)
        """, (nama, email, password, role))
        self.conn.commit()

    def book(   self, user_id, car_id, start_date, end_date, total_cost, status):
        self.cursor.execute("""
        INSERT INTO Booking(user_id, car_id, start_date, end_date, total_cost, status) VALUES 
        (%s, %s, %s, %s, %s, %s)
        """, (user_id, car_id, start_date, end_date, total_cost, status))
        self.conn.commit()
    
    def update_status(self, table, id, column, value):
        self.cursor.execute(f"""
            UPDATE {table} 
            SET {column} = %s
            WHERE id = %s
        """, (value, id))
        self.conn.commit()

    def is_created(self):
        self.cursor.execute("SHOW TABLES")
        return len(self.cursor.fetchall()) != 0
