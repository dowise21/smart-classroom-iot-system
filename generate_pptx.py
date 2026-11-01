import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # Colors
    BG_DARK = RGBColor(11, 15, 25)         # #0b0f19
    CARD_BG = RGBColor(21, 29, 45)         # #151d2d
    CARD_BORDER = RGBColor(40, 56, 85)     # #283855
    ACCENT_BLUE = RGBColor(26, 115, 232)   # #1a73e8
    ACCENT_CYAN = RGBColor(0, 210, 255)    # #00d2ff
    ACCENT_GREEN = RGBColor(40, 167, 69)   # #28a745
    ACCENT_RED = RGBColor(220, 53, 69)     # #dc3545
    ACCENT_AMBER = RGBColor(245, 158, 11)  # #f59e0b
    TEXT_WHITE = RGBColor(255, 255, 255)
    TEXT_MUTED = RGBColor(148, 163, 184)   # Slate 400
    TEXT_BODY = RGBColor(203, 213, 225)    # Slate 300

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background() # no line
        return bg

    def add_header(slide, title_text, category_text, slide_num_str):
        # Header bar
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.9))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN
        p_cat.font.name = "Segoe UI"
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.font.name = "Segoe UI"

        # Badge slide number
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.5), Inches(0.4), Inches(1.0), Inches(0.4))
        badge.fill.solid()
        badge.fill.fore_color.rgb = CARD_BG
        badge.line.color.rgb = ACCENT_BLUE
        badge.line.width = Pt(1)
        tf_b = badge.text_frame
        tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_b = tf_b.paragraphs[0]
        p_b.text = slide_num_str
        p_b.font.size = Pt(11)
        p_b.font.bold = True
        p_b.font.color.rgb = ACCENT_CYAN
        p_b.font.name = "Consolas"
        p_b.alignment = PP_ALIGN.CENTER

    def add_card(slide, left, top, width, height, title, content_list, border_color=CARD_BORDER, bg_color=CARD_BG, title_color=TEXT_WHITE):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_top = Inches(0.2)
        tf.margin_right = Inches(0.25)
        tf.margin_bottom = Inches(0.2)

        if title:
            p_title = tf.paragraphs[0]
            p_title.text = title
            p_title.font.size = Pt(14)
            p_title.font.bold = True
            p_title.font.color.rgb = title_color
            p_title.font.name = "Segoe UI"
            p_title.space_after = Pt(8)

        first = True if not title else False
        for item in content_list:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.text = item
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Segoe UI"
            p.space_after = Pt(4)
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s1)

    # Project Badges
    badge1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.2), Inches(1.3), Inches(4.9), Inches(0.45))
    badge1.fill.solid()
    badge1.fill.fore_color.rgb = RGBColor(26, 40, 65)
    badge1.line.color.rgb = ACCENT_BLUE
    p = badge1.text_frame.paragraphs[0]
    p.text = "ESP8266 ARCHITECTURE  •  FAIL-SAFE AP FALLBACK"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.alignment = PP_ALIGN.CENTER

    # Main Title
    title_box = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(2.0))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "SMART CLASSROOM IoT SYSTEM"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.alignment = PP_ALIGN.CENTER
    
    p2 = tf1.add_paragraph()
    p2.text = "Hệ thống Giám sát An toàn và Tự động hóa Phòng học Thông minh dựa trên Vi điều khiển ESP8266"
    p2.font.size = Pt(18)
    p2.font.color.rgb = ACCENT_CYAN
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(10)

    # Info Card
    add_card(s1, 2.5, 4.3, 8.33, 1.8, "THÔNG TIN HỌC PHẦN & ĐỀ TÀI CAPSTONE", [
        "• Học phần: IOT102 - Capstone Project  |  Học kỳ: Fall 2026",
        "• Vi điều khiển trung tâm: ESP8266 NodeMCU V3 (80/160 MHz)",
        "• Tính năng cốt lõi: Edge Computing, Hardware ISR, WiFi Hotspot Fallback, Cloud Webhook",
        "• Trạng thái hệ thống: Đã triển khai mô hình thực tế và kiểm thử thành công"
    ], border_color=ACCENT_BLUE)

    # =========================================================================
    # SLIDE 2: TEAM MEMBERS
    # =========================================================================
    s2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s2)
    add_header(s2, "Thành Viên Nhóm Thực Hiện Đồ Án", "Project Contributors", "02 / 14")

    members = [
        ("Nguyễn Văn A", "MSSV: SE170001", "FIRMWARE LEAD", ACCENT_BLUE, [
            "• Lập trình Non-blocking millis()",
            "• Ngắt phần cứng PIR ISR (D5)",
            "• Logic Escalation & Cooldown 5p",
            "• Tối ưu bộ nhớ ESP8266 RAM"
        ]),
        ("Trần Thị B", "MSSV: SE170002", "HARDWARE ENGINEER", ACCENT_GREEN, [
            "• Thiết kế sơ đồ nguyên lý Fritzing",
            "• Phân bổ chân Pinout an toàn",
            "• Đấu nối Relay Quạt D0 & Đèn D4",
            "• Tích hợp cụm cảm biến DHT & Gas"
        ]),
        ("Lê Văn C", "MSSV: SE170003", "CLOUD & WEB DEVELOPER", ACCENT_CYAN, [
            "• Xây dựng Web Dashboard Port 80",
            "• Cấu hình Fallback AP 192.168.4.1",
            "• Tích hợp Google Script Webhook",
            "• Thiết kế giao diện HTML Email"
        ]),
        ("Phạm Văn D", "MSSV: SE170004", "QA & DOCUMENTATION", ACCENT_AMBER, [
            "• Thực thi 4 kịch bản Test Cases",
            "• Viết báo cáo kỹ thuật IEEE",
            "• Dựng video demo & tạo mã QR",
            "• Kiểm thử chịu tải ngắt & rớt mạng"
        ])
    ]

    for i, (name, mssv, role, col, tasks) in enumerate(members):
        left = 0.8 + i * 2.95
        add_card(s2, left, 1.8, 2.8, 4.8, f"{name}\n{mssv}", [f"VAI TRÒ: {role}", ""] + tasks, border_color=col, title_color=col)

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT & CONTEXT
    # =========================================================================
    s3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s3)
    add_header(s3, "Bối Cảnh Khách Quan & Vấn Đề Tồn Tại", "Problem Statement", "03 / 14")

    problems = [
        ("01. LÃNG PHÍ ĐIỆN NĂNG QUY MÔ LỚN", ACCENT_RED, [
            "• Thực trạng: Học sinh, sinh viên thường xuyên quên tắt quạt và hệ thống đèn khi rời phòng học.",
            "• Hậu quả: Thiết bị hoạt động lãng phí suốt đêm và 2 ngày cuối tuần.",
            "• Thất thoát tài chính: Hàng chục triệu đồng tiền điện mỗi tháng tại mỗi giảng đường trường học.",
            "• Tác động môi trường: Gia tăng phát thải carbon không cần thiết."
        ]),
        ("02. RỦI RO CHÁY NỔ & RÒ RỈ GAS NGOÀI GIỜ", ACCENT_AMBER, [
            "• Thực trạng: Phòng thí nghiệm, xưởng thực hành chứa nhiều hóa chất, bình gas và thiết bị công suất cao.",
            "• Nguy cơ: Sự cố chập điện do quá tải hoặc rò rỉ khí gas xảy ra ban đêm khi không có bảo vệ trực tiếp.",
            "• Hạn chế: Không có hệ thống phát hiện sớm và cảnh báo tức thì từ xa về điện thoại người quản lý.",
            "• Thiệt hại: Có thể thiêu rụi toàn bộ cơ sở vật chất nếu không phản ứng kịp."
        ]),
        ("03. CÔNG TẮC CƠ TRUYỀN THỐNG BẤT CẬP", ACCENT_BLUE, [
            "• Bị động hoàn toàn: Hoạt động 100% phụ thuộc vào ý thức tự giác của người dùng.",
            "• Không thích ứng ngữ cảnh: Không thể tự bật đèn khi phòng tối hay tự bật quạt khi phòng nóng bức.",
            "• Không có dữ liệu: Ban quản lý nhà trường hoàn toàn không có số liệu về nhiệt độ, chất lượng không khí.",
            "• Thiếu điều khiển tập trung: Muốn tắt phải đến tận nơi bấm từng công tắc vật lý."
        ])
    ]

    for i, (title, col, items) in enumerate(problems):
        add_card(s3, 0.8 + i * 3.95, 1.8, 3.8, 4.8, title, items, border_color=col, title_color=col)

    # =========================================================================
    # SLIDE 4: PRODUCT SOLUTION OVERVIEW
    # =========================================================================
    s4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s4)
    add_header(s4, "Tổng Quan Giải Pháp Smart Classroom IoT", "Product Solution", "04 / 14")

    solutions = [
        ("TỰ ĐỘNG HÓA THÍCH ỨNG (CONTEXT-AWARE)", ACCENT_BLUE, [
            "• Đèn học LED (D4): Tự động bật khi thỏa mãn đồng thời: [Có người (PIR)] VÀ [Phòng tối (LDR)].",
            "• Giữ sáng thông minh (PIR Hold): Duy trì sáng thêm 15 giây sau khi hết chuyển động, chống tắt đột ngột.",
            "• Quạt làm mát (D0): Tự động bật khi nhiệt độ >= 30.0°C, tự tắt khi <= 29.5°C."
        ]),
        ("GIÁM SÁT ĐA CẢM BIẾN THỜI GIAN THỰC", ACCENT_GREEN, [
            "• DHT11: Đo nhiệt độ và độ ẩm không khí chính xác chu kỳ 2 giây.",
            "• MQ135: Đo nồng độ khí Gas, khói độc hại với bộ chuyển đổi ADC 10-bit.",
            "• LCD 1602 I2C: Hiển thị luân phiên thông số môi trường và địa chỉ IP kết nối.",
            "• Kiến trúc Non-blocking: Sử dụng millis() hoàn toàn, không dừng CPU."
        ]),
        ("WEB DASHBOARD & AP FALLBACK AN TOÀN", ACCENT_CYAN, [
            "• Web Server Port 80: Giao diện điều khiển bật/tắt thủ công và hiển thị trực quan.",
            "• Dự phòng AP Fallback: Mất kết nối WiFi trường quá 15 giây -> Tự phát AP 'SmartClassroom_WiFi' (192.168.4.1).",
            "• Tính sẵn sàng 100%: Ban quản trị luôn có thể truy cập mạch dù mạng ngoài bị sập."
        ]),
        ("CẢNH BÁO EMAIL HTML & COOLDOWN 5 PHÚT", ACCENT_RED, [
            "• Google Apps Script Webhook: Gửi email cảnh báo định dạng HTML đẹp mắt tức thời.",
            "• Phân cấp leo thang (Escalation): Quá nhiệt chỉ bật quạt (không hú còi), Gas nguy hiểm hú còi tối đa.",
            "• Chống bão thư rác (5-min Cooldown): Chỉ gửi lại mail sau 5 phút nếu sự cố còn tiếp diễn."
        ])
    ]

    for i, (title, col, items) in enumerate(solutions):
        col_idx = i % 2
        row_idx = i // 2
        add_card(s4, 0.8 + col_idx * 5.95, 1.8 + row_idx * 2.5, 5.8, 2.3, title, items, border_color=col, title_color=col)

    # =========================================================================
    # SLIDE 5: TABLE OF CONTENTS (BENTO GRID)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s5)
    add_header(s5, "Mục Lục Cấu Trúc Báo Cáo", "Table of Contents", "05 / 14")

    agenda = [
        ("01", "BỐI CẢNH & GIẢI PHÁP TỔNG THỂ", ACCENT_BLUE, [
            "• Vấn đề lãng phí điện năng & nguy cơ cháy nổ",
            "• 4 trụ cột công nghệ của hệ thống Smart Classroom"
        ]),
        ("02", "HỆ THỐNG PHẦN CỨNG & CẢM BIẾN", ACCENT_GREEN, [
            "• Vai trò & ngưỡng kích hoạt của 4 cảm biến",
            "• Sơ đồ Fritzing & bảng phân bổ chân Pinout chi tiết"
        ]),
        ("03", "SƠ ĐỒ KHỐI & LƯU ĐỒ THUẬT TOÁN", ACCENT_CYAN, [
            "• Sơ đồ khối kỹ thuật chuẩn công nghiệp",
            "• Lưu đồ giải thuật non-blocking & phân cấp cảnh báo"
        ]),
        ("04", "THỰC NGHIỆM & 4 KỊCH BẢN DEMO", ACCENT_AMBER, [
            "• Hình ảnh diorama phòng học thực tế",
            "• Mã QR video YouTube & chi tiết 4 Test Cases"
        ]),
        ("05", "KẾT LUẬN & ĐỊNH HƯỚNG MỞ RỘNG", ACCENT_RED, [
            "• Đánh giá kết quả kiến trúc nhúng đạt được",
            "• 3 Hướng nâng cấp: MQTT Cloud, Camera AI, PZEM-004T"
        ])
    ]

    add_card(s5, 0.8, 1.8, 3.8, 2.3, f"{agenda[0][0]}. {agenda[0][1]}", agenda[0][3], border_color=agenda[0][2], title_color=agenda[0][2])
    add_card(s5, 4.8, 1.8, 3.8, 2.3, f"{agenda[1][0]}. {agenda[1][1]}", agenda[1][3], border_color=agenda[1][2], title_color=agenda[1][2])
    add_card(s5, 8.8, 1.8, 3.8, 2.3, f"{agenda[2][0]}. {agenda[2][1]}", agenda[2][3], border_color=agenda[2][2], title_color=agenda[2][2])
    add_card(s5, 0.8, 4.3, 5.8, 2.3, f"{agenda[3][0]}. {agenda[3][1]}", agenda[3][3], border_color=agenda[3][2], title_color=agenda[3][2])
    add_card(s5, 6.8, 4.3, 5.8, 2.3, f"{agenda[4][0]}. {agenda[4][1]}", agenda[4][3], border_color=agenda[4][2], title_color=agenda[4][2])

    # =========================================================================
    # SLIDE 6: SENSORS & ROLES
    # =========================================================================
    s6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s6)
    add_header(s6, "Chi Tiết Cảm Biến & Ngưỡng Kích Hoạt", "Sensors & Roles", "06 / 14")

    sensors = [
        ("DHT11 - NHIỆT ĐỘ & ĐỘ ẨM", ACCENT_BLUE, [
            "• Chân kết nối: Chân D3 (GPIO0) - Giao thức 1-Wire Digital",
            "• Dải đo: 0 - 50°C (Sai số ±2°C), 20 - 90% RH (Sai số ±5%)",
            "• Ngưỡng Bật Quạt & Cảnh Báo: Nhiệt độ >= 30.0°C",
            "• Ngưỡng Tắt Quạt (Hysteresis): Nhiệt độ <= 29.5°C",
            "• Ý nghĩa: Trễ 0.5°C triệt tiêu hiện tượng rơ-le bật/tắt liên tục gây hỏng động cơ."
        ]),
        ("MQ135 - KHÍ GAS & KHÓI ĐỘC", ACCENT_AMBER, [
            "• Chân kết nối: Chân A0 (ADC 10-bit) - Giá trị 0 đến 1023",
            "• Độ nhạy: Khí NH3, NOx, Alcohol, Benzene, Khói và Gas rò rỉ",
            "• Ngưỡng Hú Còi Báo Động: ADC >= 500",
            "• Ngưỡng Ngắt Báo Động (Hysteresis): ADC <= 450",
            "• Cơ chế: Mức ưu tiên cao nhất, lập tức hú còi ầm ĩ và bật quạt thông gió hết công suất."
        ]),
        ("PIR HC-SR501 - PHÁT HIỆN CHUYỂN ĐỘNG", ACCENT_GREEN, [
            "• Chân kết nối: Chân D5 (GPIO14) - Hardware Interrupt (RISING)",
            "• Nguyên lý: Bức xạ hồng ngoại thụ động từ thân nhiệt người",
            "• Phương thức đọc: attachInterrupt() phản xạ tức thời < 1ms",
            "• Thời gian trễ giữ sáng: PIR_HOLD_TIME = 15.000 ms (15 giây)",
            "• Ý nghĩa: Tránh việc đèn tắt bất ngờ khi sinh viên ngồi yên ghi bài hoặc tập trung học."
        ]),
        ("LDR - CẢM BIẾN QUANG TRỞ ÁNH SÁNG", ACCENT_CYAN, [
            "• Chân kết nối: Chân D6 (GPIO12) - Digital Output (DO)",
            "• Chức năng: Nhận biết môi trường phòng học Tối (HIGH) hay Sáng (LOW)",
            "• Điều kiện bật đèn học: isDark && motionDetected",
            "• Cơ chế tiết kiệm: Trời sáng tự nhiên -> Đèn LUÔN TẮT dù có người",
            "• Ý nghĩa: Triệt tiêu 100% điện năng chiếu sáng lãng phí vào ban ngày."
        ])
    ]

    for i, (title, col, items) in enumerate(sensors):
        col_idx = i % 2
        row_idx = i // 2
        add_card(s6, 0.8 + col_idx * 5.95, 1.8 + row_idx * 2.5, 5.8, 2.3, title, items, border_color=col, title_color=col)

    # =========================================================================
    # SLIDE 7: CIRCUIT DIAGRAM & PINOUT (FRITZING)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s7)
    add_header(s7, "Sơ Đồ Đấu Dây Fritzing & Bảng Phân Bổ Chân", "Wiring & Pinout", "07 / 14")

    # Left: Image placeholder or Diorama image
    img_path = "Smart Classroom System Diorama.png"
    if os.path.exists(img_path):
        s7.shapes.add_picture(img_path, Inches(0.8), Inches(1.8), Inches(5.8), Inches(4.8))
    else:
        add_card(s7, 0.8, 1.8, 5.8, 4.8, "SƠ ĐỒ NGUYÊN LÝ FRITZING WIRING", [
            "[Vui lòng chèn file ảnh fritzing_schematic.png vào đây]",
            "",
            "• Nguồn cấp: 5V DC micro-USB & Breadboard Power Module",
            "• Common Ground: Toàn bộ GND cảm biến và ESP8266 nối chung",
            "• Chân GPIO15 (D8): Có điện trở kéo xuống Pull-down chống lỗi boot",
            "• Chân GPIO0/2 (D3/D4): Không nối tải nặng lúc khởi động"
        ], border_color=ACCENT_CYAN)

    # Right: Pinout Table Card
    pinouts = [
        "• D0 (GPIO16): Relay Quạt làm mát phòng (Active High)",
        "• D4 (GPIO2): LED Đèn học tập tự động (Active Low)",
        "• D7 (GPIO13): Warning LED đỏ nhấp nháy khi có sự cố",
        "• D8 (GPIO15): Còi Buzzer hú báo động khẩn cấp",
        "• D1/D2 (GPIO5/4): Màn hình LCD 1602 I2C (SCL / SDA - Addr 0x27)",
        "• D3 (GPIO0): Dữ liệu cảm biến nhiệt độ & độ ẩm DHT11",
        "• D5 (GPIO14): Tín hiệu cảm biến chuyển động PIR (Hardware ISR)",
        "• D6 (GPIO12): Tín hiệu cảm biến ánh sáng LDR quang trở",
        "• A0 (ADC0): Tín hiệu điện áp Analog cảm biến khí gas MQ135"
    ]
    add_card(s7, 6.8, 1.8, 5.8, 4.8, "BẢNG MAPPING PINOUT ESP8266 NODEMCU", pinouts, border_color=ACCENT_BLUE)

    # =========================================================================
    # SLIDE 8: SYSTEM BLOCK DIAGRAM (MANDATORY TECHNICAL LAYOUT)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s8)
    add_header(s8, "Sơ Đồ Khối Kỹ Thuật Hệ Thống (Block Diagram)", "System Architecture", "08 / 14")

    # Top: External Control Servers
    add_card(s8, 2.5, 1.6, 3.8, 1.1, "WEB SERVER DASHBOARD", [
        "Port 80 (LAN IP / 192.168.4.1 AP)"
    ], border_color=ACCENT_BLUE, bg_color=RGBColor(25, 35, 55))

    add_card(s8, 7.0, 1.6, 3.8, 1.1, "GOOGLE APPS SCRIPT WEBHOOK", [
        "HTTPS POST Email Alert API (5-min Cooldown)"
    ], border_color=ACCENT_RED, bg_color=RGBColor(35, 25, 35))

    # Left: 4 Inputs
    add_card(s8, 0.8, 2.9, 3.0, 0.9, "DHT11 (D3 - GPIO0)", ["Nhiệt độ & Độ ẩm"], border_color=ACCENT_BLUE)
    add_card(s8, 0.8, 3.9, 3.0, 0.9, "MQ135 (A0 - ADC)", ["Khí Gas & Khói độc"], border_color=ACCENT_AMBER)
    add_card(s8, 0.8, 4.9, 3.0, 0.9, "PIR HC-SR501 (D5)", ["Ngắt chuyển động ISR"], border_color=ACCENT_GREEN)
    add_card(s8, 0.8, 5.9, 3.0, 0.9, "LDR SENSOR (D6)", ["Cảm biến ánh sáng"], border_color=ACCENT_CYAN)

    # Center: ESP8266 NodeMCU Controller
    add_card(s8, 4.2, 2.9, 4.9, 3.9, "ESP8266 NODEMCU CONTROLLER", [
        "CPU: Tensilica Xtensa 32-bit @ 80/160 MHz",
        "-------------------------------------------",
        "• Non-blocking Task Scheduler (millis loop)",
        "• Hardware Interrupt Handler (PIR ISR)",
        "• Edge Logic: Thresholds & Hysteresis",
        "• Safety Override Engine (Cưỡng bức quạt khi gas)",
        "• Dual WiFi Stack: STA Mode + SoftAP Fallback",
        "• I2C Master Protocol: LCD 1602 Driver (0x27)"
    ], border_color=ACCENT_CYAN, bg_color=RGBColor(15, 30, 48), title_color=ACCENT_CYAN)

    # Right: 5 Outputs
    add_card(s8, 9.5, 2.8, 3.0, 0.75, "RELAY QUẠT (D0)", ["Làm mát / Thông gió"], border_color=ACCENT_BLUE)
    add_card(s8, 9.5, 3.65, 3.0, 0.75, "LED ĐÈN HỌC (D4)", ["Chiếu sáng tự động"], border_color=ACCENT_GREEN)
    add_card(s8, 9.5, 4.5, 3.0, 0.75, "WARNING LED (D7)", ["Chớp đỏ cảnh báo"], border_color=ACCENT_RED)
    add_card(s8, 9.5, 5.35, 3.0, 0.75, "CÒI BUZZER (D8)", ["Hú còi khẩn cấp gas"], border_color=ACCENT_AMBER)
    add_card(s8, 9.5, 6.2, 3.0, 0.75, "LCD 1602 I2C (D1/D2)", ["Hiển thị trực tiếp"], border_color=ACCENT_CYAN)

    # =========================================================================
    # SLIDE 9: SYSTEM FLOWCHART
    # =========================================================================
    s9 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s9)
    add_header(s9, "Lưu Đồ Thuật Toán Vận Hành (Flowchart)", "Execution Logic", "09 / 14")

    add_card(s9, 0.8, 1.8, 3.8, 4.8, "1. GIAI ĐOẠN KHỞI TẠO (SETUP)", [
        "1. Khởi động nguồn vi điều khiển ESP8266.",
        "2. Cấu hình chân GPIO, gắn ngắt PIR ISR trên chân D5.",
        "3. Khởi tạo màn hình LCD 1602 I2C (0x27).",
        "4. Kết nối WiFi STA (Trường học):",
        "   - Đếm thời gian Timeout 15 giây.",
        "   - Nếu thành công -> Nhận IP Router & Khởi động Web Server Port 80.",
        "   - Nếu thất bại/rớt mạng -> Tự động kích hoạt Fallback AP 'SmartClassroom_WiFi' (192.168.4.1).",
        "5. Chuyển sang Vòng lặp chính loop()."
    ], border_color=ACCENT_BLUE)

    add_card(s9, 4.8, 1.8, 3.8, 4.8, "2. VÒNG LẶP CHÍNH (LOOP)", [
        "1. Xử lý yêu cầu Web: server.handleClient().",
        "2. Kiểm tra cờ ngắt PIR & LDR:",
        "   - Có người + Tối -> Bật đèn học D4.",
        "   - Hết người -> Đếm trễ 15s rồi tắt đèn.",
        "3. Đọc cảm biến Non-blocking (mỗi 2s):",
        "   - Đọc DHT11 (Nhiệt độ, Độ ẩm).",
        "   - Đọc MQ135 (Nồng độ gas Analog).",
        "4. So sánh ngưỡng nhiệt độ:",
        "   - T >= 30.0°C -> Bật Quạt D0.",
        "   - T <= 29.5°C -> Tắt Quạt D0."
    ], border_color=ACCENT_GREEN)

    add_card(s9, 8.8, 1.8, 3.8, 4.8, "3. CẢNH BÁO LEO THANG & CLOUD", [
        "1. So sánh ngưỡng Gas/Khói:",
        "   - Gas >= 500 -> Hú còi D8 + Chớp LED D7.",
        "   - Gas <= 450 -> Tắt còi D8.",
        "2. Kiểm tra điều kiện gửi Email:",
        "   - Có sự cố Leo thang (Quá nhiệt hoặc Gas).",
        "   - VÀ thời gian Cooldown > 5 phút (300.000 ms).",
        "3. Gửi HTTPS POST Webhook Google Script:",
        "   - Bắn email HTML cảnh báo khẩn cấp.",
        "   - Cập nhật thời điểm lastEmailSendTime.",
        "4. Cập nhật luân phiên LCD 1602 mỗi 2 giây."
    ], border_color=ACCENT_RED)

    # =========================================================================
    # SLIDE 10: PROJECT PHOTOS GALLERY
    # =========================================================================
    s10 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s10)
    add_header(s10, "Hình Ảnh Mô Hình Phần Cứng Thực Tế", "Physical Prototype", "10 / 14")

    if os.path.exists(img_path):
        s10.shapes.add_picture(img_path, Inches(0.8), Inches(1.8), Inches(5.8), Inches(4.8))
    else:
        add_card(s10, 0.8, 1.8, 5.8, 4.8, "MÔ HÌNH DIORAMA PHÒNG HỌC", [
            "[Ảnh mô hình phòng học thu nhỏ]",
            "Tích hợp quạt trần, đèn học LED và cụm cảm biến thẩm mỹ."
        ])

    add_card(s10, 6.8, 1.8, 5.8, 1.5, "1. BO MẠCH ĐIỀU KHIỂN TRUNG TÂM", [
        "ESP8266 NodeMCU V3 kết nối cùng module Relay cách ly quang học, còi Buzzer và màn hình LCD 1602 qua mạch chuyển đổi I2C."
    ], border_color=ACCENT_BLUE)

    add_card(s10, 6.8, 3.45, 5.8, 1.5, "2. GIAO DIỆN WEB SERVER DASHBOARD (PORT 80)", [
        "Trang điều khiển giao diện Dark Mode hiển thị trực tiếp nhiệt độ, độ ẩm, nồng độ gas và các nút bật/tắt thiết bị thủ công."
    ], border_color=ACCENT_CYAN)

    add_card(s10, 6.8, 5.1, 5.8, 1.5, "3. HỆ THỐNG EMAIL HTML CẢNH BÁO TỰ ĐỘNG", [
        "Email HTML gửi về điện thoại người quản lý kèm mức độ nguy hiểm, giá trị cảm biến tại thời điểm sự cố và hướng dẫn xử lý."
    ], border_color=ACCENT_RED)

    # =========================================================================
    # SLIDE 11: DEMO & 4 TEST CASES
    # =========================================================================
    s11 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s11)
    add_header(s11, "Trình Diễn Demo & 4 Kịch Bản Kiểm Thử", "Verification & Test Cases", "11 / 14")

    # Left: QR Links
    add_card(s11, 0.8, 1.8, 4.5, 4.8, "TRUY CẬP VIDEO DEMO & SOURCE CODE", [
        "Quét mã hoặc nhấp link truy cập trực tiếp:",
        "",
        "1. VIDEO DEMO THỰC TẾ (YOUTUBE):",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "",
        "2. KHO MÃ NGUỒN GITHUB REPOSITORY:",
        "https://github.com/smartclassroom-iot/esp8266-core",
        "",
        "• Kiểm thử chịu tải ngắt phần cứng PIR liên tục.",
        "• Kiểm thử ngắt kết nối WiFi và tự phục hồi sau 15s."
    ], border_color=ACCENT_CYAN)

    # Right: 4 Test Cases
    add_card(s11, 5.6, 1.8, 7.0, 1.15, "TEST CASE 1: CẢNH BÁO QUÁ NHIỆT (>= 30°C)", [
        "• Thao tác: Dùng máy sấy gia nhiệt vào DHT11. Phản ứng: Quạt tự bật, LED đỏ chớp, Web báo đỏ, Gửi Email.",
        "• ĐẶC BIỆT: Tuyệt đối không hú còi để tránh quấy rầy lớp học kế bên (Noise-free alert) -> PASSED"
    ], border_color=ACCENT_BLUE)

    add_card(s11, 5.6, 3.05, 7.0, 1.15, "TEST CASE 2: BÁO ĐỘNG RÒ RỈ GAS KHẨN CẤP (>= 500)", [
        "• Thao tác: Xả gas bật lửa vào MQ135. Phản ứng: Quạt bật hết công suất, gửi Email khẩn cấp.",
        "• ĐẶC BIỆT: CÒI HÚ ẦM Ĩ LIÊN TỤC vì đây là sự cố đe dọa sinh mạng con người -> PASSED"
    ], border_color=ACCENT_RED)

    add_card(s11, 5.6, 4.3, 7.0, 1.15, "TEST CASE 3: TỰ ĐỘNG BẬT ĐÈN & TRỄ GIỮ SÁNG (15s)", [
        "• Thao tác: Che tối LDR và vẫy tay qua PIR -> Đèn bật ngay.",
        "• Khi hết người: Đèn sáng thêm 15 giây rồi mới tắt, chống tắt đột ngột khi ngồi ghi bài -> PASSED"
    ], border_color=ACCENT_GREEN)

    add_card(s11, 5.6, 5.55, 7.0, 1.15, "TEST CASE 4: GHI ĐÈ AN TOÀN (SAFETY OVERRIDE)", [
        "• Thao tác: Bấm TẮT quạt trên Web, sau đó xả gas vào MQ135.",
        "• Phản ứng: Edge Logic tự động cưỡng bức BẬT quạt (Safety overrules manual) -> PASSED"
    ], border_color=ACCENT_AMBER)

    # =========================================================================
    # SLIDE 12: KEY ACHIEVEMENTS & CONCLUSION
    # =========================================================================
    s12 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s12)
    add_header(s12, "Tổng Kết Các Kết Quả Kỹ Thuật Đạt Được", "Achievements & Conclusion", "12 / 14")

    achievements = [
        ("KIẾN TRÚC NON-BLOCKING HOÀN TOÀN", ACCENT_BLUE, [
            "• Loại bỏ hoàn toàn 100% các hàm trễ delay() gây đóng băng CPU.",
            "• Quản lý lịch trình đa tác vụ bằng millis() độc lập.",
            "• Web Server và ngắt phản hồi tức thời < 50ms ngay cả khi đang truyền nhận dữ liệu."
        ]),
        ("PHẢN XẠ TỨC THỜI VỚI HARDWARE ISR", ACCENT_GREEN, [
            "• Cảm biến chuyển động PIR hoạt động theo cơ chế ngắt phần cứng trên chân D5.",
            "• Ghi nhận sự hiện diện của học sinh ngay lập tức (< 1ms).",
            "• Không bị bỏ sót sự kiện chuyển động khi vi điều khiển đang bận xử lý HTTP."
        ]),
        ("CẢNH BÁO THÔNG MINH & CHỐNG SPAM MAIL", ACCENT_RED, [
            "• Phân định rạch ròi 2 cấp độ cảnh báo (Tiếng ồn thấp vs Báo động sinh mạng).",
            "• Cơ chế cờ nhớ và bộ đếm Cooldown 5 phút (300.000 ms) triệt tiêu hoàn toàn nguy cơ tràn hộp thư."
        ]),
        ("CƠ CHẾ DỰ PHÒNG FAIL-SAFE AP FALLBACK", ACCENT_CYAN, [
            "• Giám sát trạng thái kết nối mạng liên tục với bộ đếm 15 giây.",
            "• Tự động mở Hotspot nội bộ 192.168.4.1 khi rớt mạng trường học.",
            "• Đảm bảo quyền giám sát và điều khiển thiết bị không bao giờ bị gián đoạn."
        ])
    ]

    for i, (title, col, items) in enumerate(achievements):
        col_idx = i % 2
        row_idx = i // 2
        add_card(s12, 0.8 + col_idx * 5.95, 1.8 + row_idx * 2.5, 5.8, 2.3, title, items, border_color=col, title_color=col)

    # =========================================================================
    # SLIDE 13: FUTURE DEVELOPMENT
    # =========================================================================
    s13 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s13)
    add_header(s13, "Định Hướng Nghiên Cứu & Phát Triển Tương Lai", "Future Roadmap", "13 / 14")

    upgrades = [
        ("NÂNG CẤP 01: GIAO THỨC MQTT & CLOUD IOT", ACCENT_BLUE, [
            "• Tích hợp giao thức MQTT siêu nhẹ thay thế HTTP Webhook.",
            "• Kết nối với Broker đám mây (AWS IoT Core, HiveMQ, ThingsBoard).",
            "• Mở rộng kiến trúc cho phép quản trị đồng thời hàng trăm phòng học xuyên Internet."
        ]),
        ("NÂNG CẤP 02: CAMERA AI EDGE (ESP32-CAM)", ACCENT_CYAN, [
            "• Bổ sung module Camera AI nhận diện khuôn mặt điểm danh sinh viên tự động.",
            "• Thuật toán đếm số lượng người thực tế trong phòng tại biên (TinyML).",
            "• Tự động điều chỉnh cấp tốc độ quạt / điều hòa tương ứng với mật độ người."
        ]),
        ("NÂNG CẤP 03: GIÁM SÁT ĐIỆN NĂNG PZEM-004T", ACCENT_GREEN, [
            "• Lắp đặt biến dòng PZEM-004T đo trực tiếp Điện áp (V), Dòng điện (A), Công suất (W) và Điện năng (kWh).",
            "• Tự động tính tiền điện theo thời gian thực và cảnh báo rò điện, quá tải aptomat phòng học."
        ])
    ]

    for i, (title, col, items) in enumerate(upgrades):
        add_card(s13, 0.8 + i * 3.95, 1.8, 3.8, 4.8, title, items, border_color=col, title_color=col)

    # =========================================================================
    # SLIDE 14: THANK YOU & Q&A SESSION
    # =========================================================================
    s14 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s14)

    thx_box = s14.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(1.5))
    tf14 = thx_box.text_frame
    p = tf14.paragraphs[0]
    p.text = "XIN CHÂN THÀNH CẢM ƠN!"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.alignment = PP_ALIGN.CENTER

    p2 = tf14.add_paragraph()
    p2.text = "Hội đồng Đánh giá & Quý Thầy Cô đã dành thời gian lắng nghe phần trình bày của nhóm"
    p2.font.size = Pt(17)
    p2.font.color.rgb = ACCENT_CYAN
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(10)

    add_card(s14, 2.5, 3.4, 8.33, 2.8, "PHIÊN HỎI & ĐÁP (Q&A SESSION)", [
        "Kính mời Quý Thầy Cô trong Hội đồng phản biện đặt câu hỏi",
        "và đóng góp ý kiến để đề án được hoàn thiện hơn!",
        "",
        "• Mã nguồn Firmware ESP8266: Non-blocking millis() & Hardware ISR",
        "• Máy chủ đám mây: Google Apps Script Webhook & Email Escalation",
        "• Tài liệu & Sơ đồ đấu nối: Đầy đủ sơ đồ Fritzing CAD & Báo cáo kỹ thuật IEEE"
    ], border_color=ACCENT_CYAN, title_color=ACCENT_CYAN)

    # Save presentation
    output_path = "Smart_Classroom_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_presentation()

