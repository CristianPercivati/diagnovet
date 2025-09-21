from sqlalchemy import Column, Integer, String, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pacientes(Base):
    __tablename__ = 'pacientes'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=False)
    tutor = Column(String(100), index=True, nullable=False)
    edad = Column(String(50), nullable=False)
    raza = Column(String(50), nullable=False)
    # Relaciones
    informes = relationship("Informes", back_populates="paciente")

class Veterinarios(Base):
    __tablename__ = 'veterinarios'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=False)
    apellido = Column(String(100), index=True, nullable=False)
    matricula = Column(Integer, index=True)
    
    # Relaciones
    informes = relationship("Informes", back_populates="veterinario")
    users = relationship("Users", back_populates="veterinario")

class Informes(Base):
    __tablename__ = 'informes'
    
    id = Column(Integer, primary_key=True, index=True)
    antecedentes = Column(String(1000))
    diagnostico = Column(String(2000), nullable=False)
    img_folder = Column(String(200))
    fecha = Column(Date, nullable=False)
    fk_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    fk_referido = Column(Integer, ForeignKey('veterinarios.id'), nullable=False)
    
    # Relaciones
    paciente = relationship("Pacientes", back_populates="informes")
    veterinario = relationship("Veterinarios", back_populates="informes")
    estudios = relationship("Estudios", back_populates="informe", cascade="all, delete-orphan")

class Tipos_Estudios(Base):
    __tablename__ = 'tipos_estudios'
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_estudio = Column(String(100), unique=True, nullable=False)
    
    # Relaciones
    estudios = relationship("Estudios", back_populates="tipo_estudio")

class Estudios(Base):
    __tablename__ = 'estudios'
    
    id = Column(Integer, primary_key=True, index=True)
    fk_informe = Column(Integer, ForeignKey('informes.id'), nullable=False)
    fk_tipos_estudios = Column(Integer, ForeignKey('tipos_estudios.id'), nullable=False)
    
    # Relaciones
    informe = relationship("Informes", back_populates="estudios")
    tipo_estudio = relationship("Tipos_Estudios", back_populates="estudios")
    mediciones = relationship("Mediciones", back_populates="estudio", cascade="all, delete-orphan")
    observaciones = relationship("Observaciones", back_populates="estudio", cascade="all, delete-orphan")

class Organos(Base):
    __tablename__ = 'organos'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    
    # Relaciones
    mediciones = relationship("Mediciones", back_populates="organo")
    observaciones = relationship("Observaciones", back_populates="organo")

class Unidades(Base):
    __tablename__ = 'unidades'
    
    id = Column(Integer, primary_key=True, index=True)
    unidad = Column(String(50), unique=True, nullable=False)
    
    # Relaciones
    mediciones = relationship("Mediciones", back_populates="unidad")

class Medidas(Base):
    __tablename__ = 'medidas'
    
    id = Column(Integer, primary_key=True, index=True)
    medida = Column(String(100), unique=True, nullable=False)
    
    # Relaciones
    mediciones = relationship("Mediciones", back_populates="medida")

class Mediciones(Base):
    __tablename__ = 'mediciones'
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_medicion = Column(String(100), nullable=False)
    valor = Column(String(50), nullable=False)
    fk_organo = Column(Integer, ForeignKey('organos.id'), nullable=False)
    fk_medida = Column(Integer, ForeignKey('medidas.id'), nullable=False)
    fk_unidad = Column(Integer, ForeignKey('unidades.id'))
    fk_estudio = Column(Integer, ForeignKey('estudios.id'), nullable=False)
    
    # Relaciones
    organo = relationship("Organos", back_populates="mediciones")
    medida = relationship("Medidas", back_populates="mediciones")
    unidad = relationship("Unidades", back_populates="mediciones")
    estudio = relationship("Estudios", back_populates="mediciones")

class Observaciones(Base):
    __tablename__ = 'observaciones'
    
    id = Column(Integer, primary_key=True, index=True)
    observacion = Column(String(1000), nullable=False)
    fk_organo = Column(Integer, ForeignKey('organos.id'), nullable=False)
    fk_estudio = Column(Integer, ForeignKey('estudios.id'), nullable=False)
    
    # Relaciones
    organo = relationship("Organos", back_populates="observaciones")
    estudio = relationship("Estudios", back_populates="observaciones")

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    fk_vet = Column(Integer, ForeignKey('veterinarios.id'))
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False)
    photo_url = Column(String(300))
    role = Column(String(50), default="user")
    
    # Relaciones
    veterinario = relationship("Veterinarios", back_populates="users")