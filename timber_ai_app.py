import streamlit as st
import math
import re

# =========================
# PAGE SETUP
# =========================
st.set_page_config(layout="wide")

st.markdown("""
<style>
textarea, input {
    font-size: 18px !important;
}
table {
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🪵 Timber AI Assistant V7")

# =========================
# INPUT
# =========================
user_input = st.text_area("📥 Customer Enquiry", height=200)

col1, col2, col3 = st.columns(3)
with col1:
    balau_rate = st.number_input("Balau $/ton", value=5500)
with col2:
    kapur_rate = st.number_input("Kapur $/ton", value=3800)
with col3:
    chengal_rate = st.number_input("Chengal $/ton", value=6000)

# =========================
# BUTTONS
# =========================
colA, colB = st.columns(2)

with colA:
    generate = st.button("🚀 Generate")

with colB:
    refresh = st.button("🔄 Refresh")

if refresh:
    st.rerun()

# =========================
# PRICE LIST
# =========================
plywood_prices = {
    "furniture": {3:16, 6:17, 9:19, 12:24, 15:27, 18:32, 25:52},
    "marine": {6:27, 9:37, 12:45, 15:57, 18:68, 25:96},
    "mr": {3:4.5, 6:9.9, 9:15, 12:21.5, 15:28, 18:31}
}

# =========================
# HELPERS
# =========================
def mm_to_inch(mm):
    if 93 <= mm <= 95: return 4
    if 143 <= mm <= 145: return 6
    if 193 <= mm <= 195: return 8
    if 43 <= mm <= 45: return 2
    if 65 <= mm <= 75: return 3
    if 293 <= mm <= 295: return 12
    if 18 <= mm <= 25: return 1
    return round(mm / 25.4)

def standard_length(ft):
    return 20 if ft == 19 else ft

def calc(thk, wid, length, rate):
    pcs_per_ton = math.floor(7200 / thk / wid / length)
    if pcs_per_ton <= 0:
        return 0, 0
    price = round(rate / pcs_per_ton)
    return pcs_per_ton, price

def color_pcs(pcs):
    if pcs < 10:
        return "🔴"
    elif pcs < 50:
        return "🟡"
    else:
        return "🟢"

# =========================
# MAIN
# =========================
if generate:

    lines = user_input.split("\n")
    current_species = None

    timber_data = {}
    customer_lines = []
    total_value = 0
    has_timber = False

    for line in lines:
        line_clean = line.strip().lower()
        if not line_clean:
            continue

        # Detect species
        if "kapur" in line_clean:
            current_species = "Kapur"
            rate = kapur_rate
        elif "balau" in line_clean:
            current_species = "Balau"
            rate = balau_rate
        elif "chengal" in line_clean:
            current_species = "Chengal"
            rate = chengal_rate

        # Extract qty
        qty_match = re.findall(r'(\d+)\s*pcs', line_clean)
        qty = int(qty_match[0]) if qty_match else 1

        # =========================
        # TIMBER LOGIC
        # =========================
        match = re.findall(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', line_clean)

        if match and current_species:

            has_timber = True

            mm1 = int(match[0][0])
            mm2 = int(match[0][1])
            length = int(match[0][2])

            thk = mm_to_inch(mm1)
            wid = mm_to_inch(mm2)
            length_std = standard_length(length)

            pcs_per_ton, price = calc(thk, wid, length_std, rate)

            line_total = price * qty
            total_value += line_total

            timber_data.setdefault(current_species, []).append([
                f"{mm1} x {mm2} x {length}ft",
                f"{thk}x{wid}x{length_std}",
                rate,
                f"{color_pcs(pcs_per_ton)} {pcs_per_ton}",
                price,
                qty,
                line_total
            ])

            customer_lines.append(f"{current_species} timber (planed)")
            customer_lines.append(f"{mm1}mm x {mm2}mm x {length}ft @ ${price}/pcs x {qty} = ${line_total}\n")

        # =========================
        # PLYWOOD LOGIC
        # =========================
        if "plywood" in line_clean:

            if "marine" in line_clean:
                grade = "marine"
            elif "mr" in line_clean or "floor" in line_clean:
                grade = "mr"
            else:
                grade = "furniture"

            thickness_match = re.findall(r'(\d+\.?\d*)mm', line_clean)

            for t in thickness_match:
                t = float(t)

                if t in [5, 5.5]:
                    t = 6

                t = int(t)

                if t in plywood_prices[grade]:

                    price = plywood_prices[grade][t]
                    line_total = price * qty
                    total_value += line_total

                    # MOQ warning
                    if grade == "mr" and t == 3 and qty < 10:
                        customer_lines.append(f"MR plywood {t}mm @ ${price}/pcs (MOQ 10pcs) x {qty} = ${line_total}")
                        customer_lines.append("⚠ MOQ not met (minimum 10pcs)\n")
                    else:
                        customer_lines.append(f"{grade.upper()} plywood {t}mm @ ${price}/pcs x {qty} = ${line_total}")

                    timber_data.setdefault("Plywood", []).append([
                        f"{t}mm",
                        grade.upper(),
                        "-",
                        "-",
                        price,
                        qty,
                        line_total
                    ])

    # =========================
    # INTERNAL VIEW
    # =========================
    st.subheader("🧠 Internal View")

    for species, items in timber_data.items():
        st.markdown(f"### {species}")
        st.table(
            [["Input (mm)", "Std", "$/ton", "pcs/ton", "$/pcs", "Qty", "Total $"]]
            + items
        )

    # =========================
    # CUSTOMER VIEW
    # =========================
    st.subheader("📩 Customer Reply")

    customer_lines.append(f"\nTotal: ${total_value}\n")

    # Timber disclaimer
    if has_timber:
        customer_lines.append("tolerance +-1~2mm")
        customer_lines.append("tolerance length +-25~50mm\n")

    customer_lines.append("Delivery / Self Collection:")
    customer_lines.append("30 Krani Loop (Blk A) #04-05")
    customer_lines.append("TimMac @ Kranji S739570")
    customer_lines.append("Self collect: 9:30–11am / 1:30–4pm")
    customer_lines.append("Closed Sat, Sun & PH")

    reply = "\n".join(customer_lines)

    st.text_area("Reply (Copy)", reply, height=300)
    st.download_button("📋 Copy", reply)