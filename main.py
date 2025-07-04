from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import psycopg2
import plotly.graph_objs as go
import plotly.io as pio

app = FastAPI()

# Replace with your actual password
DATABASE_URL = "postgres://postgres:1234@db.dhawutoxwtmjepgxhnfu.supabase.co:5432/postgres"

def fetch_data():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute("SELECT product_name, sale_date, amount FROM sales_data ORDER BY sale_date ASC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print("DB Connection Error:", e)
        return []

@app.get("/visualize-sales", response_class=HTMLResponse)
def visualize_sales():
    data = fetch_data()

    if not data:
        return HTMLResponse("<h3>Error fetching data from DB</h3>")

    # Organize by product
    product_map = {}
    for product, sale_date, amount in data:
        if product not in product_map:
            product_map[product] = {'x': [], 'y': []}
        product_map[product]['x'].append(sale_date)
        product_map[product]['y'].append(float(amount))

    fig = go.Figure()
    for product, values in product_map.items():
        fig.add_trace(go.Scatter(
            x=values['x'], y=values['y'],
            mode='lines+markers',
            name=product
        ))

    fig.update_layout(
        title="Sales Amount by Product Over Time",
        xaxis_title="Date",
        yaxis_title="Amount",
        template="plotly_white"
    )

    html = pio.to_html(fig, full_html=False)
    return HTMLResponse(content=html)

@app.get("/ping-db")
def ping_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.close()
        return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "details": str(e)}
