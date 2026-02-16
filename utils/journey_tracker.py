import streamlit.components.v1 as components


ORDER_FLOW = [
    ("Ordered", "🛍"),
    ("Shipped", "📦"),
    ("Delivered", "✅"),
    ("Returned", "↩"),
    ("Claim Submitted", "📝"),
    ("Claim Approved", "👍"),
    ("Refund Completed", "💰")
]


def show_journey_tracker(current_status):

    labels = [x[0] for x in ORDER_FLOW]

    try:
        current_index = labels.index(current_status)
    except ValueError:
        current_index = 0

    progress_width = (current_index) / (len(ORDER_FLOW) - 1) * 100


    html = f"""
<html>

<style>

body {{
    margin: 0;
    font-family: system-ui;
}}

.container {{
    width: 100%;
    padding: 30px 10px 60px 10px;
}}

.line {{
    width: 100%;
    height: 6px;
    background: #e0e0e0;
    position: relative;
    border-radius: 10px;
}}

.progress {{
    height: 6px;
    background: linear-gradient(90deg,#00c853,#64dd17);
    width: {progress_width}%;
    border-radius: 10px;
    transition: width 0.6s ease-in-out;
}}

.steps {{
    display: flex;
    justify-content: space-between;
    position: relative;
    top: -35px;
}}

.step {{
    text-align: center;
    width: 120px;
}}

.circle {{
    width: 65px;
    height: 65px;
    border-radius: 50%;
    background: white;
    border: 4px solid #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    margin: auto;
    transition: all 0.4s ease;
}}

.completed {{
    background: linear-gradient(135deg,#00c853,#64dd17);
    border-color: #00c853;
    color: white;
    transform: scale(1.1);
    box-shadow: 0 0 15px rgba(0,200,83,0.6);
}}

.current {{
    animation: pulse 1.2s infinite;
}}

.label {{
    margin-top: 12px;
    font-size: 14px;
    font-weight: 500;
    color: #ddd;
}}

.completed-label {{
    color: #00e676;
    font-weight: 600;
}}

@keyframes pulse {{

    0% {{
        box-shadow: 0 0 0 0 rgba(0,200,83,0.7);
    }}

    70% {{
        box-shadow: 0 0 0 15px rgba(0,200,83,0);
    }}

    100% {{
        box-shadow: 0 0 0 0 rgba(0,200,83,0);
    }}

}}

</style>


<div class="container">

<div class="line">
<div class="progress"></div>
</div>

<div class="steps">
"""

    for i, (label, icon) in enumerate(ORDER_FLOW):

        circle_class = ""
        label_class = "label"

        if i < current_index:
            circle_class = "completed"
            label_class = "label completed-label"

        elif i == current_index:
            circle_class = "completed current"
            label_class = "label completed-label"

        html += f"""

<div class="step">

<div class="circle {circle_class}">
{icon}
</div>

<div class="{label_class}">
{label}
</div>

</div>

"""

    html += """
</div>
</div>

</html>
"""

    components.html(html, height=200)
