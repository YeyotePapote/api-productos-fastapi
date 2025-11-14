from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3

app = FastAPI()

# -------------------- BASE DE DATOS --------------------
def conectar():
    return sqlite3.connect("productos.db")

def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

crear_tabla()

# -------------------- MODELOS JSON --------------------
class Producto(BaseModel):
    nombre: str
    precio: float
    stock: int

class ProductoOut(Producto):
    id: int

# -------------------- ENDPOINTS CRUD --------------------

# CREATE
@app.post("/productos", response_model=ProductoOut)
def crear_producto(producto: Producto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
        (producto.nombre, producto.precio, producto.stock)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return {**producto.dict(), "id": nuevo_id}

# READ (todos)
@app.get("/productos", response_model=List[ProductoOut])
def obtener_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, precio, stock FROM productos")
    filas = cursor.fetchall()
    conn.close()

    return [
        {"id": fila[0], "nombre": fila[1], "precio": fila[2], "stock": fila[3]}
        for fila in filas
    ]

# READ (uno)
@app.get("/productos/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, precio, stock FROM productos WHERE id = ?", (producto_id,))
    fila = cursor.fetchone()
    conn.close()

    if fila is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {"id": fila[0], "nombre": fila[1], "precio": fila[2], "stock": fila[3]}

# UPDATE
@app.put("/productos/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, producto: Producto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE id = ?",
        (producto.nombre, producto.precio, producto.stock, producto_id)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    conn.close()
    return {**producto.dict(), "id": producto_id}

# DELETE
@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    conn.close()
    return {"mensaje": "Producto eliminado correctamente"}
