from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey , Table
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pandas as pd
import os

database_url = os.getenv("DATABASE_URL", "postgresql://postgres:12345678@localhost:5432/project")

engine = create_engine(database_url)


df = pd.read_csv('data_final.csv')



Base = declarative_base()

class AnnonceEquipement(Base):
    __tablename__ = 'annonce_equipement'
    id = Column(Integer, primary_key=True, autoincrement=True)
    annonce_id = Column(Integer, ForeignKey('annonces.id'), nullable=False)
    equipement_id = Column(Integer, ForeignKey('equipements.id'), nullable=False)
    annonce = relationship("Annonce", back_populates="annonce_equipements")
    equipement = relationship("Equipement", back_populates="annonce_equipements")

class Ville(Base):
    __tablename__ = 'villes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    annonces = relationship("Annonce", back_populates="ville")

class Equipement(Base):
    __tablename__ = 'equipements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    annonce_equipements = relationship("AnnonceEquipement", back_populates="equipement")

class Annonce(Base):
    __tablename__ = 'annonces'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    price = Column(String, nullable=True)  
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    nb_rooms = Column(Integer, nullable=True)
    nb_baths = Column(Integer, nullable=True)
    surface_area = Column(Float, nullable=True)
    link = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey('villes.id'), nullable=False)
    ville = relationship("Ville", back_populates="annonces")
    annonce_equipements = relationship("AnnonceEquipement", back_populates="annonce")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def get_or_create_ville(localisation):
    ville = session.query(Ville).filter_by(name=localisation).first()
    if not ville:
        ville = Ville(name=localisation)
        session.add(ville)
        session.commit()
    return ville

# Helper function to get or create an Equipement entry
def get_or_create_equipement(name):
    equipement = session.query(Equipement).filter_by(name=name).first()
    if not equipement:
        equipement = Equipement(name=name)
        session.add(equipement)
        session.commit()
    return equipement

# Map equipment columns in CSV to Equipement names
equipement_columns = ['Ascenseur', 'Balcon', 'Chauffage', 'Climatisation', 'Concierge',
                      'Cuisine equipee', 'Duplex', 'Meuble', 'Parking', 'Securite', 'Terrasse']

# Loop over rows in the DataFrame to populate tables
for a,row in df.iterrows():
    # Step 1: Create or get the Ville
    ville = get_or_create_ville(row['Localisation'])

    # Step 2: Create the Annonce entry
    annonce = Annonce(
        title=row['Title'],
        price=row['Price'] if pd.notnull(row['Price']) else "PRIX NON SPÉCIFIÉ",
        datetime=datetime.strptime(row['Date'], '%Y-%m-%d'),
        nb_rooms=row['Chambre'] if pd.notnull(row['Chambre']) else None,
        nb_baths=row['Salle de bain'] if pd.notnull(row['Salle de bain']) else None,
        surface_area=row['Surface habitable'] if pd.notnull(row['Surface habitable']) else None,
        link=row['EquipementURL'],
        ville=ville
    )
    session.add(annonce)
    session.commit()

    # Step 3: Check equipment columns and create entries in Equipement and AnnonceEquipement
    for equip_col in equipement_columns:
        if row[equip_col] == True:  # Check if the equipment is marked as present
            equipement = get_or_create_equipement(equip_col)

            # Create association in AnnonceEquipement
            annonce_equipement = AnnonceEquipement(annonce_id=annonce.id, equipement_id=equipement.id)
            session.add(annonce_equipement)

    # Commit after each row
    session.commit()

# Close the session
session.close()


