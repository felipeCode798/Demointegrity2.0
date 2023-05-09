import psycopg2


class UserConnection():
    def __init__(self):
        try:
            self.db = psycopg2.connect("dbname=INTEGRITY user=postgres password=1234 host=localhost port=5432")
        except psycopg2.OperationalError as err:
            print("Error: ", err)
            self.conn.close()


    #---------------------------------------------------------------------------------#
    #--------------- User CRUD -------------------------------------------------------#
    #---------------------------------------------------------------------------------#

    def info_user(self, data):
        with self.db.cursor() as cur:
            cur.execute("SELECT MAX(user_id) FROM users")
            result = cur.fetchone()
            next_id = result[0] + 1 if result[0] else 1  # Si no hay registros, empezar en 1
            data['user_id'] = next_id
            cur.execute("INSERT INTO users (user_id,name,dni,id_ciudad,phone,email,address,photo) VALUES (%(user_id)s, %(name)s, %(dni)s, %(id_ciudad)s, %(phone)s, %(email)s, %(address)s, %(photo)s)", data)
            self.db.commit()

    def read_users(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM users")
            data = cur.fetchall()
            return data
    
    def read_user(self, user_id):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            data = cur.fetchone()
            return data
        
    #---------------------------------------------------------------------------------#
    #--------------- City CRUD -------------------------------------------------------#
    #---------------------------------------------------------------------------------#
    
    def read_city(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM cities")
            data = cur.fetchall()
            return data

    #---------------------------------------------------------------------------------#
    #--------------- Ivestigator CRUD ------------------------------------------------#
    #---------------------------------------------------------------------------------#

    def insert_investigator(self, data):
        with self.db.cursor() as cur:
            cur.execute("SELECT MAX(inv_id) FROM investigator")
            result = cur.fetchone()
            next_id = result[0] + 1 if result[0] else 1  # Si no hay registros, empezar en 1
            data['inv_id'] = next_id
            cur.execute("INSERT INTO investigator (inv_id, name, dni) VALUES (%(inv_id)s,%(name)s, %(dni)s)", data)
            self.db.commit()
    
    def read_investigator(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM investigator")
            data = cur.fetchall()
            return data
    
    def read_investigator_id(self, inv_id):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM investigator WHERE inv_id = %s", (inv_id,))
            data = cur.fetchone()
            return data
    
    def update_investigator(self, data):
        with self.db.cursor() as cur:
            cur.execute("UPDATE investigator SET name = %(name)s, dni = %(dni)s WHERE inv_id = %(inv_id)s", data)
            self.db.commit()
    
    def delete_investigator(self, inv_id):
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM investigator WHERE inv_id = %s", (inv_id,))
            self.db.commit()

    #---------------------------------------------------------------------------------#
    #--------------- Documentos CRUD -------------------------------------------------#
    #---------------------------------------------------------------------------------#

    def info_documents(self, data):
        with self.db.cursor() as cur:
            cur.execute("SELECT MAX(id_document) FROM documents")
            result = cur.fetchone()
            next_id = result[0] + 1 if result[0] else 1  # Si no hay registros, empezar en 1
            data['id_document'] = next_id
            cur.execute("INSERT INTO documents (id_document,id_user,id_product,id_service,id_city,id_investigator,value,document) VALUES (%(id_document)s,%(id_user)s, %(id_product)s, %(id_service)s, %(id_city)s, %(id_investigator)s, %(value)s, %(document)s)", data)
            self.db.commit()
    
    def read_documents(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM documents")
            data = cur.fetchall()
            return data
    
    def read_documents_id(self, id_document):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM documents WHERE id_document = %s", (id_document,))
            data = cur.fetchone()
            return data
    
    def update_documents_info(self, data):
        with self.db.cursor() as cur:
            cur.execute("UPDATE documents SET id_user = %(id_user)s, id_product = %(id_product)s, id_service = %(id_service)s, id_city = %(id_city)s, id_investigator = %(id_investigator)s, value = %(value)s, document = %(document)s WHERE id_document = %(id_document)s", data)
            self.db.commit()

    def update_documents(self, data):
        with self.db.cursor() as cur:
            cur.execute("UPDATE documents SET creator = %(creator)s, autor = %(autor)s, producer = %(produccer)s, title = %(title)s WHERE id_document = %(id_document)s", data)
            self.db.commit()

    
    def delete_documents(self, id_document):
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM documents WHERE id_document = %s", (id_document,))
            self.db.commit()
    
    #---------------------------------------------------------------------------------#
    #--------------- Consulta Id -----------------------------------------------------#
    #---------------------------------------------------------------------------------#

    def consulta_id(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT MAX(id_document) FROM public.documents")
            data = cur.fetchone()
            data = data[0]
            return data

    def status(self, data):
        with self.db.cursor() as cur:
            status =data['status']
            data['status'] = status
            cur.execute("UPDATE documents SET status = %(status)s WHERE id_document = %(id_document)s", data)
            self.db.commit()
    
    def consulta_id_apocrifo(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT MAX(id_apocrifo) FROM public.apocrypha")
            data = cur.fetchone()
            data = data[0]
            return data

    def next_id_apocrifo(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT MAX(id_apocrifo) FROM public.apocrypha")
            data = cur.fetchone()
            if data[0] is None:
                data = 1
            else:
                data = data[0] 
                data = data + 1
            return data

    #---------------------------------------------------------------------------------#
    #--------------- Autor Consulta --------------------------------------------------#
    #---------------------------------------------------------------------------------#

    def consulta_autor(self, autor):
        with self.db.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM apocrypha WHERE autor = %s", (autor,))
            data = cur.fetchone()
            data = data[0]
            return data

    #---------------------------------------------------------------------------------#
    #--------------- Apocrifo CRUD ---------------------------------------------------#
    #---------------------------------------------------------------------------------#

    def info_apocrifo(self, data):
        with self.db.cursor() as cur:
            cur.execute("SELECT MAX(id_apocrifo) FROM apocrypha")
            result = cur.fetchone()
            next_id = result[0] + 1 if result[0] else 1  # Si no hay registros, empezar en 1
            data['id_apocrifo'] = next_id
            cur.execute("INSERT INTO apocrypha (id_apocrifo,creator,autor,producer,name,phone,dni) VALUES (%(id_apocrifo)s,%(creator)s, %(autor)s, %(producer)s, %(name)s, %(phone)s, %(dni)s)", data)
            self.db.commit()

    def read_apocrifo(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM apocrypha")
            data = cur.fetchall()
            return data
        
    def read_apocrifo_id(self, id_apocrifo):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM apocrypha WHERE id_apocrifo = %s", (id_apocrifo,))
            data = cur.fetchone()
            return data
        
    def delete_apocrifo(self, id_apocrifo):
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM apocrypha WHERE id_apocrifo = %s", (id_apocrifo,))
            self.db.commit()

    #---------------------------------------------------------------------------------#
    #--------------- Creator y Producer Consulta -------------------------------------#
    #---------------------------------------------------------------------------------#

    def consulta_creator(self, creator):
        with self.db.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM listblack WHERE creator = %s", (creator,))
            data = cur.fetchone()
            data = data[0]
            return data

    def consulta_producer(self, producer):
        with self.db.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM listblack WHERE producer = %s", (producer,))
            data = cur.fetchone()
            data = data[0]
            return data

    #---------------------------------------------------------------------------------#
    #--------------- Producto Servivio CRUD ------------------------------------------#
    #---------------------------------------------------------------------------------#

    def info_productoservice(self, data):
        with self.db.cursor() as cur:
            cur.execute("SELECT MAX(id_productsevices) FROM productsevices")
            result = cur.fetchone()
            next_id = result[0] + 1 if result[0] else 1  # Si no hay registros, empezar en 1
            data['id_productsevices'] = next_id
            cur.execute("INSERT INTO productsevices (id_productsevices,name,id_type,report_date) VALUES (%(id_productsevices)s,%(name)s, %(id_type)s, %(report_date)s)", data)
            self.db.commit()

    def read_productoservice(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM productsevices")
            data = cur.fetchall()
            return data
    
    def read_productoservice_id(self, id_productsevices):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM productsevices WHERE id_productsevices = %s", (id_productsevices,))
            data = cur.fetchone()
            return data
    
    def delete_productoservice(self, id_productsevices):
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM productsevices WHERE id_productsevices = %s", (id_productsevices,))
            self.db.commit()
            
    def get_document(self, id_document):
        with self.db.cursor() as cur:
            cur.execute("SELECT document FROM documents WHERE id_document = %s", (id_document,))
            data = cur.fetchone()
            return data
        
    #---------------------------------------------------------------------------------#
    #--------------- LOG DE CASOS  ---------------------------------------------------#
    #---------------------------------------------------------------------------------#

    def log_casos(self, data):
        with self.db.cursor() as cur:
            cur.execute("SELECT MAX(id_log) FROM log_casos")
            result = cur.fetchone()
            next_id = result[0] + 1 if result[0] else 1  # Si no hay registros, empezar en 1
            data['id_log'] = next_id
            cur.execute("INSERT INTO log_casos (id_log,name,dni,title,log_caso) VALUES (%(id_log)s, %(name)s,%(dni)s, %(newName)s, %(log_caso)s)", data)
            self.db.commit()

    def read_log_casos(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM log_casos")
            data = cur.fetchall()
            return data
        
    def read_log_casos_id(self, id_log):
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM log_casos WHERE id_log = %s", (id_log,))
            data = cur.fetchone()
            return data

    # Contar todos los log_casos
    def count_log_casos(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM log_casos")
            data = cur.fetchone()
            data = data[0]
            return data

    def __def__(self):
        self.db.close()