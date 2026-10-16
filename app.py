import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "bank.db"

st.set_page_config(page_title="NovaBank | Banking Suite", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');
:root { --ink:#172033; --muted:#6b7280; --navy:#101b3d; --blue:#4263eb; --mint:#b8f2d5; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(135deg,#f5f7fc 0%,#edf2fb 100%); color:var(--ink); }
.block-container { padding-top:1.4rem; padding-bottom:2.5rem; max-width:1500px; }
[data-testid="stSidebar"] { background:#101b3d; }
[data-testid="stSidebar"] * { color:#eef2ff !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding:8px 10px; border-radius:10px; }
.hero { background:linear-gradient(115deg,#101b3d 0%,#263c80 65%,#4263eb 100%); color:white; border-radius:22px; padding:28px 30px; margin-bottom:20px; box-shadow:0 14px 35px #243b7a20; }
.hero h1 { font-family:Manrope,sans-serif; font-size:30px; margin:0 0 6px 0; color:white; }
.hero p { margin:0; color:#d9e2ff; font-size:14px; }
.metric-card { background:white; border:1px solid #e8ecf5; border-radius:18px; padding:18px 20px; min-height:116px; box-shadow:0 6px 18px #1c2a4a08; }
.metric-label { color:#737d91; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.7px; }
.metric-value { font-family:Manrope,sans-serif; font-size:27px; font-weight:800; color:#172033; margin-top:9px; }
.metric-note { font-size:12px; color:#7b8497; margin-top:4px; }
.section-title { font-family:Manrope,sans-serif; font-size:19px; font-weight:800; margin:18px 0 10px 0; }
.panel { background:white; border:1px solid #e8ecf5; border-radius:18px; padding:18px; }
div[data-testid="stForm"] { background:white; padding:18px; border-radius:16px; border:1px solid #e8ecf5; }
.stButton button, .stFormSubmitButton button { border-radius:10px; font-weight:700; min-height:42px; }
.small-note { color:#748096; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ---------- Database ----------
def connect():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            account_no TEXT UNIQUE NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no TEXT NOT NULL,
            txn_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            balance_after REAL NOT NULL,
            FOREIGN KEY(account_no) REFERENCES customers(account_no)
        );
        """)

def seed_demo_data():
    with connect() as con:
        count = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        if count:
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        people = [
            ("Aarav Sharma","aarav@example.com","9876501201","NB1001001","Savings",84500.00),
            ("Priya Verma","priya@example.com","9876501202","NB1001002","Current",126750.50),
            ("Kabir Singh","kabir@example.com","9876501203","NB1001003","Savings",42500.00),
            ("Meera Patel","meera@example.com","9876501204","NB1001004","Salary",97320.00),
            ("Ishaan Gupta","ishaan@example.com","9876501205","NB1001005","Savings",15890.75),
            ("Ananya Rao","ananya@example.com","9876501206","NB1001006","Current",211000.00),
            ("Rohan Das","rohan@example.com","9876501207","NB1001007","Salary",63420.25),
            ("Sana Khan","sana@example.com","9876501208","NB1001008","Savings",28750.00),
        ]
        for name,email,phone,acc,typ,balance in people:
            con.execute("""INSERT INTO customers(full_name,email,phone,account_no,account_type,balance,status,created_at)
                         VALUES(?,?,?,?,?,?,?,?)""",(name,email,phone,acc,typ,balance,"Active",now))
            con.execute("""INSERT INTO transactions(account_no,txn_type,amount,description,created_at,balance_after)
                         VALUES(?,?,?,?,?,?)""",(acc,"Credit",balance,"Opening demo balance",now,balance))
        # A few illustrative transactions for a richer demo timeline.
        samples = [
            ("NB1001001","Debit",1250,"Grocery purchase", "2026-10-14 18:20:00",83250),
            ("NB1001002","Credit",15000,"Client payment", "2026-10-14 15:05:00",126750.50),
            ("NB1001003","Debit",500,"Mobile recharge", "2026-10-13 10:42:00",42000),
            ("NB1001004","Credit",42000,"Monthly salary", "2026-10-12 09:15:00",97320),
            ("NB1001005","Debit",999,"Online subscription", "2026-10-11 21:10:00",14891.75),
            ("NB1001006","Debit",2500,"Office supplies", "2026-10-10 13:30:00",211000),
        ]
        for acc,typ,amount,desc,ts,bal in samples:
            con.execute("""INSERT INTO transactions(account_no,txn_type,amount,description,created_at,balance_after)
                         VALUES(?,?,?,?,?,?)""",(acc,typ,amount,desc,ts,bal))

init_db()
seed_demo_data()

def query_df(sql, params=()):
    with connect() as con:
        return pd.read_sql_query(sql, con, params=params)

def money(value):
    return f"₹{float(value):,.2f}"

def all_accounts():
    return query_df("SELECT * FROM customers ORDER BY id DESC")

def get_customer(account_no):
    with connect() as con:
        return con.execute("SELECT * FROM customers WHERE account_no=?",(account_no,)).fetchone()

def add_transaction(account_no, txn_type, amount, description):
    amount = round(float(amount), 2)
    if amount <= 0:
        return False, "Amount must be greater than ₹0."
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        customer = con.execute("SELECT * FROM customers WHERE account_no=?",(account_no,)).fetchone()
        if not customer:
            return False, "Account not found."
        if customer["status"] != "Active":
            return False, "This account is inactive. Transactions are blocked."
        balance = float(customer["balance"])
        if txn_type == "Debit" and amount > balance:
            return False, "Insufficient balance. Transaction cancelled."
        new_balance = balance + amount if txn_type == "Credit" else balance - amount
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con.execute("UPDATE customers SET balance=? WHERE account_no=?",(new_balance,account_no))
        con.execute("""INSERT INTO transactions(account_no,txn_type,amount,description,created_at,balance_after)
                     VALUES(?,?,?,?,?,?)""",(account_no,txn_type,amount,description.strip() or txn_type,now,new_balance))
    return True, f"{txn_type} successful. New balance: {money(new_balance)}"

def create_customer(name,email,phone,account_type,opening):
    with connect() as con:
        last = con.execute("SELECT COALESCE(MAX(id),0)+1 FROM customers").fetchone()[0]
        account_no = f"NB{1001000+last}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            con.execute("""INSERT INTO customers(full_name,email,phone,account_no,account_type,balance,status,created_at)
                         VALUES(?,?,?,?,?,?,?,?)""",(name.strip(),email.strip().lower(),phone.strip(),account_no,account_type,float(opening),"Active",now))
            if opening > 0:
                con.execute("""INSERT INTO transactions(account_no,txn_type,amount,description,created_at,balance_after)
                             VALUES(?,?,?,?,?,?)""",(account_no,"Credit",float(opening),"Opening deposit",now,float(opening)))
        except sqlite3.IntegrityError:
            return False, "That email is already registered. Use a different email."
    return True, f"Account created successfully. Account number: {account_no}"

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🏦 NovaBank")
    st.caption("BANKING MANAGEMENT SUITE")
    st.divider()
    page = st.radio("WORKSPACE", ["Overview", "Customers & Accounts", "Transactions", "Transfer Funds", "Open Account", "Reports", "About"], label_visibility="visible")
    st.divider()
    st.markdown("**Demo environment**")
    st.caption("Local SQLite database · Sample data")
    st.caption("No real money or bank network is connected.")
    if st.button("↻ Refresh data", use_container_width=True):
        st.rerun()

# ---------- Header ----------
st.markdown(f"""
<div class="hero">
  <h1>Banking, made clearer.</h1>
  <p>NovaBank Management Suite &nbsp;·&nbsp; Securely organized demo banking operations</p>
</div>
""", unsafe_allow_html=True)

customers = all_accounts()
transactions = query_df("SELECT * FROM transactions ORDER BY created_at DESC, id DESC")
total_balance = customers["balance"].sum() if not customers.empty else 0
active_count = int((customers["status"] == "Active").sum()) if not customers.empty else 0
txn_volume = transactions["amount"].sum() if not transactions.empty else 0

def metric(label, value, note):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

def page_title(title, subtitle):
    st.markdown(f"## {title}")
    st.caption(subtitle)

if page == "Overview":
    page_title("Executive overview", "A live snapshot of the demo bank's accounts, balances, and transaction activity.")
    cols = st.columns(4)
    with cols[0]: metric("Total deposits", money(total_balance), "Combined customer balances")
    with cols[1]: metric("Customers", f"{len(customers):,}", "Registered accounts")
    with cols[2]: metric("Active accounts", f"{active_count:,}", "Currently eligible for transactions")
    with cols[3]: metric("Transaction volume", money(txn_volume), f"{len(transactions):,} recorded entries")
    left, right = st.columns([1.35,1])
    with left:
        st.markdown('<div class="section-title">Balance by account type</div>', unsafe_allow_html=True)
        if not customers.empty:
            by_type = customers.groupby("account_type", as_index=False)["balance"].sum()
            st.bar_chart(by_type.set_index("account_type"), y="balance", color="#4263eb")
        else:
            st.info("No accounts yet.")
    with right:
        st.markdown('<div class="section-title">Customer balance mix</div>', unsafe_allow_html=True)
        if not customers.empty:
            by_customer = customers[["full_name","balance"]].sort_values("balance", ascending=False).head(6).set_index("full_name")
            st.bar_chart(by_customer, color="#2bbf9f")
    st.markdown('<div class="section-title">Recent activity</div>', unsafe_allow_html=True)
    if transactions.empty:
        st.info("No transactions recorded.")
    else:
        recent = transactions.head(8).copy()
        recent["amount"] = recent["amount"].map(money)
        recent["balance_after"] = recent["balance_after"].map(money)
        recent = recent.rename(columns={"account_no":"Account","txn_type":"Type","amount":"Amount","description":"Description","created_at":"Date & time","balance_after":"Balance after"})
        st.dataframe(recent[["Account","Type","Amount","Description","Date & time","Balance after"]], use_container_width=True, hide_index=True)

elif page == "Customers & Accounts":
    page_title("Customers & accounts", "Search customers and review account status, account type, and available balance.")
    search = st.text_input("Search by name, email, phone, or account number", placeholder="e.g. Aarav or NB1001001")
    filtered = customers.copy()
    if search:
        mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]
    display = filtered[["account_no","full_name","email","phone","account_type","balance","status","created_at"]].copy()
    display["balance"] = display["balance"].map(money)
    display = display.rename(columns={"account_no":"Account number","full_name":"Customer","email":"Email","phone":"Phone","account_type":"Account type","balance":"Balance","status":"Status","created_at":"Created"})
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.markdown('<div class="section-title">Account details</div>', unsafe_allow_html=True)
    if not customers.empty:
        chosen = st.selectbox("Choose an account", customers["account_no"].tolist(), format_func=lambda x: f"{x} — {customers.loc[customers.account_no==x,'full_name'].iloc[0]}")
        customer = get_customer(chosen)
        a,b,c = st.columns(3)
        with a: metric("Customer", customer["full_name"], customer["email"])
        with b: metric("Available balance", money(customer["balance"]), customer["account_type"]+" account")
        with c: metric("Account status", customer["status"], "Transaction eligibility")
        if st.button("Deactivate account" if customer["status"] == "Active" else "Reactivate account", type="secondary"):
            new_status = "Inactive" if customer["status"] == "Active" else "Active"
            with connect() as con:
                con.execute("UPDATE customers SET status=? WHERE account_no=?",(new_status,chosen))
            st.success(f"Account status changed to {new_status}.")
            st.rerun()

elif page == "Transactions":
    page_title("Transaction center", "Post deposits and withdrawals with balance validation and an auditable ledger.")
    accounts = customers["account_no"].tolist()
    with st.form("transaction_form"):
        acc = st.selectbox("Customer account", accounts, format_func=lambda x: f"{x} — {customers.loc[customers.account_no==x,'full_name'].iloc[0]}")
        kind = st.radio("Transaction type", ["Credit (Deposit)","Debit (Withdrawal)"], horizontal=True)
        amount = st.number_input("Amount (₹)", min_value=1.0, value=1000.0, step=100.0)
        description = st.text_input("Description", placeholder="e.g. Cash deposit")
        submitted = st.form_submit_button("Submit transaction", use_container_width=True)
    if submitted:
        ok,msg = add_transaction(acc, "Credit" if kind.startswith("Credit") else "Debit", amount, description)
        (st.success if ok else st.error)(msg)
    st.markdown('<div class="section-title">Full transaction ledger</div>', unsafe_allow_html=True)
    f1,f2 = st.columns(2)
    with f1: type_filter = st.selectbox("Filter by type",["All","Credit","Debit"])
    with f2: account_filter = st.selectbox("Filter by account",["All"]+accounts)
    ledger = query_df("SELECT * FROM transactions ORDER BY created_at DESC, id DESC")
    if type_filter != "All": ledger = ledger[ledger["txn_type"] == type_filter]
    if account_filter != "All": ledger = ledger[ledger["account_no"] == account_filter]
    ledger["amount"] = ledger["amount"].map(money)
    ledger["balance_after"] = ledger["balance_after"].map(money)
    ledger = ledger.rename(columns={"account_no":"Account","txn_type":"Type","amount":"Amount","description":"Description","created_at":"Date & time","balance_after":"Balance after"})
    st.dataframe(ledger[["id","Account","Type","Amount","Description","Date & time","Balance after"]], use_container_width=True, hide_index=True)

elif page == "Transfer Funds":
    page_title("Transfer funds", "Move funds between two active demo accounts. Both ledger entries are recorded together.")
    accounts = customers["account_no"].tolist()
    with st.form("transfer_form"):
        source = st.selectbox("From account", accounts, format_func=lambda x: f"{x} — {customers.loc[customers.account_no==x,'full_name'].iloc[0]}")
        destination_options = [x for x in accounts if x != source]
        destination = st.selectbox("To account", destination_options, format_func=lambda x: f"{x} — {customers.loc[customers.account_no==x,'full_name'].iloc[0]}")
        amount = st.number_input("Transfer amount (₹)", min_value=1.0, value=500.0, step=100.0)
        note = st.text_input("Transfer note", value="Internal account transfer")
        submitted = st.form_submit_button("Review & transfer", use_container_width=True)
    if submitted:
        with connect() as con:
            con.execute("BEGIN IMMEDIATE")
            src = con.execute("SELECT * FROM customers WHERE account_no=?",(source,)).fetchone()
            dst = con.execute("SELECT * FROM customers WHERE account_no=?",(destination,)).fetchone()
            if source == destination:
                st.error("Choose two different accounts.")
            elif not src or not dst:
                st.error("One of the selected accounts was not found.")
            elif src["status"] != "Active" or dst["status"] != "Active":
                st.error("Both accounts must be active.")
            elif amount <= 0 or amount > src["balance"]:
                st.error("Invalid amount or insufficient source balance.")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                src_bal = round(float(src["balance"])-amount,2)
                dst_bal = round(float(dst["balance"])+amount,2)
                con.execute("UPDATE customers SET balance=? WHERE account_no=?",(src_bal,source))
                con.execute("UPDATE customers SET balance=? WHERE account_no=?",(dst_bal,destination))
                con.execute("INSERT INTO transactions(account_no,txn_type,amount,description,created_at,balance_after) VALUES(?,?,?,?,?,?)",(source,"Debit",amount,f"Transfer to {destination}: {note}",now,src_bal))
                con.execute("INSERT INTO transactions(account_no,txn_type,amount,description,created_at,balance_after) VALUES(?,?,?,?,?,?)",(destination,"Credit",amount,f"Transfer from {source}: {note}",now,dst_bal))
                st.success(f"Transfer complete: {money(amount)} moved from {source} to {destination}.")
                st.rerun()
    st.info("Transfers are atomic in this demo: the debit and credit ledger entries are committed together.")

elif page == "Open Account":
    page_title("Open a new account", "Register a customer and initialize a demo bank account.")
    with st.form("open_account_form"):
        name = st.text_input("Full name")
        email = st.text_input("Email address")
        phone = st.text_input("Phone number")
        account_type = st.selectbox("Account type",["Savings","Current","Salary"])
        opening = st.number_input("Opening deposit (₹)", min_value=0.0, value=1000.0, step=500.0)
        submitted = st.form_submit_button("Create account", use_container_width=True)
    if submitted:
        if not name.strip() or not email.strip() or not phone.strip():
            st.error("Please complete all customer fields.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.error("Enter a valid email address.")
        elif len(phone.strip()) < 10:
            st.error("Enter a valid phone number (at least 10 characters).")
        else:
            ok,msg = create_customer(name,email,phone,account_type,opening)
            (st.success if ok else st.error)(msg)
            if ok: st.rerun()

elif page == "Reports":
    page_title("Reports & analytics", "Explore account distribution and transaction trends from the local sample database.")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Account type distribution</div>', unsafe_allow_html=True)
        if not customers.empty:
            st.bar_chart(customers["account_type"].value_counts(), color="#4263eb")
    with c2:
        st.markdown('<div class="section-title">Credits vs debits</div>', unsafe_allow_html=True)
        if not transactions.empty:
            summary = transactions.groupby("txn_type")["amount"].sum().reindex(["Credit","Debit"]).fillna(0)
            st.bar_chart(summary, color="#2bbf9f")
    st.markdown('<div class="section-title">Transaction history by date</div>', unsafe_allow_html=True)
    if not transactions.empty:
        transactions["date"] = pd.to_datetime(transactions["created_at"], errors="coerce").dt.date.astype(str)
        daily = transactions.groupby(["date","txn_type"],as_index=False)["amount"].sum()
        pivot = daily.pivot(index="date",columns="txn_type",values="amount").fillna(0)
        st.line_chart(pivot)
    st.download_button("⬇ Download customer report (CSV)", customers.to_csv(index=False).encode("utf-8"), "novabank_customers.csv", "text/csv")
    st.download_button("⬇ Download transaction ledger (CSV)", transactions.to_csv(index=False).encode("utf-8"), "novabank_transactions.csv", "text/csv")

else:
    page_title("About NovaBank", "A learning project demonstrating common banking-management workflows.")
    st.markdown("""
    <div class="panel">
    <h3>Included modules</h3>
    <ul>
      <li>Dashboard with key metrics and charts</li>
      <li>Customer and account management</li>
      <li>Account creation and opening deposit</li>
      <li>Credit/debit transactions with balance validation</li>
      <li>Internal transfers with paired ledger entries</li>
      <li>Transaction history, filters, reports, and CSV exports</li>
      <li>SQLite persistence: data remains after restarting the app</li>
    </ul>
    <p><b>Important:</b> This is an educational demo, not production banking software. It does not connect to real banks and is not suitable for holding real money or sensitive customer data. Production systems require authentication, role-based authorization, encryption, audit controls, regulatory compliance, backups, monitoring, and independent security review.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="small-note">NovaBank Demo Suite · Built with Python, Streamlit, Pandas, and SQLite · Sample data only</div>', unsafe_allow_html=True)
