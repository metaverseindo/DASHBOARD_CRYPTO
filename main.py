# --- DATA PROCESSING ---
with st.spinner("Menarik data dari blockchain..."):
    data = fetch_crypto_data(exchange_choice)

# Cek apakah data berhasil ditarik
if len(data) > 0:
    df = pd.DataFrame(data)
    df = df.sort_values("Volume", ascending=False).reset_index(drop=True)

    # --- TOP 3 METRICS ---
    top_symbols = ["BTC", "ETH", "SOL"]
    m_cols = st.columns(3)
    
    for i, sym in enumerate(top_symbols):
        row = df[df['Koin'] == sym]
        if not row.empty:
            price = row.iloc['Harga']
            change = row.iloc['Change']
            m_cols[i].metric(label=f"{sym}/USDT", value=f"${price:,.2f}", delta=f"{change:+.2f}%")

    st.markdown("---")

    # --- MAIN CONTENT: CHART & TABLE ---
    col_table, col_chart = st.columns()

    with col_table:
        st.subheader("📊 Market Overview")
        search = st.text_input("🔍 Cari Koin (Contoh: XRP, DOGE)", "").upper()
        
        if search:
            df_display = df[df['Koin'].str.contains(search)]
        else:
            df_display = df.head(50)

        def color_change(val):
            color = '#deff9a' if val >= 0 else '#ff4b4b'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df_display.style.format({
                "Harga": "${:,.4f}",
                "Change": "{:+.2f}%",
                "Volume": "${:,.0f}"
            }).map(color_change, subset=["Change"]),
            use_container_width=True,
            height=450,
            hide_index=True
        )

    with col_chart:
        st.subheader("🔥 Top Volume (Visual)")
        top_10 = df.head(10)
        fig = go.Figure(go.Bar(
            x=top_10['Volume'],
            y=top_10['Koin'],
            orientation='h',
            marker=dict(color='#deff9a')
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=450,
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')} | Total Pairs: {len(df)}")

else:
    # SEKARANG SUDAH RAPI: Menjorok ke dalam blok else
    st.warning("Menunggu data dari Exchange... Pastikan koneksi internet stabil.")

# --- AUTO REFRESH ---
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()
