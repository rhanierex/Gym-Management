from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(20), unique=True, nullable=False)
    tanggal_daftar = db.Column(db.DateTime, nullable=False, default=datetime.now)
    tanggal_expire = db.Column(db.DateTime, nullable=False)
    type_member = db.Column(db.String(50), nullable=False)
    biaya_bulanan = db.Column(db.Float, nullable=False)
    biaya_pendaftaran = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    jenis_kelamin = db.Column(db.String(20), nullable=False)
    pekerjaan = db.Column(db.String(100), nullable=False)
    no_handphone = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'<Member {self.member_id} - {self.nama}>'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Attendance(db.Model):
    """Model untuk menyimpan history check-in/check-out member"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(20), db.ForeignKey('members.member_id'), nullable=False)
    check_in = db.Column(db.DateTime, nullable=False, default=datetime.now)
    check_out = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='check_in')  # check_in, check_out
    
    # Relationship
    member = db.relationship('Member', backref=db.backref('attendances', lazy=True))
    
    def __repr__(self):
        return f'<Attendance {self.member_id} - {self.check_in}>'
