import streamlit as st
import pandas as pd
from io import StringIO

# ==========================================================
# CẤU HÌNH TRANG
# ==========================================================

st.set_page_config(
    page_title="Loan Calculator",
    page_icon="🏦",
    layout="wide"
)

# ==========================================================
# CSS GIAO DIỆN
# ==========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fb;
}

.main-title {
    text-align: center;
    font-size: 38px;
    font-weight: 800;
    color: #174a7e;
    margin-bottom: 5px;
}

.sub-title {
    text-align: center;
    color: #666;
    font-size: 17px;
    margin-bottom: 25px;
}

.card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

.result-box {
    background-color: #eaf4ff;
    padding: 20px;
    border-radius: 15px;
    border-left: 5px solid #1769aa;
}

.big-number {
    font-size: 25px;
    font-weight: bold;
    color: #1769aa;
}

.footer {
    text-align: center;
    color: #777;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HÀM ĐỊNH DẠNG TIỀN
# ==========================================================

def format_money(value):
    return f"{value:,.0f}".replace(",", ".") + " đ"


# ==========================================================
# HÀM TÍNH GỐC ĐỀU - LÃI GIẢM DẦN
# ==========================================================

def calculate_equal_principal(loan, months, annual_rate):

    monthly_rate = annual_rate / 100 / 12

    principal_month = loan / months

    data = []

    remaining = loan

    total_interest = 0

    for month in range(1, months + 1):

        interest = remaining * monthly_rate

        payment = principal_month + interest

        remaining_after = remaining - principal_month

        if remaining_after < 0:
            remaining_after = 0

        total_interest += interest

        data.append({
            "Tháng": month,
            "Dư nợ đầu kỳ": remaining,
            "Gốc phải trả": principal_month,
            "Lãi phải trả": interest,
            "Tổng thanh toán": payment,
            "Dư nợ cuối kỳ": remaining_after
        })

        remaining = remaining_after

    return pd.DataFrame(data), total_interest


# ==========================================================
# HÀM TÍNH TRẢ GÓP ĐỀU
# ==========================================================

def calculate_annuity(loan, months, annual_rate):

    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        payment = loan / months
    else:
        payment = (
            loan
            * monthly_rate
            * (1 + monthly_rate) ** months
            / ((1 + monthly_rate) ** months - 1)
        )

    data = []

    remaining = loan

    total_interest = 0

    for month in range(1, months + 1):

        interest = remaining * monthly_rate

        principal = payment - interest

        if month == months:
            principal = remaining
            payment_actual = principal + interest
        else:
            payment_actual = payment

        remaining_after = remaining - principal

        if remaining_after < 0:
            remaining_after = 0

        total_interest += interest

        data.append({
            "Tháng": month,
            "Dư nợ đầu kỳ": remaining,
            "Gốc phải trả": principal,
            "Lãi phải trả": interest,
            "Tổng thanh toán": payment_actual,
            "Dư nợ cuối kỳ": remaining_after
        })

        remaining = remaining_after

    return pd.DataFrame(data), total_interest


# ==========================================================
# TIÊU ĐỀ
# ==========================================================

st.markdown(
    '<div class="main-title">🏦 LOAN CALCULATOR</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Ứng dụng tính gốc và lãi khoản vay ngân hàng'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("🏦 LOAN CALCULATOR")

    st.markdown("---")

    st.markdown("### 📌 Chức năng")

    st.write("💰 Tính khoản vay")
    st.write("📊 Lịch trả nợ")
    st.write("📈 Biểu đồ khoản vay")
    st.write("🧾 Xuất dữ liệu")
    st.write("💡 Tư vấn khoản vay")

    st.markdown("---")

    st.markdown("### 📍 Thông tin")

    st.write("Ứng dụng mô phỏng khoản vay")
    st.write("Phục vụ mục đích học tập")

# ==========================================================
# NHẬP THÔNG TIN KHOẢN VAY
# ==========================================================

st.markdown("## 📝 1. Thông tin khoản vay")

col1, col2 = st.columns(2)

with col1:

    loan = st.number_input(
        "💰 Số tiền vay (VNĐ)",
        min_value=1000000.0,
        max_value=10000000000.0,
        value=100000000.0,
        step=1000000.0
    )

    months = st.number_input(
        "📅 Thời hạn vay (tháng)",
        min_value=1,
        max_value=360,
        value=12,
        step=1
    )

    annual_rate = st.number_input(
        "📈 Lãi suất (%/năm)",
        min_value=0.0,
        max_value=50.0,
        value=10.0,
        step=0.1
    )

with col2:

    purpose = st.selectbox(
        "🎯 Mục đích vay",
        [
            "Vay tiêu dùng",
            "Vay mua nhà",
            "Vay mua ô tô",
            "Vay kinh doanh",
            "Vay học tập",
            "Vay sửa chữa nhà"
        ]
    )

    product = st.selectbox(
        "🏦 Sản phẩm vay",
        [
            "Vay tín chấp",
            "Vay thế chấp",
            "Vay tiêu dùng cá nhân",
            "Vay mua nhà",
            "Vay mua ô tô",
            "Vay kinh doanh"
        ]
    )

    method = st.radio(
        "💳 Phương thức trả nợ",
        [
            "Gốc đều - lãi giảm dần",
            "Trả góp đều hàng tháng"
        ]
    )

# ==========================================================
# NÚT TÍNH
# ==========================================================

calculate = st.button(
    "🧮 TÍNH KHOẢN VAY",
    type="primary",
    use_container_width=True
)

# ==========================================================
# TÍNH TOÁN
# ==========================================================

if calculate:

    if loan <= 0:
        st.error("Số tiền vay phải lớn hơn 0.")

    elif months <= 0:
        st.error("Thời hạn vay phải lớn hơn 0.")

    elif annual_rate < 0:
        st.error("Lãi suất không được âm.")

    else:

        if method == "Gốc đều - lãi giảm dần":

            df, total_interest = calculate_equal_principal(
                loan,
                months,
                annual_rate
            )

        else:

            df, total_interest = calculate_annuity(
                loan,
                months,
                annual_rate
            )

        total_payment = loan + total_interest

        first_payment = df.iloc[0]["Tổng thanh toán"]

        first_principal = df.iloc[0]["Gốc phải trả"]

        first_interest = df.iloc[0]["Lãi phải trả"]

        # Lưu kết quả
        st.session_state["loan_df"] = df
        st.session_state["total_interest"] = total_interest
        st.session_state["total_payment"] = total_payment
        st.session_state["first_payment"] = first_payment
        st.session_state["first_principal"] = first_principal
        st.session_state["first_interest"] = first_interest

        st.success("Đã tính khoản vay thành công!")

# ==========================================================
# HIỂN THỊ KẾT QUẢ
# ==========================================================

if "loan_df" in st.session_state:

    df = st.session_state["loan_df"]

    total_interest = st.session_state["total_interest"]

    total_payment = st.session_state["total_payment"]

    first_payment = st.session_state["first_payment"]

    first_principal = st.session_state["first_principal"]

    first_interest = st.session_state["first_interest"]

    st.markdown("---")

    st.markdown("## 📊 2. Kết quả khoản vay")

    # ======================================================
    # THÔNG TIN CHUNG
    # ======================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Số tiền vay",
            format_money(loan)
        )

    with col2:

        st.metric(
            "📅 Thời hạn",
            f"{months} tháng"
        )

    with col3:

        st.metric(
            "📈 Lãi suất",
            f"{annual_rate:.2f}%/năm"
        )

    with col4:

        st.metric(
            "🎯 Mục đích",
            purpose
        )

    # ======================================================
    # KẾT QUẢ THANH TOÁN
    # ======================================================

    st.markdown("### 💵 Số tiền phải trả")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            f"""
            <div class="result-box">
            <p>Gốc tháng đầu</p>
            <div class="big-number">
            {format_money(first_principal)}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="result-box">
            <p>Lãi tháng đầu</p>
            <div class="big-number">
            {format_money(first_interest)}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="result-box">
            <p>Thanh toán tháng đầu</p>
            <div class="big-number">
            {format_money(first_payment)}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 📌 Tổng kết khoản vay")

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            f"💰 *Tổng tiền lãi:* "
            f"{format_money(total_interest)}"
        )

    with col2:

        st.success(
            f"💵 *Tổng tiền phải trả:* "
            f"{format_money(total_payment)}"
        )

    # ======================================================
    # THÔNG TIN SẢN PHẨM
    # ======================================================

    st.markdown("---")

    st.markdown("## 🎯 3. Thông tin khoản vay")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write("*Mục đích vay*")
        st.write(purpose)

    with col2:

        st.write("*Sản phẩm vay*")
        st.write(product)

    with col3:

        st.write("*Phương thức trả nợ*")
        st.write(method)

    # ======================================================
    # BẢNG LỊCH TRẢ NỢ
    # ======================================================

    st.markdown("---")

    st.markdown("## 📋 4. Lịch trả nợ")

    display_df = df.copy()

    for column in [
        "Dư nợ đầu kỳ",
        "Gốc phải trả",
        "Lãi phải trả",
        "Tổng thanh toán",
        "Dư nợ cuối kỳ"
    ]:

        display_df[column] = display_df[column].apply(
            format_money
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # ======================================================
    # BIỂU ĐỒ
    # ======================================================

    st.markdown("---")

    st.markdown("## 📈 5. Biểu đồ khoản vay")

    chart_data = df[
        [
            "Gốc phải trả",
            "Lãi phải trả"
        ]
    ].copy()

    chart_data.index = [
        f"Tháng {i}"
        for i in range(1, len(chart_data) + 1)
    ]

    st.bar_chart(chart_data)

    # ======================================================
    # BIỂU ĐỒ DƯ NỢ
    # ======================================================

    st.markdown("### 📉 Dư nợ còn lại")

    balance_data = df[
        ["Dư nợ cuối kỳ"]
    ].copy()

    balance_data.index = [
        f"Tháng {i}"
        for i in range(1, len(balance_data) + 1)
    ]

    st.line_chart(balance_data)

    # ======================================================
    # TẢI FILE CSV
    # ======================================================

    st.markdown("---")

    st.markdown("## 📥 6. Xuất lịch trả nợ")

    csv_data = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="⬇️ TẢI LỊCH TRẢ NỢ CSV",
        data=csv_data,
        file_name="lich_tra_no.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ======================================================
    # TƯ VẤN
    # ======================================================

    st.markdown("---")

    st.markdown("## 💡 7. Tư vấn khoản vay")

    ratio = total_interest / loan * 100

    if ratio < 10:

        st.success(
            "Khoản lãi dự kiến tương đối thấp so với số tiền vay."
        )

    elif ratio < 25:

        st.warning(
            "Khoản lãi ở mức trung bình. "
            "Bạn nên cân nhắc khả năng thanh toán hàng tháng."
        )

    else:

        st.error(
            "Tổng tiền lãi khá cao so với số tiền vay. "
            "Nên cân nhắc giảm thời hạn hoặc tìm mức lãi suất phù hợp hơn."
        )

    st.info(
        "⚠️ Đây là công cụ mô phỏng phục vụ học tập. "
        "Lãi suất và lịch trả nợ thực tế có thể khác tùy ngân hàng, "
        "hợp đồng và phương thức tính lãi."
    )

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.markdown(
    """
    <div class="footer">
    🏦 LOAN CALCULATOR | Mini App môn Tài chính - Ngân hàng
    <br>
    Công cụ mô phỏng khoản vay phục vụ mục đích học tập
    </div>
    """,
    unsafe_allow_html=True
)
