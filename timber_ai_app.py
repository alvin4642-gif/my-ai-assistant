import streamlit as st
import math
import re

st.set_page_config(layout="wide")
st.title("🪵 Timber AI Assistant V8")

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

colA, colB = st.columns(2)
generate = colA.button("🚀 Generate")
refresh = colB.button("🔄 Refresh")

if refresh:
    st.rerun()

# =========================
# PLYWOOD PRICE
# =========================
plywood_prices = {
    "furniture": {3:16, 6:17, 9:19, 12:24, 15:27, 18:32, 25:52},
    "marine": {6:27, 9:37, 12:45, 15:57, 18:68, 25:96},
    "mr": {3:4.5, 6:9.9, 9:15, 12:21.5, 15:28, 18:31}
}

# =========================
# FUNCTIONS
# =========================
def mm_to_inch(mm):
    if 18 <= mm <= 25: return 1
    if 40 <= mm <= 50: return 2
    if 60 <= mm <= 75: return 3
    if 90 <= mm <= 100: return 4
    if 140 <= mm <= 150: return 6
    if 190 <= mm <= 205: return 8
    if 290 <= mm <= 305: return 12
    
    # fallback (CRITICAL FIX)
    val = round(mm / 25.4)
    return max(val, 1)  # NEVER allow 0

def std_length(ft):
    if ft == 19:
        return 20
    return max(ft, 1)  # NEVER allow 0

def calc(thk, wid, length, rate):
    # SAFETY CHECK (CRITICAL)
    if thk == 0 or wid == 0 or length == 0:
        return 0, 0

    pcs = math.floor(7200 / thk / wid / length)

    if pcs <= 0:
        return 0, 0

    price = round(rate / pcs)
    return pcs, price

# =========================
# MAIN
# =========================
if generate:

    lines = user_input.split("\n")
    current = None

    timber_data = {}
    reply_lines = []
    total = 0
    has_timber = False

    for line in lines:
        text = line.lower().strip()
        if not text:
            continue

        # detect species
        if "kapur" in text:
            current = ("Kapur", kapur_rate)
        elif "balau" in text:
            current = ("Balau", balau_rate)
        elif "chengal" in text:
            current = ("Chengal", chengal_rate)

        qty_match = re.findall(r'(\d+)\s*pcs', text)
        qty = int(qty_match[0]) if qty_match else 1

        size_match = re.findall(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', text)

        # ================= TIMBER =================
        if size_match and current:

            has_timber = True

            mm1 = int(size_match[0][0])
            mm2 = int(size_match[0][1])
            ft = int(size_match[0][2])

            thk = mm_to_inch(mm1)
            wid = mm_to_inch(mm2)
            length = std_length(ft)

            pcs, price = calc(thk, wid, length, current[1])

            if pcs == 0:
                reply_lines.append(f"{current[0]} timber size error → check input")
                continue

            line_total = price * qty
            total += line_total

            timber_data.setdefault(current[0], []).append([
                f"{mm1} x {mm2} x {ft}ft",
                f"{thk}x{wid}x{length}",
                current[1],
                pcs,
                price,
                qty,
                line_total
            ])

            reply_lines.append(f"{current[0]} timber (planed)")
            reply_lines.append(f"{mm1}mm x {mm2}mm x {ft}ft @ ${price}/pcs x {qty} = ${line_total}\n")

        # ================= PLYWOOD =================
        if "plywood" in text:

            if "marine" in text:
                grade = "marine"
            elif "mr" in text or "floor" in text:
                grade = "mr"
            else:
                grade = "furniture"

            thk_match = re.findall(r'(\d+\.?\d*)mm', text)

            for t in thk_match:
                t = float(t)
                if t in [5, 5.5]:
                    t = 6
                t = int(t)

                if t in plywood_prices[grade]:

                    price = plywood_prices[grade][t]
                    line_total = price * qty
                    total += line_total

                    if grade == "mr" and t == 3 and qty < 10:
                        reply_lines.append(f"MR plywood {t}mm @ ${price}/pcs (MOQ 10pcs)")
                        reply_lines.append("⚠ MOQ not met\n")
                    else:
                        reply_lines.append(f"{grade.upper()} plywood {t}mm @ ${price}/pcs x {qty} = ${line_total}")

                    timber_data.setdefault("Plywood", []).append([
                        f"{t}mm",
                        grade,
                        "-",
                        "-",
                        price,
                        qty,
                        line_total
                    ])

    # ================= OUTPUT =================
    st.subheader("🧠 Internal View")
    for k, v in timber_data.items():
        st.markdown(f"### {k}")
        st.table([["Input", "Std", "$/ton", "pcs/ton", "$/pcs", "Qty", "Total"]] + v)

    st.subheader("📩 Customer Reply")

    reply_lines.append(f"\nTotal: ${total}\n")

    if has_timber:
        reply_lines.append("tolerance +-1~2mm")
        reply_lines.append("tolerance length +-25~50mm\n")

    reply_lines.append("Delivery / Self Collection:")
    reply_lines.append("30 Krani Loop (Blk A) #04-05")
    reply_lines.append("TimMac @ Kranji S739570")
    reply_lines.append("Self collect: 9:30–11am / 1:30–4pm")
    reply_lines.append("Closed Sat, Sun & PH")

    final_reply = "\n".join(reply_lines)

    st.text_area("Reply", final_reply, height=300)
    st.download_button("📋 Copy", final_reply)
